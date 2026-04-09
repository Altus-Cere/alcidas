"""Data models for the ALCIDAS auth service."""
import secrets
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class LicenseRecord:
    """One license key bound to one Stripe customer."""
    license_key: str
    stripe_customer_id: str
    stripe_subscription_id: str
    plan: str                          # e.g. "starter", "growth"
    display_name: str                  # Business name for logs
    active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_validated_at: Optional[datetime] = None

    @staticmethod
    def generate_key() -> str:
        """Generate a URL-safe license key: ALCD-XXXX-XXXX-XXXX-XXXX."""
        parts = [secrets.token_hex(3).upper() for _ in range(4)]
        return "ALCD-" + "-".join(parts)


@dataclass
class ValidationResult:
    valid: bool
    customer_id: Optional[str] = None
    plan: Optional[str] = None
    display_name: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> dict:
        d: dict = {"valid": self.valid}
        if self.valid:
            d["customer_id"] = self.customer_id
            d["plan"] = self.plan
            d["display_name"] = self.display_name
        else:
            d["error"] = self.error
        return d
