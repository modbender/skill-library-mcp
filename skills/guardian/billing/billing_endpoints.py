#!/usr/bin/env python3
"""
Guardian Pro Billing HTTP Endpoints
====================================
Drop-in extension for Guardian's HTTP server (scripts/serve.py).

Adds the following routes when Guardian Pro is enabled:

  GET  /billing/status?user_id=<id>   — subscription status
  POST /billing/subscribe              — create subscription
  POST /billing/cancel                 — cancel subscription
  POST /billing/webhook                — Stripe webhook receiver
  GET  /billing/plan                   — plan features info
  GET  /pro/signatures                 — premium signature delivery (gated)

Integration example (in scripts/serve.py do_GET / do_POST)::

    from billing.billing_endpoints import BillingRouter

    # In server init:
    billing = BillingRouter.from_config(config_path="config.json")

    # In GuardianHTTPHandler.do_GET:
    handled, status, payload = billing.handle_get(self.path, self.headers)
    if handled:
        self._json_response(status, payload)
        return

    # In GuardianHTTPHandler.do_POST:
    handled, status, payload = billing.handle_post(self.path, self.headers, body_bytes)
    if handled:
        self._json_response(status, payload)
        return
"""

from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from urllib.parse import parse_qs, urlparse

log = logging.getLogger(__name__)

# Allow imports from workspace root
_WORKSPACE = Path(__file__).resolve().parent.parent
if str(_WORKSPACE) not in sys.path:
    sys.path.insert(0, str(_WORKSPACE))

from billing.stripe_integration import (
    FeatureGatedError,
    SubscriptionGate,
    SubscriptionManager,
    handle_cancel,
    handle_status,
    handle_subscribe,
    handle_webhook_event,
)

# Premium signature packs directory (relative to skill root)
_SKILL_ROOT = _WORKSPACE / "skills" / "guardian"
_PREMIUM_SIGS_DIR = _SKILL_ROOT / "definitions" / "premium"

# ---------------------------------------------------------------------------
# Premium signature delivery
# ---------------------------------------------------------------------------


def _load_premium_signatures(pack_names: Optional[list] = None) -> Dict[str, Any]:
    """
    Load premium signature packs from disk.

    In production these packs live in definitions/premium/ and are only
    served to verified Pro subscribers. Returns merged signature data.
    """
    if pack_names is None:
        pack_names = [
            "advanced-injection-v2.json",
            "llm-jailbreaks.json",
            "supply-chain-attacks.json",
        ]

    merged: Dict[str, Any] = {"signatures": [], "version": "2.1.0", "tier": "pro"}

    if not _PREMIUM_SIGS_DIR.exists():
        # Premium packs not yet generated — return placeholder
        merged["signatures"] = [
            {
                "id": "PRO-001",
                "description": "Advanced multi-stage prompt injection (Pro)",
                "severity": "critical",
                "score": 95,
                "tier": "pro",
            },
            {
                "id": "PRO-002",
                "description": "LLM jailbreak via role-playing scaffold (Pro)",
                "severity": "high",
                "score": 85,
                "tier": "pro",
            },
            {
                "id": "PRO-003",
                "description": "Supply chain tool poisoning pattern (Pro)",
                "severity": "critical",
                "score": 98,
                "tier": "pro",
            },
            {
                "id": "PRO-004",
                "description": "Insider threat: mass file enumeration (Pro)",
                "severity": "high",
                "score": 80,
                "tier": "pro",
            },
        ]
        merged["_note"] = "Premium pack directory not yet populated. Showing placeholder definitions."
        return merged

    for pack in pack_names:
        pack_path = _PREMIUM_SIGS_DIR / pack
        if not pack_path.exists():
            continue
        try:
            data = json.loads(pack_path.read_text(encoding="utf-8"))
            sigs = data.get("signatures", data) if isinstance(data, dict) else data
            merged["signatures"].extend(sigs)
        except (json.JSONDecodeError, OSError) as exc:
            log.warning("Failed to load premium pack %s: %s", pack, exc)

    return merged


# ---------------------------------------------------------------------------
# BillingRouter — main integration class
# ---------------------------------------------------------------------------


class BillingRouter:
    """
    Handles all /billing/* and /pro/* HTTP routes.

    Thread-safe (manager and gate hold no per-request state).
    """

    # Routes handled by this router
    GET_ROUTES = {"/billing/status", "/billing/plan", "/pro/signatures"}
    POST_ROUTES = {"/billing/subscribe", "/billing/cancel", "/billing/webhook"}

    def __init__(
        self,
        manager: SubscriptionManager,
        enabled: bool = True,
        gating_mode: str = "soft",
        user_id_header: str = "X-Guardian-User-Id",
    ) -> None:
        self.manager = manager
        self.gate = SubscriptionGate(manager=manager)
        self.enabled = enabled
        self.gating_mode = gating_mode  # "soft" | "hard"
        self.user_id_header = user_id_header

    @classmethod
    def from_config(cls, config_path: Optional[str] = None) -> "BillingRouter":
        """
        Construct a BillingRouter from Guardian's config.json.

        Returns a no-op router (enabled=False) if pro_tier is not configured.
        """
        cfg_path = Path(config_path or (_SKILL_ROOT / "config.json"))
        try:
            cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            log.warning("Cannot load config for billing: %s", exc)
            return cls._disabled()

        pro = cfg.get("pro_tier", {})
        if not pro.get("enabled", False):
            log.info("Guardian Pro tier not enabled in config. Billing routes inactive.")
            return cls._disabled()

        billing = pro.get("billing", {})
        access = pro.get("access_control", {})

        # Resolve billing DB path
        db_path = billing.get("billing_db_path", "auto")
        if db_path == "auto":
            db_path = str(_SKILL_ROOT / "billing.db")

        api_key = os.environ.get("STRIPE_SECRET_KEY", "")
        price_id = billing.get("stripe_price_id") or os.environ.get("STRIPE_PRICE_ID", "")
        webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

        try:
            mgr = SubscriptionManager(
                api_key=api_key,
                price_id=price_id,
                db_path=db_path,
                webhook_secret=webhook_secret,
            )
        except Exception as exc:
            log.error("Failed to initialise SubscriptionManager: %s", exc)
            return cls._disabled()

        return cls(
            manager=mgr,
            enabled=True,
            gating_mode=access.get("gating_mode", "soft"),
            user_id_header=access.get("user_id_header", "X-Guardian-User-Id"),
        )

    @classmethod
    def _disabled(cls) -> "BillingRouter":
        """Return a router that responds to no billing routes."""
        dummy_mgr = SubscriptionManager(api_key="sk_test_disabled", db_path=":memory:")
        router = cls(manager=dummy_mgr, enabled=False)
        return router

    # ---- Route dispatch --------------------------------------------------

    def handles_get(self, path: str) -> bool:
        return self.enabled and urlparse(path).path in self.GET_ROUTES

    def handles_post(self, path: str) -> bool:
        return self.enabled and urlparse(path).path in self.POST_ROUTES

    def handle_get(
        self,
        path: str,
        headers: Any,
    ) -> Tuple[bool, int, Dict[str, Any]]:
        """
        Try to handle a GET request.

        Returns:
            (handled, status_code, payload) — if handled=False, caller should proceed normally.
        """
        parsed = urlparse(path)
        route = parsed.path

        if not self.enabled or route not in self.GET_ROUTES:
            return False, 0, {}

        qs = parse_qs(parsed.query)
        user_id = self._extract_user_id(headers, qs)

        if route == "/billing/status":
            status, payload = handle_status(self.manager, user_id)
            return True, status, payload

        if route == "/billing/plan":
            if not user_id:
                return True, 400, {"error": "user_id required (via header or query param)"}
            plan = self.gate.get_plan_info(user_id)
            return True, 200, {"user_id": user_id, **plan}

        if route == "/pro/signatures":
            return True, *self._handle_pro_signatures(user_id)

        return False, 0, {}

    def handle_post(
        self,
        path: str,
        headers: Any,
        body: bytes,
    ) -> Tuple[bool, int, Dict[str, Any]]:
        """
        Try to handle a POST request.

        Returns:
            (handled, status_code, payload)
        """
        parsed = urlparse(path)
        route = parsed.path

        if not self.enabled or route not in self.POST_ROUTES:
            return False, 0, {}

        if route == "/billing/webhook":
            sig_header = self._get_header(headers, "Stripe-Signature") or ""
            status, payload = handle_webhook_event(self.manager, body, sig_header)
            return True, status, payload

        # For other POST routes, parse JSON body
        try:
            data: Dict[str, Any] = json.loads(body.decode("utf-8")) if body else {}
        except (json.JSONDecodeError, UnicodeDecodeError):
            return True, 400, {"error": "Request body must be valid JSON"}

        if route == "/billing/subscribe":
            status, payload = handle_subscribe(self.manager, data)
            return True, status, payload

        if route == "/billing/cancel":
            status, payload = handle_cancel(self.manager, data)
            return True, status, payload

        return False, 0, {}

    # ---- Premium signature delivery -------------------------------------

    def _handle_pro_signatures(self, user_id: str) -> Tuple[int, Dict[str, Any]]:
        """
        Serve premium signature pack to verified Pro subscribers.

        In "soft" gating mode, falls back to free-tier signatures on auth failure.
        In "hard" gating mode, returns 403 if subscription check fails.
        """
        if not user_id:
            if self.gating_mode == "hard":
                return 401, {
                    "error": "Authentication required",
                    "hint": f"Set the {self.user_id_header} header with your user ID",
                }
            # Soft mode: serve free tier signatures with upgrade notice
            return 200, self._free_tier_response()

        try:
            self.gate.require_pro(user_id, feature="premium_signatures")
        except FeatureGatedError as exc:
            if self.gating_mode == "hard":
                return 403, {
                    "error": str(exc),
                    "upgrade_url": "https://openclaw.app/pro",
                    "plan": "free",
                }
            # Soft gating: serve free tier with notice
            return 200, self._free_tier_response(upgrade_hint=True)

        # Pro user — serve premium packs
        sigs = _load_premium_signatures()
        sigs["user_id"] = user_id
        sigs["access"] = "pro"
        return 200, sigs

    def _free_tier_response(self, upgrade_hint: bool = False) -> Dict[str, Any]:
        resp: Dict[str, Any] = {
            "signatures": [],
            "version": "2.1.0",
            "tier": "free",
            "access": "free",
            "_note": "Free tier does not include premium signature packs.",
        }
        if upgrade_hint:
            resp["upgrade_url"] = "https://openclaw.app/pro"
            resp["upgrade_message"] = (
                "Upgrade to Guardian Pro ($9/mo) for premium signatures, "
                "extended analytics, and priority support."
            )
        return resp

    # ---- Helpers ---------------------------------------------------------

    def _extract_user_id(self, headers: Any, qs: Dict[str, Any]) -> str:
        """Extract user_id from header or query string."""
        # Try custom header first
        uid = self._get_header(headers, self.user_id_header) or ""
        if uid:
            return uid.strip()
        # Fall back to query param
        uid_list = qs.get("user_id", [])
        if uid_list:
            return str(uid_list[0]).strip()
        return ""

    @staticmethod
    def _get_header(headers: Any, name: str) -> Optional[str]:
        """Extract a header value from various header object types."""
        if headers is None:
            return None
        # http.server BaseHTTPRequestHandler.headers (email.message.Message)
        if hasattr(headers, "get"):
            return headers.get(name) or headers.get(name.lower())
        # Dict fallback
        if isinstance(headers, dict):
            return headers.get(name) or headers.get(name.lower())
        return None
