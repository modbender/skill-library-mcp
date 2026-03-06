from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch

from free_search.__main__ import main
from free_search.router import SearchRouterError


class TestCLI(unittest.TestCase):
    def test_success_exit_zero_and_json_output(self) -> None:
        payload = {
            "query": "milan events",
            "provider": "duckduckgo",
            "results": [],
            "meta": {},
        }
        with patch("free_search.__main__.search", return_value=payload):
            out = io.StringIO()
            with redirect_stdout(out):
                code = main(["milan", "events"])

        self.assertEqual(code, 0)
        data = json.loads(out.getvalue())
        self.assertEqual(data["provider"], "duckduckgo")

    def test_brave_search_compat_mode(self) -> None:
        payload = {
            "query": "milan events",
            "provider": "brave",
            "results": [],
            "meta": {},
        }
        with patch("free_search.__main__.search", return_value=payload) as mock_search:
            out = io.StringIO()
            with redirect_stdout(out):
                code = main(["brave", "search", "milan", "events", "--compact"])

        self.assertEqual(code, 0)
        mock_search.assert_called_once_with("milan events", max_results=8, config_path=None)
        self.assertEqual(out.getvalue().strip(), json.dumps(payload, ensure_ascii=False))

    def test_router_error_exit_two(self) -> None:
        with patch("free_search.__main__.search", side_effect=SearchRouterError("all failed")):
            err = io.StringIO()
            with redirect_stderr(err):
                code = main(["milan", "events"])
        self.assertEqual(code, 2)
        self.assertIn("all failed", err.getvalue())

    def test_status_shows_quota_without_search(self) -> None:
        payload = {
            "date": "2026-02-24",
            "providers": [
                {
                    "provider": "duckduckgo",
                    "used_today": 2,
                    "remaining": 998,
                    "daily_quota": 1000,
                    "percentage_used": 0.2,
                }
            ],
        }
        with patch("free_search.__main__.get_quota_status", return_value=payload) as mock_status:
            with patch("free_search.__main__.search") as mock_search:
                out = io.StringIO()
                with redirect_stdout(out):
                    code = main(["status", "--compact"])

        self.assertEqual(code, 0)
        mock_status.assert_called_once_with(config_path=None)
        mock_search.assert_not_called()
        self.assertEqual(out.getvalue().strip(), json.dumps(payload, ensure_ascii=False))

    def test_status_reset_calls_reset_quota(self) -> None:
        payload = {"date": "2026-02-24", "providers": []}
        with patch("free_search.__main__.reset_quota", return_value=payload) as mock_reset:
            out = io.StringIO()
            with redirect_stdout(out):
                code = main(["status", "--reset"])

        self.assertEqual(code, 0)
        mock_reset.assert_called_once_with(config_path=None)
        data = json.loads(out.getvalue())
        self.assertEqual(data["providers"], [])


if __name__ == "__main__":
    unittest.main()
