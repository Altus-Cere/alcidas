"""License validation client — called by the gateway on startup.

Phones home to the ALCIDAS auth server to verify the license key is still
active before the Telegram adapter connects.

Skipped when ALCIDAS_LICENSE_KEY is unset (dev/test mode).
"""
import logging
import os

import httpx

logger = logging.getLogger(__name__)

_AUTH_URL = os.environ.get(
    "ALCIDAS_AUTH_URL",
    "https://auth.alcidas.com/v1/license/validate",
)
_TIMEOUT = 10  # seconds


def validate_on_boot() -> None:
    """Check license key against auth server. Raises on failure.

    No-ops when ALCIDAS_LICENSE_KEY is not set (dev mode).
    Raises RuntimeError if the key is invalid or the subscription is inactive.
    """
    key = os.environ.get("ALCIDAS_LICENSE_KEY", "").strip()
    if not key:
        logger.warning(
            "ALCIDAS_LICENSE_KEY not set — skipping license check (dev/test mode)."
        )
        return

    logger.info("Validating license key with auth server...")
    try:
        resp = httpx.post(
            _AUTH_URL,
            json={"license_key": key},
            timeout=_TIMEOUT,
        )
    except httpx.RequestError as exc:
        # Network failure — fail open so a transient outage doesn't kill the bot
        logger.warning(
            "License server unreachable (%s) — continuing with cached status.", exc
        )
        return

    if resp.status_code == 200:
        data = resp.json()
        if data.get("valid"):
            logger.info(
                "License valid — customer: %s, plan: %s",
                data.get("customer_id"),
                data.get("plan"),
            )
            return

    if resp.status_code in (402, 403):
        raise RuntimeError(
            f"License key invalid or subscription inactive. "
            f"Manage at https://alcidas.com/billing\n"
            f"Server response: {resp.text}"
        )

    # Any other error (500, etc.) — fail open, log loudly
    logger.error(
        "Unexpected response from license server (HTTP %s): %s",
        resp.status_code,
        resp.text,
    )
