"""Free Search Aggregator public API.

Usage:
    from free_search import search
    data = search("latest ai benchmarks", max_results=5)
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from .router import SearchRouter, SearchRouterError
from .task_search import task_search
from .quota_real import get_real_quota


def configure_logging(level: str = "INFO") -> None:
    """Configure package-level logging for consumers that do not set handlers."""
    numeric = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric,
        format="%(asctime)s %(levelname)s %(name)s :: %(message)s",
    )


def search(
    query: str,
    *,
    max_results: int = 8,
    config_path: str | None = None,
) -> dict[str, Any]:
    """Run a search with automatic provider failover.

    Args:
        query: Search query.
        max_results: Maximum results to return.
        config_path: Optional explicit path to providers.yaml.

    Returns:
        Dictionary with unified `results` and `meta` fields.
    """
    if not query or not query.strip():
        raise ValueError("query must be non-empty")
    if max_results <= 0:
        raise ValueError("max_results must be > 0")

    router = SearchRouter(config_path=config_path)
    return router.search(query.strip(), max_results=max_results)

def get_quota_status(*, config_path: str | None = None) -> dict[str, Any]:
    """Return per-provider daily quota usage without running a search."""
    router = SearchRouter(config_path=config_path)
    return router.quota_status()


def reset_quota(*, config_path: str | None = None, provider: str | None = None) -> dict[str, Any]:
    """Reset daily quota usage (all providers or a single provider)."""
    router = SearchRouter(config_path=config_path)
    return router.reset_quota(provider=provider)


__all__ = [
    "search",
    "task_search",
    "get_real_quota",
    "get_quota_status",
    "reset_quota",
    "configure_logging",
    "SearchRouter",
    "SearchRouterError",
]


def _default_config_path() -> Path:
    return Path(__file__).resolve().parents[2] / "config" / "providers.yaml"
