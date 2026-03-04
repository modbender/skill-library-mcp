#!/usr/bin/env python3
"""
Guardian Pro — Stripe Billing Integration
==========================================
Manages $9/mo Pro tier subscriptions: creation, cancellation, status checks,
webhook handling, and a local SQLite cache to gate premium feature access.

Design principles:
  - No third-party SDK required at runtime (stdlib urllib used for Stripe API)
  - stripe package is used if available, but falls back gracefully
  - All subscription state is mirrored locally for low-latency gating
  - Webhook events keep local cache in sync with Stripe

Usage::

    from billing.stripe_integration import SubscriptionManager, SubscriptionGate

    mgr = SubscriptionManager(api_key="sk_live_...")
    sub = mgr.create_subscription(
        customer_email="user@example.com",
        payment_method_id="pm_...",
    )

    gate = SubscriptionGate(db_path="billing.db", api_key="sk_live_...")
    if gate.is_pro(user_id="user@example.com"):
        # serve premium signatures
        ...

Environment variables (override constructor args):
  STRIPE_SECRET_KEY   — Stripe secret key (sk_live_... or sk_test_...)
  STRIPE_PRICE_ID     — Stripe price ID for the $9/mo plan
  STRIPE_WEBHOOK_SECRET — for webhook signature verification
  BILLING_DB_PATH     — path for local SQLite subscription cache
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import sqlite3
import time
import urllib.error
import urllib.parse
import urllib.request
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Generator, List, Optional, Tuple

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

GUARDIAN_PRO_PRICE_USD = 9_00  # $9.00 in cents
STRIPE_API_BASE = "https://api.stripe.com/v1"
PRO_TIER_FEATURES = [
    "premium_signatures",
    "extended_analytics",
    "priority_support",
    "api_rate_limit_5x",
    "export_csv",
    "custom_alert_rules",
]

# Stripe subscription statuses that count as "active" for feature gating
ACTIVE_STATUSES = {"active", "trialing"}
# Statuses that indicate the user had pro but it lapsed — grace period applies
GRACE_STATUSES = {"past_due"}
# Grace period in seconds (3 days) for past_due before access is cut
GRACE_PERIOD_SECONDS = 3 * 24 * 3600


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class BillingError(Exception):
    """Base billing error."""


class StripeAPIError(BillingError):
    """Raised on unexpected Stripe API errors."""

    def __init__(self, message: str, status_code: int = 0, stripe_code: str = "") -> None:
        super().__init__(message)
        self.status_code = status_code
        self.stripe_code = stripe_code


class SubscriptionNotFoundError(BillingError):
    """Raised when the requested subscription cannot be found."""


class WebhookVerificationError(BillingError):
    """Raised when a Stripe webhook signature cannot be verified."""


class FeatureGatedError(BillingError):
    """Raised when a Pro-gated feature is accessed without an active subscription."""

    def __init__(self, user_id: str, feature: str) -> None:
        super().__init__(f"Pro feature '{feature}' requires an active Guardian Pro subscription.")
        self.user_id = user_id
        self.feature = feature


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class SubscriptionRecord:
    """Local cache record for a Stripe subscription."""

    user_id: str
    stripe_customer_id: str
    stripe_subscription_id: str
    status: str  # active | trialing | canceled | past_due | incomplete | ...
    plan_id: str
    current_period_end: int  # Unix timestamp
    cancel_at_period_end: bool = False
    created_at: int = field(default_factory=lambda: int(time.time()))
    updated_at: int = field(default_factory=lambda: int(time.time()))
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_active(self) -> bool:
        """True if subscription grants Pro access (including grace period)."""
        if self.status in ACTIVE_STATUSES:
            return True
        if self.status in GRACE_STATUSES:
            grace_expires = self.current_period_end + GRACE_PERIOD_SECONDS
            return int(time.time()) < grace_expires
        return False

    @property
    def expires_at_iso(self) -> str:
        return datetime.fromtimestamp(self.current_period_end, tz=timezone.utc).isoformat()


@dataclass
class CheckoutSession:
    """Result of initiating a Stripe checkout session."""

    session_id: str
    checkout_url: str
    customer_email: str


# ---------------------------------------------------------------------------
# Low-level Stripe API client (stdlib only)
# ---------------------------------------------------------------------------


class StripeClient:
    """
    Minimal Stripe REST client using stdlib urllib.

    If the ``stripe`` package is installed, its SDK is preferred
    (better error handling, retries). Falls back to raw HTTP otherwise.
    """

    def __init__(self, api_key: str) -> None:
        if not api_key or not api_key.startswith("sk_"):
            raise BillingError(
                "Invalid Stripe API key. Must start with 'sk_test_' or 'sk_live_'."
            )
        self._api_key = api_key
        self._use_sdk = self._check_sdk()

    def _check_sdk(self) -> bool:
        try:
            import stripe  # noqa: F401
            return True
        except ImportError:
            return False

    # ---- SDK path --------------------------------------------------------

    def _sdk_request(self, method: str, path: str, params: Dict[str, Any]) -> Dict[str, Any]:
        import stripe  # type: ignore
        stripe.api_key = self._api_key
        # Use the stripe SDK's resource methods via getattr for flexibility
        resource_map = {
            "/customers": stripe.Customer,
            "/subscriptions": stripe.Subscription,
            "/payment_methods": stripe.PaymentMethod,
            "/checkout/sessions": stripe.checkout.Session,
        }
        # Generic approach: use stripe.api_requestor
        requestor = stripe.api_requestor.APIRequestor(self._api_key)
        resp, _ = requestor.request(method.lower(), path, params)
        return dict(resp)

    # ---- Stdlib HTTP path ------------------------------------------------

    def _http_request(self, method: str, path: str, params: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{STRIPE_API_BASE}{path}"
        auth = urllib.parse.quote(self._api_key) + ":"
        auth_b64 = __import__("base64").b64encode(auth.encode()).decode()
        headers = {
            "Authorization": f"Basic {auth_b64}",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "GuardianPro/2.1.0",
            "Stripe-Version": "2023-10-16",
        }
        body: Optional[bytes] = None
        if method.upper() in ("POST", "DELETE") and params:
            body = urllib.parse.urlencode(params, doseq=True).encode()
        elif method.upper() == "GET" and params:
            url = f"{url}?{urllib.parse.urlencode(params, doseq=True)}"

        req = urllib.request.Request(url, data=body, headers=headers, method=method.upper())
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw)
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            try:
                err_body = json.loads(raw)
                err = err_body.get("error", {})
                raise StripeAPIError(
                    err.get("message", raw),
                    status_code=exc.code,
                    stripe_code=err.get("code", ""),
                ) from exc
            except (json.JSONDecodeError, KeyError):
                raise StripeAPIError(raw, status_code=exc.code) from exc
        except urllib.error.URLError as exc:
            raise StripeAPIError(f"Network error reaching Stripe: {exc.reason}") from exc

    def request(self, method: str, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a Stripe API request, preferring the SDK if available."""
        params = params or {}
        try:
            if self._use_sdk:
                return self._sdk_request(method, path, params)
            return self._http_request(method, path, params)
        except StripeAPIError:
            raise
        except Exception as exc:
            raise StripeAPIError(f"Stripe request failed: {exc}") from exc

    # ---- Convenience methods ---------------------------------------------

    def create_customer(self, email: str, name: str = "", metadata: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        return self.request("POST", "/customers", {
            "email": email,
            "name": name,
            **({"metadata": metadata} if metadata else {}),
        })

    def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        payment_method_id: Optional[str] = None,
        trial_days: int = 0,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "customer": customer_id,
            "items[0][price]": price_id,
            "expand[]": "latest_invoice.payment_intent",
        }
        if payment_method_id:
            params["default_payment_method"] = payment_method_id
        if trial_days > 0:
            params["trial_period_days"] = trial_days
        return self.request("POST", "/subscriptions", params)

    def cancel_subscription(self, subscription_id: str, at_period_end: bool = True) -> Dict[str, Any]:
        params: Dict[str, Any] = {"cancel_at_period_end": "true" if at_period_end else "false"}
        if not at_period_end:
            return self.request("DELETE", f"/subscriptions/{subscription_id}", {})
        return self.request("POST", f"/subscriptions/{subscription_id}", params)

    def get_subscription(self, subscription_id: str) -> Dict[str, Any]:
        return self.request("GET", f"/subscriptions/{subscription_id}", {})

    def list_subscriptions(self, customer_id: str, status: str = "all") -> List[Dict[str, Any]]:
        resp = self.request("GET", "/subscriptions", {
            "customer": customer_id,
            "status": status,
            "limit": "100",
        })
        return resp.get("data", [])

    def attach_payment_method(self, payment_method_id: str, customer_id: str) -> Dict[str, Any]:
        return self.request("POST", f"/payment_methods/{payment_method_id}/attach", {
            "customer": customer_id,
        })

    def create_checkout_session(
        self,
        customer_email: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
        metadata: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "mode": "subscription",
            "customer_email": customer_email,
            "line_items[0][price]": price_id,
            "line_items[0][quantity]": "1",
            "success_url": success_url,
            "cancel_url": cancel_url,
        }
        if metadata:
            for k, v in metadata.items():
                params[f"metadata[{k}]"] = v
        return self.request("POST", "/checkout/sessions", params)


# ---------------------------------------------------------------------------
# Local subscription database (SQLite cache)
# ---------------------------------------------------------------------------


class SubscriptionDB:
    """SQLite-backed local cache for Stripe subscription state."""

    SCHEMA = """
    CREATE TABLE IF NOT EXISTS subscriptions (
        id                    INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id               TEXT NOT NULL,
        stripe_customer_id    TEXT NOT NULL,
        stripe_subscription_id TEXT NOT NULL UNIQUE,
        status                TEXT NOT NULL DEFAULT 'inactive',
        plan_id               TEXT NOT NULL DEFAULT '',
        current_period_end    INTEGER NOT NULL DEFAULT 0,
        cancel_at_period_end  INTEGER NOT NULL DEFAULT 0,
        created_at            INTEGER NOT NULL,
        updated_at            INTEGER NOT NULL,
        metadata_json         TEXT NOT NULL DEFAULT '{}'
    );

    CREATE UNIQUE INDEX IF NOT EXISTS idx_subscriptions_user_id
        ON subscriptions (user_id);

    CREATE INDEX IF NOT EXISTS idx_subscriptions_status
        ON subscriptions (status);

    CREATE TABLE IF NOT EXISTS webhook_events (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id    TEXT NOT NULL UNIQUE,
        event_type  TEXT NOT NULL,
        processed_at INTEGER NOT NULL,
        payload_json TEXT NOT NULL DEFAULT '{}'
    );

    CREATE TABLE IF NOT EXISTS billing_audit (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id     TEXT NOT NULL,
        action      TEXT NOT NULL,
        detail_json TEXT NOT NULL DEFAULT '{}',
        created_at  INTEGER NOT NULL
    );
    """

    def __init__(self, db_path: str = ":memory:") -> None:
        self._path = db_path
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._migrate()

    def _migrate(self) -> None:
        for stmt in self.SCHEMA.strip().split(";"):
            stmt = stmt.strip()
            if stmt:
                self._conn.execute(stmt)
        self._conn.commit()

    @contextmanager
    def _tx(self) -> Generator[sqlite3.Connection, None, None]:
        try:
            yield self._conn
            self._conn.commit()
        except Exception:
            self._conn.rollback()
            raise

    def upsert_subscription(self, record: SubscriptionRecord) -> None:
        with self._tx() as conn:
            conn.execute(
                """
                INSERT INTO subscriptions
                    (user_id, stripe_customer_id, stripe_subscription_id,
                     status, plan_id, current_period_end, cancel_at_period_end,
                     created_at, updated_at, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(stripe_subscription_id) DO UPDATE SET
                    user_id=excluded.user_id,
                    stripe_customer_id=excluded.stripe_customer_id,
                    status=excluded.status,
                    plan_id=excluded.plan_id,
                    current_period_end=excluded.current_period_end,
                    cancel_at_period_end=excluded.cancel_at_period_end,
                    updated_at=excluded.updated_at,
                    metadata_json=excluded.metadata_json
                """,
                (
                    record.user_id,
                    record.stripe_customer_id,
                    record.stripe_subscription_id,
                    record.status,
                    record.plan_id,
                    record.current_period_end,
                    int(record.cancel_at_period_end),
                    record.created_at,
                    record.updated_at,
                    json.dumps(record.metadata),
                ),
            )

    def get_by_user_id(self, user_id: str) -> Optional[SubscriptionRecord]:
        row = self._conn.execute(
            "SELECT * FROM subscriptions WHERE user_id = ? ORDER BY updated_at DESC LIMIT 1",
            (user_id,),
        ).fetchone()
        return self._row_to_record(row) if row else None

    def get_by_subscription_id(self, sub_id: str) -> Optional[SubscriptionRecord]:
        row = self._conn.execute(
            "SELECT * FROM subscriptions WHERE stripe_subscription_id = ?",
            (sub_id,),
        ).fetchone()
        return self._row_to_record(row) if row else None

    def get_by_customer_id(self, customer_id: str) -> Optional[SubscriptionRecord]:
        row = self._conn.execute(
            "SELECT * FROM subscriptions WHERE stripe_customer_id = ? ORDER BY updated_at DESC LIMIT 1",
            (customer_id,),
        ).fetchone()
        return self._row_to_record(row) if row else None

    def update_status(self, sub_id: str, status: str, period_end: Optional[int] = None) -> None:
        now = int(time.time())
        if period_end is not None:
            self._conn.execute(
                "UPDATE subscriptions SET status=?, current_period_end=?, updated_at=? WHERE stripe_subscription_id=?",
                (status, period_end, now, sub_id),
            )
        else:
            self._conn.execute(
                "UPDATE subscriptions SET status=?, updated_at=? WHERE stripe_subscription_id=?",
                (status, now, sub_id),
            )
        self._conn.commit()

    def list_active(self) -> List[SubscriptionRecord]:
        rows = self._conn.execute(
            "SELECT * FROM subscriptions WHERE status IN ('active', 'trialing', 'past_due')"
        ).fetchall()
        return [self._row_to_record(r) for r in rows if r]

    def mark_webhook_processed(self, event_id: str, event_type: str, payload: Dict[str, Any]) -> None:
        try:
            self._conn.execute(
                "INSERT OR IGNORE INTO webhook_events (event_id, event_type, processed_at, payload_json) VALUES (?, ?, ?, ?)",
                (event_id, event_type, int(time.time()), json.dumps(payload)),
            )
            self._conn.commit()
        except sqlite3.IntegrityError:
            pass  # Already processed (duplicate delivery)

    def is_webhook_processed(self, event_id: str) -> bool:
        row = self._conn.execute(
            "SELECT 1 FROM webhook_events WHERE event_id=?", (event_id,)
        ).fetchone()
        return row is not None

    def audit_log(self, user_id: str, action: str, detail: Dict[str, Any]) -> None:
        self._conn.execute(
            "INSERT INTO billing_audit (user_id, action, detail_json, created_at) VALUES (?, ?, ?, ?)",
            (user_id, action, json.dumps(detail), int(time.time())),
        )
        self._conn.commit()

    def get_audit_log(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        rows = self._conn.execute(
            "SELECT * FROM billing_audit WHERE user_id=? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
        return [dict(r) for r in rows]

    def _row_to_record(self, row: sqlite3.Row) -> SubscriptionRecord:
        try:
            meta = json.loads(row["metadata_json"] or "{}")
        except (json.JSONDecodeError, TypeError):
            meta = {}
        return SubscriptionRecord(
            user_id=row["user_id"],
            stripe_customer_id=row["stripe_customer_id"],
            stripe_subscription_id=row["stripe_subscription_id"],
            status=row["status"],
            plan_id=row["plan_id"],
            current_period_end=int(row["current_period_end"]),
            cancel_at_period_end=bool(row["cancel_at_period_end"]),
            created_at=int(row["created_at"]),
            updated_at=int(row["updated_at"]),
            metadata=meta,
        )

    def close(self) -> None:
        self._conn.close()


# ---------------------------------------------------------------------------
# Subscription Manager (high-level business logic)
# ---------------------------------------------------------------------------


class SubscriptionManager:
    """
    High-level API for Guardian Pro subscription lifecycle.

    Typical flow::

        mgr = SubscriptionManager(api_key="sk_...", price_id="price_...",
                                   db_path="billing.db")

        # New subscriber
        record = mgr.create_subscription(
            user_id="user@example.com",
            customer_email="user@example.com",
            payment_method_id="pm_...",
        )

        # Check status
        record = mgr.get_subscription_status("user@example.com")

        # Cancel
        mgr.cancel_subscription("user@example.com")
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        price_id: Optional[str] = None,
        db_path: Optional[str] = None,
        webhook_secret: Optional[str] = None,
    ) -> None:
        self._api_key = api_key or os.environ.get("STRIPE_SECRET_KEY", "")
        self._price_id = price_id or os.environ.get("STRIPE_PRICE_ID", "")
        self._webhook_secret = webhook_secret or os.environ.get("STRIPE_WEBHOOK_SECRET", "")
        db_path = db_path or os.environ.get("BILLING_DB_PATH", ":memory:")
        self.db = SubscriptionDB(db_path)
        self._client: Optional[StripeClient] = None

    @property
    def client(self) -> StripeClient:
        if self._client is None:
            self._client = StripeClient(self._api_key)
        return self._client

    def _parse_subscription(self, user_id: str, sub: Dict[str, Any]) -> SubscriptionRecord:
        """Convert a raw Stripe subscription dict into a SubscriptionRecord."""
        customer_id = sub.get("customer", "")
        if isinstance(customer_id, dict):
            customer_id = customer_id.get("id", "")

        items = sub.get("items", {}).get("data", [])
        plan_id = ""
        if items:
            plan_id = items[0].get("price", {}).get("id", "") or items[0].get("plan", {}).get("id", "")

        return SubscriptionRecord(
            user_id=user_id,
            stripe_customer_id=customer_id,
            stripe_subscription_id=sub["id"],
            status=sub.get("status", "unknown"),
            plan_id=plan_id or self._price_id,
            current_period_end=int(sub.get("current_period_end", 0)),
            cancel_at_period_end=bool(sub.get("cancel_at_period_end", False)),
            metadata=sub.get("metadata", {}),
        )

    # ---- Public methods --------------------------------------------------

    def create_subscription(
        self,
        user_id: str,
        customer_email: str,
        payment_method_id: Optional[str] = None,
        trial_days: int = 0,
        name: str = "",
    ) -> SubscriptionRecord:
        """
        Create or reactivate a Pro subscription for a user.

        1. Creates a Stripe customer (or reuses existing from cache)
        2. Creates a subscription at $9/mo
        3. Caches result locally
        """
        if not self._price_id:
            raise BillingError(
                "STRIPE_PRICE_ID not configured. Set price_id= or STRIPE_PRICE_ID env var."
            )

        # Check if user already has a subscription
        existing = self.db.get_by_user_id(user_id)
        if existing and existing.status in ACTIVE_STATUSES:
            log.info("User %s already has active subscription %s", user_id, existing.stripe_subscription_id)
            return existing

        # Create or find Stripe customer
        customer_id: str
        if existing:
            customer_id = existing.stripe_customer_id
        else:
            customer = self.client.create_customer(
                email=customer_email,
                name=name or customer_email,
                metadata={"guardian_user_id": user_id},
            )
            customer_id = customer["id"]

        # Attach payment method if provided
        if payment_method_id:
            self.client.attach_payment_method(payment_method_id, customer_id)

        # Create subscription
        sub = self.client.create_subscription(
            customer_id=customer_id,
            price_id=self._price_id,
            payment_method_id=payment_method_id,
            trial_days=trial_days,
        )

        record = self._parse_subscription(user_id, sub)
        self.db.upsert_subscription(record)
        self.db.audit_log(user_id, "subscribe", {
            "subscription_id": record.stripe_subscription_id,
            "status": record.status,
            "trial_days": trial_days,
        })
        log.info("Created subscription %s for user %s (status=%s)", record.stripe_subscription_id, user_id, record.status)
        return record

    def cancel_subscription(
        self,
        user_id: str,
        at_period_end: bool = True,
        reason: str = "",
    ) -> SubscriptionRecord:
        """
        Cancel a user's Pro subscription.

        By default, cancels at the end of the current billing period
        (user retains access until then). Pass at_period_end=False to
        cancel immediately.
        """
        record = self.db.get_by_user_id(user_id)
        if not record:
            raise SubscriptionNotFoundError(f"No subscription found for user {user_id!r}")

        if record.status == "canceled":
            log.info("Subscription %s already canceled", record.stripe_subscription_id)
            return record

        sub = self.client.cancel_subscription(
            record.stripe_subscription_id,
            at_period_end=at_period_end,
        )
        updated = self._parse_subscription(user_id, sub)
        self.db.upsert_subscription(updated)
        self.db.audit_log(user_id, "cancel", {
            "subscription_id": record.stripe_subscription_id,
            "at_period_end": at_period_end,
            "reason": reason,
        })
        log.info("Canceled subscription %s for user %s (at_period_end=%s)", record.stripe_subscription_id, user_id, at_period_end)
        return updated

    def get_subscription_status(
        self,
        user_id: str,
        force_refresh: bool = False,
    ) -> Optional[SubscriptionRecord]:
        """
        Return the subscription record for a user, optionally refreshing from Stripe.

        Args:
            user_id: User identifier (email or internal ID)
            force_refresh: If True, re-fetch from Stripe API (slower but authoritative)

        Returns:
            SubscriptionRecord or None if user has no subscription
        """
        record = self.db.get_by_user_id(user_id)
        if record is None:
            return None

        if force_refresh:
            try:
                sub = self.client.get_subscription(record.stripe_subscription_id)
                refreshed = self._parse_subscription(user_id, sub)
                self.db.upsert_subscription(refreshed)
                return refreshed
            except StripeAPIError as exc:
                log.warning("Failed to refresh subscription from Stripe: %s", exc)
                # Return cached version as fallback
        return record

    def reactivate_subscription(self, user_id: str) -> SubscriptionRecord:
        """Reactivate a subscription that was set to cancel at period end."""
        record = self.db.get_by_user_id(user_id)
        if not record:
            raise SubscriptionNotFoundError(f"No subscription found for user {user_id!r}")
        if not record.cancel_at_period_end:
            return record  # Nothing to do

        sub = self.client.request("POST", f"/subscriptions/{record.stripe_subscription_id}", {
            "cancel_at_period_end": "false",
        })
        updated = self._parse_subscription(user_id, sub)
        self.db.upsert_subscription(updated)
        self.db.audit_log(user_id, "reactivate", {"subscription_id": record.stripe_subscription_id})
        return updated

    def create_checkout_session(
        self,
        user_id: str,
        customer_email: str,
        success_url: str = "https://openclaw.app/billing/success",
        cancel_url: str = "https://openclaw.app/billing/cancel",
    ) -> CheckoutSession:
        """
        Create a Stripe-hosted checkout session for self-serve subscription.

        Returns the checkout URL to redirect the user to.
        """
        if not self._price_id:
            raise BillingError("STRIPE_PRICE_ID not configured")

        resp = self.client.create_checkout_session(
            customer_email=customer_email,
            price_id=self._price_id,
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={"guardian_user_id": user_id},
        )
        self.db.audit_log(user_id, "checkout_initiated", {"session_id": resp.get("id", "")})
        return CheckoutSession(
            session_id=resp.get("id", ""),
            checkout_url=resp.get("url", ""),
            customer_email=customer_email,
        )

    def handle_webhook(self, payload: bytes, sig_header: str) -> Tuple[str, Dict[str, Any]]:
        """
        Verify and process a Stripe webhook event.

        Args:
            payload: Raw request body bytes
            sig_header: Value of 'Stripe-Signature' header

        Returns:
            Tuple of (event_type, event_data)

        Raises:
            WebhookVerificationError: If signature cannot be verified
        """
        event = self._verify_webhook(payload, sig_header)
        event_id = event.get("id", "")
        event_type = event.get("type", "")

        if self.db.is_webhook_processed(event_id):
            log.debug("Webhook %s already processed, skipping", event_id)
            return event_type, event

        self._process_webhook_event(event)
        self.db.mark_webhook_processed(event_id, event_type, event)
        return event_type, event

    def _verify_webhook(self, payload: bytes, sig_header: str) -> Dict[str, Any]:
        """Verify Stripe webhook signature (Stripe-Signature header)."""
        if not self._webhook_secret:
            # Allow unsigned webhooks in test/dev mode with a warning
            log.warning("STRIPE_WEBHOOK_SECRET not set — skipping webhook verification (unsafe for production)")
            try:
                return json.loads(payload)
            except json.JSONDecodeError as exc:
                raise WebhookVerificationError(f"Invalid JSON payload: {exc}") from exc

        # Parse signature header: t=<timestamp>,v1=<sig>,...
        parts: Dict[str, str] = {}
        for part in sig_header.split(","):
            k, _, v = part.partition("=")
            parts[k.strip()] = v.strip()

        timestamp = parts.get("t", "")
        signature = parts.get("v1", "")
        if not timestamp or not signature:
            raise WebhookVerificationError("Malformed Stripe-Signature header")

        # Replay-attack protection: reject events > 5 minutes old
        try:
            event_ts = int(timestamp)
        except ValueError:
            raise WebhookVerificationError("Invalid timestamp in Stripe-Signature")

        age = abs(int(time.time()) - event_ts)
        if age > 300:
            raise WebhookVerificationError(f"Webhook too old (age={age}s). Possible replay attack.")

        # Compute expected signature
        signed_payload = f"{timestamp}.{payload.decode('utf-8', errors='replace')}"
        expected = hmac.new(
            self._webhook_secret.encode("utf-8"),
            signed_payload.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(expected, signature):
            raise WebhookVerificationError("Webhook signature mismatch")

        try:
            return json.loads(payload)
        except json.JSONDecodeError as exc:
            raise WebhookVerificationError(f"Invalid JSON payload: {exc}") from exc

    def _process_webhook_event(self, event: Dict[str, Any]) -> None:
        """Update local DB based on Stripe webhook event type."""
        event_type = event.get("type", "")
        data_obj = event.get("data", {}).get("object", {})

        handlers: Dict[str, Any] = {
            "customer.subscription.created": self._on_subscription_created,
            "customer.subscription.updated": self._on_subscription_updated,
            "customer.subscription.deleted": self._on_subscription_deleted,
            "invoice.payment_succeeded": self._on_payment_succeeded,
            "invoice.payment_failed": self._on_payment_failed,
            "checkout.session.completed": self._on_checkout_completed,
        }

        handler = handlers.get(event_type)
        if handler:
            try:
                handler(data_obj)
            except Exception as exc:
                log.error("Error processing webhook %s: %s", event_type, exc)
        else:
            log.debug("Unhandled webhook event: %s", event_type)

    def _on_subscription_created(self, sub: Dict[str, Any]) -> None:
        user_id = sub.get("metadata", {}).get("guardian_user_id", "")
        if not user_id:
            customer_id = sub.get("customer", "")
            if isinstance(customer_id, str):
                # Try to look up user_id from existing DB record
                rec = self.db.get_by_customer_id(customer_id)
                user_id = rec.user_id if rec else customer_id
        if user_id:
            record = self._parse_subscription(user_id, sub)
            self.db.upsert_subscription(record)
            self.db.audit_log(user_id, "webhook_created", {"subscription_id": sub["id"]})

    def _on_subscription_updated(self, sub: Dict[str, Any]) -> None:
        sub_id = sub.get("id", "")
        existing = self.db.get_by_subscription_id(sub_id)
        user_id = sub.get("metadata", {}).get("guardian_user_id", "")
        if not user_id and existing:
            user_id = existing.user_id
        if not user_id:
            customer_id = sub.get("customer", "")
            if isinstance(customer_id, str):
                rec = self.db.get_by_customer_id(customer_id)
                user_id = rec.user_id if rec else customer_id
        if user_id:
            record = self._parse_subscription(user_id, sub)
            self.db.upsert_subscription(record)
            self.db.audit_log(user_id, "webhook_updated", {
                "subscription_id": sub_id, "status": sub.get("status"),
            })

    def _on_subscription_deleted(self, sub: Dict[str, Any]) -> None:
        sub_id = sub.get("id", "")
        self.db.update_status(sub_id, "canceled")
        existing = self.db.get_by_subscription_id(sub_id)
        if existing:
            self.db.audit_log(existing.user_id, "webhook_deleted", {"subscription_id": sub_id})

    def _on_payment_succeeded(self, invoice: Dict[str, Any]) -> None:
        sub_id = invoice.get("subscription", "")
        if sub_id:
            period_end = invoice.get("lines", {}).get("data", [{}])[0].get("period", {}).get("end", 0)
            self.db.update_status(sub_id, "active", period_end=period_end or None)

    def _on_payment_failed(self, invoice: Dict[str, Any]) -> None:
        sub_id = invoice.get("subscription", "")
        if sub_id:
            self.db.update_status(sub_id, "past_due")
            existing = self.db.get_by_subscription_id(sub_id)
            if existing:
                self.db.audit_log(existing.user_id, "payment_failed", {"subscription_id": sub_id})

    def _on_checkout_completed(self, session: Dict[str, Any]) -> None:
        # Subscription will be created via customer.subscription.created event
        user_id = session.get("metadata", {}).get("guardian_user_id", "")
        self.db.audit_log(user_id or "unknown", "checkout_completed", {
            "session_id": session.get("id", ""),
        })


# ---------------------------------------------------------------------------
# Subscription Gate (used in API server middleware)
# ---------------------------------------------------------------------------


class SubscriptionGate:
    """
    Lightweight feature gating layer for Guardian Pro endpoints.

    Usage in API handlers::

        gate = SubscriptionGate(manager=mgr)

        # Check without raising
        if gate.is_pro("user@example.com"):
            serve_premium_signatures()

        # Check with exception on failure
        gate.require_pro("user@example.com", feature="premium_signatures")
    """

    def __init__(
        self,
        manager: Optional[SubscriptionManager] = None,
        db_path: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> None:
        if manager is not None:
            self.manager = manager
        else:
            self.manager = SubscriptionManager(
                api_key=api_key or os.environ.get("STRIPE_SECRET_KEY", ""),
                db_path=db_path or os.environ.get("BILLING_DB_PATH", ":memory:"),
            )

    def is_pro(self, user_id: str, refresh_if_expired: bool = False) -> bool:
        """
        Return True if the user has an active (or grace-period) Pro subscription.

        Args:
            user_id: User identifier (email or internal ID)
            refresh_if_expired: If True and local cache shows expired, re-check Stripe
        """
        if not user_id:
            return False

        record = self.manager.db.get_by_user_id(user_id)
        if record is None:
            return False

        if record.is_active:
            return True

        # Local cache says inactive — optionally re-verify with Stripe
        if refresh_if_expired and record.status not in ("canceled",):
            try:
                refreshed = self.manager.get_subscription_status(user_id, force_refresh=True)
                if refreshed:
                    return refreshed.is_active
            except Exception as exc:
                log.warning("Failed to refresh subscription status for %s: %s", user_id, exc)

        return False

    def require_pro(self, user_id: str, feature: str = "premium_signatures") -> SubscriptionRecord:
        """
        Assert the user has an active Pro subscription for a given feature.

        Raises:
            FeatureGatedError: If user does not have an active Pro subscription.
        """
        record = self.manager.db.get_by_user_id(user_id)
        if record and record.is_active:
            return record
        raise FeatureGatedError(user_id, feature)

    def get_plan_info(self, user_id: str) -> Dict[str, Any]:
        """Return plan details for a user (used for API status responses)."""
        record = self.manager.db.get_by_user_id(user_id)
        if record is None:
            return {"plan": "free", "features": [], "is_pro": False}

        features = PRO_TIER_FEATURES if record.is_active else []
        return {
            "plan": "pro" if record.is_active else "free",
            "status": record.status,
            "subscription_id": record.stripe_subscription_id,
            "current_period_end": record.expires_at_iso,
            "cancel_at_period_end": record.cancel_at_period_end,
            "features": features,
            "is_pro": record.is_active,
        }


# ---------------------------------------------------------------------------
# Convenience factory
# ---------------------------------------------------------------------------


def create_manager_from_env(db_path: Optional[str] = None) -> SubscriptionManager:
    """
    Create a SubscriptionManager configured from environment variables.

    Required env vars:
        STRIPE_SECRET_KEY    — Stripe secret key
        STRIPE_PRICE_ID      — Price ID for the $9/mo Guardian Pro plan

    Optional:
        STRIPE_WEBHOOK_SECRET — For webhook signature verification
        BILLING_DB_PATH       — SQLite path (default: billing.db)
    """
    api_key = os.environ.get("STRIPE_SECRET_KEY", "")
    price_id = os.environ.get("STRIPE_PRICE_ID", "")
    webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
    db = db_path or os.environ.get("BILLING_DB_PATH", "billing.db")

    if not api_key:
        raise BillingError(
            "STRIPE_SECRET_KEY not set. Cannot initialise billing. "
            "Set it in your environment or pass api_key= directly."
        )

    return SubscriptionManager(
        api_key=api_key,
        price_id=price_id,
        webhook_secret=webhook_secret,
        db_path=db,
    )


# ---------------------------------------------------------------------------
# API endpoint handlers (used by billing_api.py / serve.py integration)
# ---------------------------------------------------------------------------


def handle_subscribe(
    manager: SubscriptionManager,
    data: Dict[str, Any],
) -> Tuple[int, Dict[str, Any]]:
    """
    Handle POST /billing/subscribe.

    Expected body::

        {
            "user_id": "user@example.com",
            "customer_email": "user@example.com",
            "payment_method_id": "pm_...",   // optional if using checkout
            "name": "Jane Doe"                // optional
        }
    """
    user_id = str(data.get("user_id", "")).strip()
    email = str(data.get("customer_email", "")).strip()
    pm_id = str(data.get("payment_method_id", "")).strip() or None
    name = str(data.get("name", "")).strip()

    if not user_id or not email:
        return 400, {"error": "user_id and customer_email are required"}

    try:
        record = manager.create_subscription(
            user_id=user_id,
            customer_email=email,
            payment_method_id=pm_id,
            name=name,
        )
        return 200, {
            "ok": True,
            "subscription_id": record.stripe_subscription_id,
            "status": record.status,
            "current_period_end": record.expires_at_iso,
            "plan": "pro",
            "features": PRO_TIER_FEATURES,
        }
    except BillingError as exc:
        return 400, {"error": str(exc)}
    except Exception as exc:
        log.exception("Unexpected error in subscribe handler")
        return 500, {"error": "Internal billing error"}


def handle_cancel(
    manager: SubscriptionManager,
    data: Dict[str, Any],
) -> Tuple[int, Dict[str, Any]]:
    """
    Handle POST /billing/cancel.

    Expected body::

        {
            "user_id": "user@example.com",
            "at_period_end": true,   // optional, default true
            "reason": "..."          // optional
        }
    """
    user_id = str(data.get("user_id", "")).strip()
    at_period_end = bool(data.get("at_period_end", True))
    reason = str(data.get("reason", "")).strip()

    if not user_id:
        return 400, {"error": "user_id is required"}

    try:
        record = manager.cancel_subscription(user_id, at_period_end=at_period_end, reason=reason)
        return 200, {
            "ok": True,
            "subscription_id": record.stripe_subscription_id,
            "status": record.status,
            "cancel_at_period_end": record.cancel_at_period_end,
            "access_until": record.expires_at_iso,
        }
    except SubscriptionNotFoundError as exc:
        return 404, {"error": str(exc)}
    except BillingError as exc:
        return 400, {"error": str(exc)}
    except Exception:
        log.exception("Unexpected error in cancel handler")
        return 500, {"error": "Internal billing error"}


def handle_status(
    manager: SubscriptionManager,
    user_id: str,
) -> Tuple[int, Dict[str, Any]]:
    """
    Handle GET /billing/status?user_id=<user_id>.
    """
    if not user_id:
        return 400, {"error": "user_id query parameter is required"}

    record = manager.get_subscription_status(user_id)
    if record is None:
        return 200, {
            "user_id": user_id,
            "plan": "free",
            "status": "none",
            "is_pro": False,
            "features": [],
        }

    gate = SubscriptionGate(manager=manager)
    plan_info = gate.get_plan_info(user_id)
    return 200, {"user_id": user_id, **plan_info}


def handle_webhook_event(
    manager: SubscriptionManager,
    payload: bytes,
    sig_header: str,
) -> Tuple[int, Dict[str, Any]]:
    """
    Handle POST /billing/webhook (Stripe webhook endpoint).
    """
    try:
        event_type, _ = manager.handle_webhook(payload, sig_header)
        return 200, {"ok": True, "received": event_type}
    except WebhookVerificationError as exc:
        log.warning("Webhook verification failed: %s", exc)
        return 400, {"error": str(exc)}
    except Exception:
        log.exception("Unexpected error in webhook handler")
        return 500, {"error": "Webhook processing failed"}


if __name__ == "__main__":
    # Quick smoke-test with test credentials
    import sys

    logging.basicConfig(level=logging.INFO)
    key = os.environ.get("STRIPE_SECRET_KEY", "")
    if not key or not key.startswith("sk_test_"):
        print("Set STRIPE_SECRET_KEY=sk_test_... to run smoke test", file=sys.stderr)
        sys.exit(1)

    mgr = create_manager_from_env(db_path=":memory:")
    print("SubscriptionManager created OK")
    gate = SubscriptionGate(manager=mgr)
    print(f"is_pro('nobody@example.com') = {gate.is_pro('nobody@example.com')}")
    print("Smoke test passed.")
