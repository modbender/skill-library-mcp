"""Fetch real provider quota/usage when supported by provider APIs."""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Any

import requests

from .router import SearchRouter


@dataclass
class RealQuotaResult:
    provider: str
    supported: bool
    ok: bool
    remaining: int | None
    limit: int | None
    used: int | None
    unit: str | None
    detail: str | None
    raw: dict[str, Any] | None
    probe_consumes_request: bool = False


def _safe_int(value: Any) -> int | None:
    try:
        if value is None:
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def _get_searchapi_quota(api_key: str) -> RealQuotaResult:
    url = "https://www.searchapi.io/api/v1/me"
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
    except requests.RequestException as exc:
        return RealQuotaResult(
            provider="searchapi",
            supported=True,
            ok=False,
            remaining=None,
            limit=None,
            used=None,
            unit="monthly_credits",
            detail=f"network_error: {exc}",
            raw=None,
        )

    if resp.status_code != 200:
        return RealQuotaResult(
            provider="searchapi",
            supported=True,
            ok=False,
            remaining=None,
            limit=None,
            used=None,
            unit="monthly_credits",
            detail=f"http_{resp.status_code}: {resp.text[:200]}",
            raw=None,
        )

    try:
        payload = resp.json()
    except ValueError:
        return RealQuotaResult(
            provider="searchapi",
            supported=True,
            ok=False,
            remaining=None,
            limit=None,
            used=None,
            unit="monthly_credits",
            detail="invalid_json",
            raw={"text": resp.text[:200]},
        )

    account = payload.get("account", {}) if isinstance(payload, dict) else {}
    remaining = _safe_int(account.get("remaining_credits"))
    limit = _safe_int(account.get("monthly_allowance"))
    used = _safe_int(account.get("current_month_usage"))
    return RealQuotaResult(
        provider="searchapi",
        supported=True,
        ok=True,
        remaining=remaining,
        limit=limit,
        used=used,
        unit="monthly_credits",
        detail=None,
        raw=payload if isinstance(payload, dict) else {"raw": payload},
    )


def _get_tavily_quota(api_key: str) -> RealQuotaResult:
    url = "https://api.tavily.com/usage"
    headers = {"Authorization": f"Bearer {api_key}"}
    params = {"api_key": api_key}

    # Try Authorization header first, then fallback to query param.
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code in (401, 403):
            resp = requests.get(url, params=params, timeout=10)
    except requests.RequestException as exc:
        return RealQuotaResult(
            provider="tavily",
            supported=True,
            ok=False,
            remaining=None,
            limit=None,
            used=None,
            unit="requests",
            detail=f"network_error: {exc}",
            raw=None,
        )

    if resp.status_code != 200:
        return RealQuotaResult(
            provider="tavily",
            supported=True,
            ok=False,
            remaining=None,
            limit=None,
            used=None,
            unit="requests",
            detail=f"http_{resp.status_code}: {resp.text[:200]}",
            raw=None,
        )

    try:
        payload = resp.json()
    except ValueError:
        return RealQuotaResult(
            provider="tavily",
            supported=True,
            ok=False,
            remaining=None,
            limit=None,
            used=None,
            unit="requests",
            detail="invalid_json",
            raw={"text": resp.text[:200]},
        )

    # Tavily response schema is not yet standardized in public docs.
    # We attempt to extract common fields but always return raw.
    remaining = _safe_int(payload.get("remaining")) if isinstance(payload, dict) else None
    limit = _safe_int(payload.get("limit")) if isinstance(payload, dict) else None
    used = _safe_int(payload.get("used")) if isinstance(payload, dict) else None

    return RealQuotaResult(
        provider="tavily",
        supported=True,
        ok=True,
        remaining=remaining,
        limit=limit,
        used=used,
        unit="requests",
        detail=None if (remaining is not None or limit is not None or used is not None) else "schema_unknown",
        raw=payload if isinstance(payload, dict) else {"raw": payload},
    )


def _get_brave_quota(api_key: str) -> RealQuotaResult:
    # Brave does not provide a dedicated quota endpoint; quota is available via headers.
    # We do a light probe (counts against quota) to read X-RateLimit-Remaining.
    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {"Accept": "application/json", "X-Subscription-Token": api_key}
    params = {"q": "health", "count": 1}
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
    except requests.RequestException as exc:
        return RealQuotaResult(
            provider="brave",
            supported=True,
            ok=False,
            remaining=None,
            limit=None,
            used=None,
            unit="requests",
            detail=f"network_error: {exc}",
            raw=None,
            probe_consumes_request=True,
        )

    remaining = None
    limit = None
    try:
        remaining_header = resp.headers.get("X-RateLimit-Remaining")
        limit_header = resp.headers.get("X-RateLimit-Limit")
        if remaining_header:
            parts = [p.strip() for p in remaining_header.split(",")]
            remaining = _safe_int(parts[-1]) if parts else None
        if limit_header:
            parts = [p.strip() for p in limit_header.split(",")]
            limit = _safe_int(parts[-1]) if parts else None
    except Exception:
        pass

    ok = resp.status_code == 200
    detail = None if ok else f"http_{resp.status_code}: {resp.text[:200]}"
    return RealQuotaResult(
        provider="brave",
        supported=True,
        ok=ok,
        remaining=remaining,
        limit=limit,
        used=None,
        unit="requests",
        detail=detail,
        raw={"headers": dict(resp.headers)},
        probe_consumes_request=True,
    )


def _get_serper_quota(api_key: str) -> RealQuotaResult:
    # Serper does not expose a documented usage endpoint.
    return RealQuotaResult(
        provider="serper",
        supported=False,
        ok=False,
        remaining=None,
        limit=None,
        used=None,
        unit="requests",
        detail="no_public_quota_endpoint",
        raw=None,
    )


def _get_duckduckgo_quota() -> RealQuotaResult:
    return RealQuotaResult(
        provider="duckduckgo",
        supported=False,
        ok=False,
        remaining=None,
        limit=None,
        used=None,
        unit=None,
        detail="no_quota_applies",
        raw=None,
    )


def get_real_quota(
    *,
    config_path: str | None = None,
    probe_brave: bool = False,
) -> dict[str, Any]:
    router = SearchRouter(config_path=config_path)
    providers_cfg = router.config.get("providers", {})
    results: list[RealQuotaResult] = []

    for name in router.order:
        cfg = providers_cfg.get(name, {})
        enabled = bool(cfg.get("enabled", True))
        if not enabled:
            results.append(
                RealQuotaResult(
                    provider=name,
                    supported=False,
                    ok=False,
                    remaining=None,
                    limit=None,
                    used=None,
                    unit=None,
                    detail="disabled",
                    raw=None,
                )
            )
            continue

        api_key = (cfg.get("api_key") or "").strip()

        if name == "tavily":
            if not api_key:
                results.append(
                    RealQuotaResult(
                        provider=name,
                        supported=True,
                        ok=False,
                        remaining=None,
                        limit=None,
                        used=None,
                        unit="requests",
                        detail="missing_api_key",
                        raw=None,
                    )
                )
                continue
            results.append(_get_tavily_quota(api_key))
        elif name == "searchapi":
            if not api_key:
                results.append(
                    RealQuotaResult(
                        provider=name,
                        supported=True,
                        ok=False,
                        remaining=None,
                        limit=None,
                        used=None,
                        unit="monthly_credits",
                        detail="missing_api_key",
                        raw=None,
                    )
                )
                continue
            results.append(_get_searchapi_quota(api_key))
        elif name == "brave":
            if not api_key:
                results.append(
                    RealQuotaResult(
                        provider=name,
                        supported=True,
                        ok=False,
                        remaining=None,
                        limit=None,
                        used=None,
                        unit="requests",
                        detail="missing_api_key",
                        raw=None,
                    )
                )
                continue
            if probe_brave:
                results.append(_get_brave_quota(api_key))
            else:
                results.append(
                    RealQuotaResult(
                        provider=name,
                        supported=True,
                        ok=False,
                        remaining=None,
                        limit=None,
                        used=None,
                        unit="requests",
                        detail="requires_probe_for_headers",
                        raw=None,
                        probe_consumes_request=True,
                    )
                )
        elif name == "serper":
            if not api_key:
                results.append(
                    RealQuotaResult(
                        provider=name,
                        supported=True,
                        ok=False,
                        remaining=None,
                        limit=None,
                        used=None,
                        unit="requests",
                        detail="missing_api_key",
                        raw=None,
                    )
                )
                continue
            results.append(_get_serper_quota(api_key))
        elif name.startswith("duckduckgo"):
            results.append(_get_duckduckgo_quota())
        elif name in ("bing_html", "mojeek", "searxng", "wikipedia"):
            results.append(
                RealQuotaResult(
                    provider=name,
                    supported=False,
                    ok=False,
                    remaining=None,
                    limit=None,
                    used=None,
                    unit=None,
                    detail="no_quota_applies",
                    raw=None,
                )
            )
        elif name in ("google_cse", "exa", "baidu", "yacy"):
            results.append(
                RealQuotaResult(
                    provider=name,
                    supported=False,
                    ok=False,
                    remaining=None,
                    limit=None,
                    used=None,
                    unit=None,
                    detail="no_public_quota_endpoint",
                    raw=None,
                )
            )
        else:
            results.append(
                RealQuotaResult(
                    provider=name,
                    supported=False,
                    ok=False,
                    remaining=None,
                    limit=None,
                    used=None,
                    unit=None,
                    detail="unsupported_provider",
                    raw=None,
                )
            )

    return {
        "timestamp": int(time.time()),
        "providers": [result.__dict__ for result in results],
    }

