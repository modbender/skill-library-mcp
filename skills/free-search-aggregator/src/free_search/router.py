"""Provider routing, failover, and quota/rate awareness."""

from __future__ import annotations

import json
import logging
import os
import re
import time
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from .providers import (
    AuthError,
    NetworkError,
    ParseError,
    ProviderError,
    QuotaExceededError,
    RateLimitError,
    SearchItem,
    UpstreamError,
    PROVIDER_REGISTRY,
)

logger = logging.getLogger(__name__)
_UNRESOLVED_ENV_PATTERN = re.compile(r"^\$\{[A-Za-z_][A-Za-z0-9_]*\}$")

# Warn when a provider has consumed this fraction of its daily quota
QUOTA_WARN_THRESHOLD = 0.80


class SearchRouterError(Exception):
    """Raised when all providers are exhausted."""


class QuotaState:
    """Persistent provider usage tracker with day-level quotas."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.today = datetime.now(UTC).date().isoformat()
        self.state: dict[str, Any] = {"date": self.today, "providers": {}}
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            logger.warning("Unable to read quota state at %s; resetting", self.path)
            return
        if data.get("date") != self.today:
            return
        self.state = data

    def save(self) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps(self.state, indent=2), encoding="utf-8")
        except OSError:
            logger.warning("Failed to persist quota state at %s", self.path, exc_info=True)

    def get_count(self, provider: str) -> int:
        pstate = self.state["providers"].get(provider, {})
        return int(pstate.get("requests", 0))

    def increment(self, provider: str) -> None:
        pstate = self.state["providers"].setdefault(provider, {})
        pstate["requests"] = int(pstate.get("requests", 0)) + 1
        pstate["last_request_ts"] = int(time.time())

    def reset(self, provider: str | None = None) -> None:
        if provider is None:
            self.state = {"date": self.today, "providers": {}}
            return
        self.state["providers"].pop(provider, None)


class SearchRouter:
    """Routes search requests through ordered providers with failover."""

    def __init__(self, config_path: str | os.PathLike[str] | None = None) -> None:
        default_config = Path(__file__).resolve().parents[2] / "config" / "providers.yaml"
        self.config_path = Path(config_path) if config_path else default_config
        self.config = self._load_config(self.config_path)
        self.order = self._load_order(self.config)

        quota_path = self.config.get("router", {}).get("quota_state_file", ".quota_state.json")
        if not os.path.isabs(quota_path):
            quota_path = str((self.config_path.parent / quota_path).resolve())
        self.quota = QuotaState(Path(quota_path))

        self.providers = self._build_providers()

    @staticmethod
    def _expand_env(value: Any) -> Any:
        if isinstance(value, str):
            expanded = os.path.expandvars(value)
            # Treat unresolved `${VAR}` placeholders as unset to avoid false auth attempts.
            if _UNRESOLVED_ENV_PATTERN.match(expanded):
                return ""
            return expanded
        if isinstance(value, dict):
            return {k: SearchRouter._expand_env(v) for k, v in value.items()}
        if isinstance(value, list):
            return [SearchRouter._expand_env(v) for v in value]
        return value

    def _load_config(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            raise FileNotFoundError(f"Provider config not found: {path}")
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        return self._expand_env(raw)

    def _load_order(self, config: dict[str, Any]) -> list[str]:
        order = config.get("router", {}).get("provider_order")
        if order:
            return [str(p).strip().lower() for p in order if str(p).strip()]
        return ["brave", "tavily", "duckduckgo", "serper"]

    def _build_providers(self) -> dict[str, Any]:
        configured = self.config.get("providers", {})
        providers: dict[str, Any] = {}
        for name in self.order:
            pconf = configured.get(name, {})
            cls = PROVIDER_REGISTRY.get(name)
            if not cls:
                logger.warning("Unknown provider in order list: %s", name)
                continue
            providers[name] = cls(config=pconf)
        return providers

    def _has_quota(self, name: str, provider_cfg: dict[str, Any]) -> bool:
        daily_quota = provider_cfg.get("daily_quota")
        if daily_quota is None:
            return True
        daily_quota = int(daily_quota)
        used = self.quota.get_count(name)
        if daily_quota > 0 and used >= daily_quota * QUOTA_WARN_THRESHOLD:
            pct = round(used / daily_quota * 100, 1)
            logger.warning(
                "Provider %s quota at %.1f%% (%d/%d) — nearing daily limit",
                name, pct, used, daily_quota,
            )
        return used < daily_quota

    def _try_provider(
        self,
        name: str,
        provider: Any,
        query: str,
        max_results: int,
    ) -> tuple[list[SearchItem] | None, dict[str, Any], bool]:
        """Attempt one provider search.

        Returns:
            (items, attempt_record, count_quota)
            - items=None means a hard failure (skip to next provider)
            - items=[]   means no results (skip to next provider, quota consumed)
            - items=[..] means success
            - count_quota: True if the HTTP request reached the provider
        """
        started = time.perf_counter()

        try:
            items: list[SearchItem] = provider.search(query, max_results=max_results)
        except (AuthError, NetworkError) as exc:
            # AuthError  → API rejected the key; provider quota was NOT consumed
            # NetworkError → request never reached the provider
            elapsed_ms = int((time.perf_counter() - started) * 1000)
            logger.warning("Provider %s failed (%s): %s", name, type(exc).__name__, exc)
            return (
                None,
                {
                    "provider": name,
                    "status": "failed",
                    "reason": type(exc).__name__,
                    "detail": str(exc),
                    "latency_ms": elapsed_ms,
                },
                False,  # do NOT count quota
            )
        except ProviderError as exc:
            # RateLimitError / UpstreamError / ParseError / QuotaExceededError
            # Request reached the provider → count quota
            elapsed_ms = int((time.perf_counter() - started) * 1000)
            logger.warning("Provider %s failed (%s): %s", name, type(exc).__name__, exc)
            return (
                None,
                {
                    "provider": name,
                    "status": "failed",
                    "reason": type(exc).__name__,
                    "detail": str(exc),
                    "latency_ms": elapsed_ms,
                },
                True,  # count quota — request was made
            )
        except Exception as exc:  # pragma: no cover — defensive failover guard
            elapsed_ms = int((time.perf_counter() - started) * 1000)
            logger.exception("Provider %s crashed unexpectedly", name)
            return (
                None,
                {
                    "provider": name,
                    "status": "failed",
                    "reason": "unexpected_error",
                    "detail": str(exc),
                    "latency_ms": elapsed_ms,
                },
                False,
            )

        elapsed_ms = int((time.perf_counter() - started) * 1000)
        if not items:
            return (
                [],
                {
                    "provider": name,
                    "status": "failed",
                    "reason": "empty_results",
                    "detail": "provider returned zero results",
                    "latency_ms": elapsed_ms,
                },
                True,  # request was made
            )

        return (
            items,
            {
                "provider": name,
                "status": "ok",
                "result_count": len(items),
                "latency_ms": elapsed_ms,
            },
            True,
        )

    def search(self, query: str, *, max_results: int = 8) -> dict[str, Any]:
        if max_results <= 0:
            raise ValueError("max_results must be > 0")
        attempted: list[dict[str, Any]] = []
        providers_cfg = self.config.get("providers", {})

        for name in self.order:
            provider = self.providers.get(name)
            cfg = providers_cfg.get(name, {})

            if not provider:
                attempted.append({"provider": name, "status": "skipped", "reason": "not_configured"})
                continue
            if not provider.is_enabled():
                attempted.append({"provider": name, "status": "skipped", "reason": "disabled"})
                continue
            if not self._has_quota(name, cfg):
                attempted.append({"provider": name, "status": "failed", "reason": "quota_exceeded"})
                continue

            logger.info("Attempting provider=%s for query=%r", name, query)
            items, attempt, count_quota = self._try_provider(name, provider, query, max_results)

            if count_quota:
                self.quota.increment(name)
                self.quota.save()

            attempted.append(attempt)

            if not items:  # None (error) or [] (empty results) → try next
                continue

            return {
                "query": query,
                "provider": name,
                "results": [asdict(item) for item in items],
                "meta": {
                    "attempted": attempted,
                    "quota": self._quota_snapshot(),
                    "timestamp_utc": datetime.now(UTC).isoformat(),
                },
            }

        logger.error("All providers exhausted for query=%r", query)
        raise SearchRouterError(
            "All providers failed. "
            + " | ".join(f"{x['provider']}:{x.get('reason', 'unknown')}" for x in attempted)
        )

    def _quota_snapshot(self) -> dict[str, Any]:
        providers_cfg = self.config.get("providers", {})
        snapshot: dict[str, Any] = {}
        for name in self.order:
            used = self.quota.get_count(name)
            daily_quota = providers_cfg.get(name, {}).get("daily_quota")
            snapshot[name] = {
                "used_today": used,
                "daily_quota": int(daily_quota) if daily_quota is not None else None,
                "remaining": None if daily_quota is None else max(int(daily_quota) - used, 0),
            }
        return snapshot

    @staticmethod
    def _percentage_used(used: int, daily_quota: int | None) -> float | None:
        if daily_quota is None or daily_quota <= 0:
            return None
        return round((used / daily_quota) * 100, 2)

    def quota_status(self) -> dict[str, Any]:
        providers_cfg = self.config.get("providers", {})
        providers: list[dict[str, Any]] = []
        for name in self.order:
            used = self.quota.get_count(name)
            daily_quota_raw = providers_cfg.get(name, {}).get("daily_quota")
            daily_quota = int(daily_quota_raw) if daily_quota_raw is not None else None
            remaining = None if daily_quota is None else max(daily_quota - used, 0)
            providers.append(
                {
                    "provider": name,
                    "used_today": used,
                    "remaining": remaining,
                    "daily_quota": daily_quota,
                    "percentage_used": self._percentage_used(used, daily_quota),
                }
            )
        return {
            "date": self.quota.state.get("date", self.quota.today),
            "providers": providers,
        }

    def reset_quota(self, provider: str | None = None) -> dict[str, Any]:
        self.quota.reset(provider)
        self.quota.save()
        return self.quota_status()
