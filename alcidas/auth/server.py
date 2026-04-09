"""ALCIDAS license auth server.

Exposes two endpoints:
  POST /v1/license/validate   — called by install.sh and the gateway on boot
  POST /v1/webhooks/stripe    — called by Stripe on subscription events

Run with:
  pip install fastapi uvicorn
  python -m alcidas.auth.server

Environment variables:
  STRIPE_WEBHOOK_SECRET   — from Stripe Dashboard → Webhooks → Signing secret
  STRIPE_SECRET_KEY       — sk_live_... or sk_test_...
  ALCIDAS_AUTH_PORT       — default 8741
"""
import hashlib
import hmac
import logging
import os
import time
from typing import Any

# TODO: pip install fastapi uvicorn stripe (not in hermes deps — auth server
#       runs as a separate process on the Hetzner VPS alongside the gateway)
try:
    from fastapi import FastAPI, HTTPException, Request, Header
    from fastapi.responses import JSONResponse
    import uvicorn
except ImportError as e:
    raise ImportError(
        "Auth server requires: pip install fastapi uvicorn\n"
        "These are not part of the gateway venv — run in a separate env."
    ) from e

from alcidas.auth.models import LicenseRecord, ValidationResult
from alcidas.auth.license_store import LicenseStore

logger = logging.getLogger(__name__)
app = FastAPI(title="ALCIDAS Auth", version="0.1.0")
_store = LicenseStore()


# ── License validation ────────────────────────────────────────────────────────

@app.post("/v1/license/validate")
async def validate_license(request: Request) -> JSONResponse:
    """Called by install.sh and the gateway on startup.

    Body: {"license_key": "ALCD-XXXX-...", "installer_version": "latest"}
    Returns 200 + ValidationResult on success, 402 on inactive/unknown key.
    """
    body = await request.json()
    key: str = body.get("license_key", "").strip()

    if not key:
        raise HTTPException(status_code=400, detail="license_key required")

    record = _store.get(key)
    if record is None:
        return JSONResponse(
            status_code=402,
            content=ValidationResult(valid=False, error="Unknown license key").to_dict()
        )

    if not record.active:
        return JSONResponse(
            status_code=402,
            content=ValidationResult(
                valid=False,
                error="Subscription inactive. Manage at https://alcidas.com/billing"
            ).to_dict()
        )

    _store.touch_validated(key)
    return JSONResponse(
        content=ValidationResult(
            valid=True,
            customer_id=record.stripe_customer_id,
            plan=record.plan,
            display_name=record.display_name,
        ).to_dict()
    )


# ── Stripe webhook ────────────────────────────────────────────────────────────

def _verify_stripe_signature(payload: bytes, sig_header: str, secret: str) -> None:
    """Raise HTTPException if the Stripe webhook signature is invalid."""
    try:
        pairs = {k: v for k, v in (p.split("=", 1) for p in sig_header.split(","))}
        timestamp = int(pairs["t"])
        signatures = [v for k, v in pairs.items() if k == "v1"]
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid Stripe-Signature header")

    # Reject replays older than 5 minutes
    if abs(time.time() - timestamp) > 300:
        raise HTTPException(status_code=400, detail="Webhook timestamp too old")

    signed_payload = f"{timestamp}.".encode() + payload
    expected = hmac.new(secret.encode(), signed_payload, hashlib.sha256).hexdigest()
    if not any(hmac.compare_digest(expected, sig) for sig in signatures):
        raise HTTPException(status_code=400, detail="Stripe signature mismatch")


@app.post("/v1/webhooks/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="Stripe-Signature"),
) -> JSONResponse:
    """Stripe sends events here on subscription lifecycle changes.

    Handled events:
      customer.subscription.created   → issue license key, TODO: email to customer
      customer.subscription.deleted   → deactivate license key
      customer.subscription.updated   → handle plan change (future)
      invoice.payment_failed          → warn but keep active (Stripe retries)
    """
    webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
    payload = await request.body()

    if webhook_secret:
        _verify_stripe_signature(payload, stripe_signature or "", webhook_secret)
    else:
        logger.warning("STRIPE_WEBHOOK_SECRET not set — skipping signature verification")

    event: dict[str, Any] = await request.json()
    event_type: str = event.get("type", "")
    data = event.get("data", {}).get("object", {})

    logger.info("Stripe event: %s", event_type)

    if event_type == "customer.subscription.created":
        _handle_subscription_created(data)

    elif event_type == "customer.subscription.deleted":
        customer_id = data.get("customer")
        if customer_id:
            _store.set_active(customer_id, False)
            logger.info("Deactivated license for customer %s", customer_id)

    elif event_type == "invoice.payment_failed":
        # Stripe retries on its own schedule — log only, don't deactivate yet.
        customer_id = data.get("customer")
        logger.warning("Payment failed for customer %s — watching for retry", customer_id)

    # All other events acknowledged but ignored
    return JSONResponse(content={"received": True})


def _handle_subscription_created(subscription: dict[str, Any]) -> None:
    """Issue a license key for a new paying customer."""
    customer_id = subscription.get("customer")
    subscription_id = subscription.get("id")
    plan_id = (
        subscription.get("items", {})
        .get("data", [{}])[0]
        .get("price", {})
        .get("nickname") or "starter"
    )

    if not customer_id or not subscription_id:
        logger.error("subscription.created missing customer or id: %s", subscription)
        return

    existing = _store.get_by_stripe_customer(customer_id)
    if existing:
        # Re-activation after lapse — restore existing key
        _store.set_active(customer_id, True)
        logger.info("Reactivated existing license for customer %s", customer_id)
        return

    key = LicenseRecord.generate_key()
    record = LicenseRecord(
        license_key=key,
        stripe_customer_id=customer_id,
        stripe_subscription_id=subscription_id,
        plan=plan_id,
        display_name=customer_id,  # TODO: fetch from Stripe Customer object
    )
    _store.create(record)
    logger.info("Issued license %s for customer %s (plan: %s)", key, customer_id, plan_id)

    # TODO: email license key to customer via Stripe Customer email
    # customer = stripe.Customer.retrieve(customer_id)
    # send_license_email(to=customer.email, license_key=key)


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    port = int(os.environ.get("ALCIDAS_AUTH_PORT", 8741))
    uvicorn.run("alcidas.auth.server:app", host="0.0.0.0", port=port, reload=False)


if __name__ == "__main__":
    main()
