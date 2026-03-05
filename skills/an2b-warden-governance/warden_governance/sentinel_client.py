"""War/Den Governance Client -- routes to community or enterprise governance.

Community mode: evaluates policies locally via CommunityPolicyEngine.
Enterprise mode: POSTs to Sentinel_OS /api/v1/check for cloud evaluation.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from warden_governance.action_bridge import (
    Action,
    CheckResult,
    Decision,
    GovernanceError,
)
from warden_governance.audit_log import LocalAuditLog
from warden_governance.policy_engine import CommunityPolicyEngine
from warden_governance.settings import Settings

logger = logging.getLogger("warden")


class PolicyDecisionCache:
    """Session-scoped cache for governance decisions.

    Rules:
    - Only caches ALLOW decisions
    - DENY and REVIEW are NEVER cached (always hit fresh)
    - Configurable TTL (default 300s)
    """

    def __init__(self, ttl_seconds: int = 300):
        self._cache: dict[str, dict[str, Any]] = {}
        self._ttl = ttl_seconds
        self._hits = 0
        self._misses = 0

    def get(self, action_type: str, env: str) -> CheckResult | None:
        key = f"{action_type}:{env}"
        entry = self._cache.get(key)

        if entry is None:
            self._misses += 1
            return None

        if time.time() - entry["cached_at"] > self._ttl:
            del self._cache[key]
            self._misses += 1
            return None

        self._hits += 1
        return entry["result"]

    def set(self, action_type: str, env: str, result: CheckResult) -> None:
        if result.decision != Decision.ALLOW:
            return
        key = f"{action_type}:{env}"
        self._cache[key] = {"result": result, "cached_at": time.time()}

    def clear(self) -> None:
        self._cache.clear()
        self._hits = 0
        self._misses = 0

    def stats(self) -> dict[str, Any]:
        total = self._hits + self._misses
        return {
            "hits": self._hits,
            "misses": self._misses,
            "cached_keys": len(self._cache),
            "hit_rate": self._hits / total if total else 0.0,
        }


class SentinelClient:
    """Governance gateway. Routes checks to community or enterprise engine."""

    def __init__(self, config: Settings):
        self.config = config
        self.cache = PolicyDecisionCache(ttl_seconds=config.warden_cache_ttl)
        self.audit_log = LocalAuditLog(config.warden_audit_db)

        # Initialize policy engine
        self.policy_engine = CommunityPolicyEngine(
            policy_file=config.warden_policy_file or None,
        )

        # Load policy packs
        if config.warden_policy_packs:
            for pack_name in config.warden_policy_packs.split(","):
                pack_name = pack_name.strip()
                if pack_name:
                    self.policy_engine.load_pack(pack_name)

        self._enterprise_mode = bool(config.sentinel_api_key)

    def check(self, action: Action) -> CheckResult:
        """Evaluate an action against governance policies.

        Returns CheckResult with decision: ALLOW, DENY, or REVIEW.
        Writes every decision to the audit log.
        Raises GovernanceError on DENY (when fail_open=false).
        """
        env = action.context.get("env", "dev")

        cached = self.cache.get(action.type.value, env)
        if cached is not None:
            return cached

        try:
            if self._enterprise_mode:
                result = self._check_enterprise(action)
            else:
                result = self._check_community(action)
        except GovernanceError:
            raise
        except Exception as exc:
            logger.error("Governance engine error: %s", exc)
            if self.config.warden_fail_open:
                return CheckResult(
                    decision=Decision.ALLOW,
                    reason=f"governance engine error (fail-open): {exc}",
                )
            raise GovernanceError(f"governance engine error: {exc}")

        self.audit_log.write(
            action=action,
            decision=result.decision,
            reason=result.reason,
            policy_id=result.policy_id,
        )

        self.cache.set(action.type.value, env, result)

        if result.decision == Decision.DENY:
            raise GovernanceError(result.reason, result.policy_id)

        return result

    def _check_community(self, action: Action) -> CheckResult:
        """Evaluate using the local policy engine."""
        return self.policy_engine.evaluate(action)

    def _check_enterprise(self, action: Action) -> CheckResult:
        """Evaluate using Sentinel_OS cloud API (/api/v1/check)."""
        try:
            import httpx
        except ImportError:
            logger.warning(
                "httpx not installed; falling back to community governance. "
                "Install httpx for enterprise mode: pip install httpx"
            )
            return self._check_community(action)

        url = f"{self.config.sentinel_base_url}/api/v1/check"
        payload = action.to_sentinel_payload()

        try:
            with httpx.Client(timeout=30) as client:
                resp = client.post(
                    url,
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {self.config.sentinel_api_key}",
                        "Content-Type": "application/json",
                        "User-Agent": "WardenGovernanceSkill/1.0.0",
                    },
                )

            if resp.status_code == 401:
                logger.error("Invalid SENTINEL_API_KEY")
                if not self.config.warden_fail_open:
                    return CheckResult(
                        decision=Decision.DENY,
                        reason="Invalid SENTINEL_API_KEY -- check your key at getsentinelos.com",
                    )
                return CheckResult(
                    decision=Decision.ALLOW,
                    reason="SENTINEL_API_KEY invalid; fail-open enabled",
                )

            data = resp.json()
            decision = Decision(data.get("decision", "allow"))
            return CheckResult(
                decision=decision,
                reason=data.get("reason", ""),
                policy_id=data.get("policyId"),
                check_id=data.get("checkId", ""),
                evaluated_at=data.get("evaluatedAt", ""),
            )

        except Exception as exc:
            logger.error("Sentinel_OS unreachable: %s", exc)
            if not self.config.warden_fail_open:
                return CheckResult(
                    decision=Decision.DENY,
                    reason=f"Sentinel_OS unreachable: {exc}",
                )
            return CheckResult(
                decision=Decision.ALLOW,
                reason=f"Sentinel_OS unreachable; fail-open enabled: {exc}",
            )
