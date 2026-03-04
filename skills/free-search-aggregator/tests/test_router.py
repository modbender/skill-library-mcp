from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml

from free_search.providers import SearchItem
from free_search.router import QuotaState, SearchRouter, SearchRouterError


class _EmptyProvider:
    def __init__(self, *, config: dict):
        self._enabled = bool(config.get("enabled", True))

    def is_enabled(self) -> bool:
        return self._enabled

    def search(self, query: str, *, max_results: int):
        return []


class _OkProvider:
    def __init__(self, *, config: dict):
        self._enabled = bool(config.get("enabled", True))

    def is_enabled(self) -> bool:
        return self._enabled

    def search(self, query: str, *, max_results: int):
        return [
            SearchItem(
                title="Result",
                url="https://example.com",
                snippet="ok",
                source="second",
                rank=1,
            )
        ]


class _DisabledProvider:
    def __init__(self, *, config: dict):
        self._enabled = False

    def is_enabled(self) -> bool:
        return self._enabled

    def search(self, query: str, *, max_results: int):
        return []

class _CrashProvider:
    def __init__(self, *, config: dict):
        self._enabled = bool(config.get("enabled", True))

    def is_enabled(self) -> bool:
        return self._enabled

    def search(self, query: str, *, max_results: int):
        raise RuntimeError("boom")


class TestRouter(unittest.TestCase):
    def _write_config(self, base: Path) -> Path:
        cfg = {
            "router": {
                "provider_order": ["first", "second", "third"],
                "quota_state_file": ".quota_state.json",
            },
            "providers": {
                "first": {"enabled": True, "daily_quota": 10},
                "second": {"enabled": True, "daily_quota": 10},
                "third": {"enabled": True, "daily_quota": 10},
            },
        }
        path = base / "providers.yaml"
        path.write_text(yaml.safe_dump(cfg), encoding="utf-8")
        return path

    def test_failover_when_first_provider_returns_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cfg_path = self._write_config(Path(tmp))
            registry = {"first": _EmptyProvider, "second": _OkProvider, "third": _DisabledProvider}
            with patch("free_search.router.PROVIDER_REGISTRY", registry):
                router = SearchRouter(config_path=str(cfg_path))
                payload = router.search("milan events", max_results=5)

        self.assertEqual(payload["provider"], "second")
        self.assertEqual(len(payload["results"]), 1)
        attempts = payload["meta"]["attempted"]
        self.assertEqual(attempts[0]["provider"], "first")
        self.assertEqual(attempts[0]["reason"], "empty_results")
        self.assertEqual(attempts[1]["provider"], "second")
        self.assertEqual(attempts[1]["status"], "ok")

    def test_raises_when_all_providers_exhausted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cfg_path = self._write_config(Path(tmp))
            registry = {"first": _EmptyProvider, "second": _EmptyProvider, "third": _DisabledProvider}
            with patch("free_search.router.PROVIDER_REGISTRY", registry):
                router = SearchRouter(config_path=str(cfg_path))
                with self.assertRaises(SearchRouterError):
                    router.search("milan events", max_results=5)

    def test_max_results_validation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cfg_path = self._write_config(Path(tmp))
            registry = {"first": _OkProvider, "second": _OkProvider, "third": _OkProvider}
            with patch("free_search.router.PROVIDER_REGISTRY", registry):
                router = SearchRouter(config_path=str(cfg_path))
                with self.assertRaises(ValueError):
                    router.search("x", max_results=0)

    def test_expand_env_unresolved_placeholder(self) -> None:
        self.assertEqual(SearchRouter._expand_env("${MISSING_TOKEN}"), "")

    def test_unexpected_provider_exception_fails_over(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cfg_path = self._write_config(Path(tmp))
            registry = {"first": _CrashProvider, "second": _OkProvider, "third": _DisabledProvider}
            with patch("free_search.router.PROVIDER_REGISTRY", registry):
                router = SearchRouter(config_path=str(cfg_path))
                payload = router.search("milan events", max_results=5)

        self.assertEqual(payload["provider"], "second")
        attempts = payload["meta"]["attempted"]
        self.assertEqual(attempts[0]["provider"], "first")
        self.assertEqual(attempts[0]["reason"], "unexpected_error")

    def test_quota_status_contains_expected_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cfg_path = self._write_config(Path(tmp))
            registry = {"first": _OkProvider, "second": _OkProvider, "third": _OkProvider}
            with patch("free_search.router.PROVIDER_REGISTRY", registry):
                router = SearchRouter(config_path=str(cfg_path))
                router.quota.increment("first")
                router.quota.save()
                status = router.quota_status()

        self.assertIn("date", status)
        providers = status["providers"]
        self.assertEqual(providers[0]["provider"], "first")
        self.assertEqual(providers[0]["used_today"], 1)
        self.assertEqual(providers[0]["remaining"], 9)
        self.assertEqual(providers[0]["daily_quota"], 10)
        self.assertEqual(providers[0]["percentage_used"], 10.0)

    def test_reset_quota_clears_all_provider_usage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cfg_path = self._write_config(Path(tmp))
            registry = {"first": _OkProvider, "second": _OkProvider, "third": _OkProvider}
            with patch("free_search.router.PROVIDER_REGISTRY", registry):
                router = SearchRouter(config_path=str(cfg_path))
                router.quota.increment("first")
                router.quota.increment("second")
                router.quota.save()
                router.reset_quota()

                reloaded = SearchRouter(config_path=str(cfg_path))
                reloaded_status = reloaded.quota_status()

        self.assertEqual(reloaded_status["providers"][0]["used_today"], 0)
        self.assertEqual(reloaded_status["providers"][1]["used_today"], 0)


class TestQuotaState(unittest.TestCase):
    def test_old_date_state_is_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            state_path = Path(tmp) / "state.json"
            state_path.write_text(
                json.dumps(
                    {
                        "date": "1999-01-01",
                        "providers": {"duckduckgo": {"requests": 99}},
                    }
                ),
                encoding="utf-8",
            )
            quota = QuotaState(state_path)
            self.assertEqual(quota.get_count("duckduckgo"), 0)


if __name__ == "__main__":
    unittest.main()
