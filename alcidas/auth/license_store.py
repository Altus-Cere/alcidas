"""SQLite-backed license key store.

Thin persistence layer. Stripe is the source of truth for subscription status —
this store caches the mapping of license_key → stripe_customer_id and is
refreshed on every Stripe webhook event.
"""
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Optional

from alcidas.auth.models import LicenseRecord


DEFAULT_DB_PATH = Path.home() / ".alcidas" / "auth.db"


class LicenseStore:
    def __init__(self, db_path: Path = DEFAULT_DB_PATH):
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_db(self) -> None:
        with self._conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS licenses (
                    license_key          TEXT PRIMARY KEY,
                    stripe_customer_id   TEXT NOT NULL,
                    stripe_subscription_id TEXT NOT NULL,
                    plan                 TEXT NOT NULL,
                    display_name         TEXT NOT NULL,
                    active               INTEGER NOT NULL DEFAULT 1,
                    created_at           TEXT NOT NULL,
                    last_validated_at    TEXT
                )
            """)
            conn.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS idx_stripe_customer "
                "ON licenses (stripe_customer_id)"
            )

    def create(self, record: LicenseRecord) -> None:
        with self._conn() as conn:
            conn.execute("""
                INSERT INTO licenses
                  (license_key, stripe_customer_id, stripe_subscription_id,
                   plan, display_name, active, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                record.license_key,
                record.stripe_customer_id,
                record.stripe_subscription_id,
                record.plan,
                record.display_name,
                int(record.active),
                record.created_at.isoformat(),
            ))

    def get(self, license_key: str) -> Optional[LicenseRecord]:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM licenses WHERE license_key = ?", (license_key,)
            ).fetchone()
        if row is None:
            return None
        return self._row_to_record(row)

    def get_by_stripe_customer(self, stripe_customer_id: str) -> Optional[LicenseRecord]:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM licenses WHERE stripe_customer_id = ?",
                (stripe_customer_id,)
            ).fetchone()
        return self._row_to_record(row) if row else None

    def set_active(self, stripe_customer_id: str, active: bool) -> None:
        with self._conn() as conn:
            conn.execute(
                "UPDATE licenses SET active = ? WHERE stripe_customer_id = ?",
                (int(active), stripe_customer_id)
            )

    def touch_validated(self, license_key: str) -> None:
        with self._conn() as conn:
            conn.execute(
                "UPDATE licenses SET last_validated_at = ? WHERE license_key = ?",
                (datetime.utcnow().isoformat(), license_key)
            )

    @staticmethod
    def _row_to_record(row: sqlite3.Row) -> LicenseRecord:
        return LicenseRecord(
            license_key=row["license_key"],
            stripe_customer_id=row["stripe_customer_id"],
            stripe_subscription_id=row["stripe_subscription_id"],
            plan=row["plan"],
            display_name=row["display_name"],
            active=bool(row["active"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            last_validated_at=(
                datetime.fromisoformat(row["last_validated_at"])
                if row["last_validated_at"] else None
            ),
        )
