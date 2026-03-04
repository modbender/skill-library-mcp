#!/usr/bin/env python3
"""Unit tests for scripts/client.py — HTTP client, auth, URL building, retry."""

import io
import json
import os
import unittest
from unittest.mock import patch, MagicMock

# Ensure token is set before importing client
os.environ.setdefault("ZEDEDA_API_TOKEN", "test-token-for-unit-tests")

from scripts.client import ZededaClient, DEFAULT_BASE_URL, MAX_RETRIES
from scripts.errors import (
    ZededaAuthError,
    ZededaError,
    ZededaNotFoundError,
    ZededaServerError,
    ZededaValidationError,
)


class TestClientInit(unittest.TestCase):
    """Client initialization and auth validation."""

    def test_init_with_explicit_token(self):
        c = ZededaClient(token="my-token")
        self.assertEqual(c.token, "my-token")
        self.assertEqual(c.base_url, DEFAULT_BASE_URL)

    def test_init_with_env_token(self):
        with patch.dict(os.environ, {"ZEDEDA_API_TOKEN": "env-tok"}):
            c = ZededaClient()
            self.assertEqual(c.token, "env-tok")

    def test_init_with_custom_base_url(self):
        c = ZededaClient(token="t", base_url="https://custom.local/api/")
        self.assertEqual(c.base_url, "https://custom.local/api")  # trailing / stripped

    def test_init_raises_without_token(self):
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("ZEDEDA_API_TOKEN", None)
            with self.assertRaises(ZededaAuthError):
                ZededaClient(token="")


class TestBuildUrl(unittest.TestCase):
    """URL construction."""

    def setUp(self):
        self.c = ZededaClient(token="tok")

    def test_simple_path(self):
        url = self.c._build_url("/v1/devices")
        self.assertEqual(url, f"{DEFAULT_BASE_URL}/v1/devices")

    def test_path_without_leading_slash(self):
        url = self.c._build_url("v1/devices")
        self.assertEqual(url, f"{DEFAULT_BASE_URL}/v1/devices")

    def test_query_params(self):
        url = self.c._build_url("/v1/devices", query={"summary": True, "pageSize": 10})
        self.assertIn("summary=True", url)
        self.assertIn("pageSize=10", url)
        self.assertIn("?", url)

    def test_none_query_values_dropped(self):
        url = self.c._build_url("/v1/devices", query={"keep": "yes", "drop": None})
        self.assertIn("keep=yes", url)
        self.assertNotIn("drop", url)

    def test_empty_query(self):
        url = self.c._build_url("/v1/devices", query={})
        self.assertNotIn("?", url)


class TestSanitise(unittest.TestCase):
    """Token redaction in log output."""

    def test_token_is_redacted(self):
        result = ZededaClient._sanitise("Bearer secret123 in url", "secret123")
        self.assertNotIn("secret123", result)
        self.assertIn("***REDACTED***", result)

    def test_empty_token_no_change(self):
        result = ZededaClient._sanitise("no token here", "")
        self.assertEqual(result, "no token here")

    def test_multiple_occurrences(self):
        result = ZededaClient._sanitise("tok tok tok", "tok")
        self.assertEqual(result.count("***REDACTED***"), 3)


class TestConvenienceWrappers(unittest.TestCase):
    """GET/POST/PUT/DELETE/PATCH delegate to request()."""

    def setUp(self):
        self.c = ZededaClient(token="tok")
        self.c.request = MagicMock(return_value={"ok": True})

    def test_get(self):
        self.c.get("/v1/devices", query={"x": 1})
        self.c.request.assert_called_once_with("GET", "/v1/devices", query={"x": 1})

    def test_post(self):
        self.c.post("/v1/devices", body={"name": "d1"})
        self.c.request.assert_called_once_with("POST", "/v1/devices", body={"name": "d1"}, query=None)

    def test_put(self):
        self.c.put("/v1/devices/id/abc", body={"a": 1})
        self.c.request.assert_called_once_with("PUT", "/v1/devices/id/abc", body={"a": 1}, query=None)

    def test_delete(self):
        self.c.delete("/v1/devices/id/abc")
        self.c.request.assert_called_once_with("DELETE", "/v1/devices/id/abc", query=None)

    def test_patch(self):
        self.c.patch("/v1/devices/id/abc", body={"b": 2})
        self.c.request.assert_called_once_with("PATCH", "/v1/devices/id/abc", body={"b": 2}, query=None)


class TestRequest(unittest.TestCase):
    """HTTP request execution, JSON parsing, and error handling."""

    def setUp(self):
        self.c = ZededaClient(token="tok")

    def _mock_urlopen(self, body: str = '{"ok":true}', status: int = 200):
        """Create a mock context manager for urllib.request.urlopen."""
        mock_resp = MagicMock()
        mock_resp.read.return_value = body.encode("utf-8")
        mock_resp.status = status
        mock_resp.__enter__ = MagicMock(return_value=mock_resp)
        mock_resp.__exit__ = MagicMock(return_value=False)
        return mock_resp

    @patch("scripts.client.urllib.request.urlopen")
    def test_successful_get(self, mock_urlopen):
        mock_urlopen.return_value = self._mock_urlopen('{"items": []}')
        result = self.c.request("GET", "/v1/devices")
        self.assertEqual(result, {"items": []})

    @patch("scripts.client.urllib.request.urlopen")
    def test_empty_response_returns_empty_dict(self, mock_urlopen):
        mock_urlopen.return_value = self._mock_urlopen("  ")
        result = self.c.request("GET", "/v1/ping")
        self.assertEqual(result, {})

    @patch("scripts.client.urllib.request.urlopen")
    def test_non_json_returns_raw(self, mock_urlopen):
        mock_urlopen.return_value = self._mock_urlopen("<html>ok</html>")
        result = self.c.request("GET", "/health")
        self.assertIn("raw", result)

    @patch("scripts.client.urllib.request.urlopen")
    def test_post_with_body(self, mock_urlopen):
        mock_urlopen.return_value = self._mock_urlopen('{"id":"new"}')
        result = self.c.request("POST", "/v1/devices", body={"name": "test"})
        self.assertEqual(result, {"id": "new"})
        call_args = mock_urlopen.call_args[0][0]
        self.assertEqual(call_args.method, "POST")
        self.assertIsNotNone(call_args.data)

    @patch("scripts.client.urllib.request.urlopen")
    def test_404_raises_not_found(self, mock_urlopen):
        import urllib.error
        err_resp = io.BytesIO(b'{"error":"not found"}')
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="http://test", code=404, msg="Not Found",
            hdrs={}, fp=err_resp
        )
        with self.assertRaises(ZededaNotFoundError):
            self.c.request("GET", "/v1/devices/id/bad")

    @patch("scripts.client.urllib.request.urlopen")
    def test_400_raises_validation(self, mock_urlopen):
        import urllib.error
        err_resp = io.BytesIO(b'{"error":"bad request"}')
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="http://test", code=400, msg="Bad Request",
            hdrs={}, fp=err_resp
        )
        with self.assertRaises(ZededaValidationError):
            self.c.request("POST", "/v1/devices", body={})

    @patch("scripts.client.urllib.request.urlopen")
    @patch("scripts.client.time.sleep")  # don't actually sleep
    def test_500_retries_then_raises(self, mock_sleep, mock_urlopen):
        import urllib.error
        err_resp = io.BytesIO(b'{"error":"internal"}')
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="http://test", code=500, msg="Internal",
            hdrs={}, fp=err_resp
        )
        with self.assertRaises(ZededaServerError):
            self.c.request("GET", "/v1/devices")
        # Should have retried MAX_RETRIES times + 1 original = MAX_RETRIES + 1 calls
        self.assertEqual(mock_urlopen.call_count, MAX_RETRIES + 1)

    @patch("scripts.client.urllib.request.urlopen")
    @patch("scripts.client.time.sleep")
    def test_429_retries(self, mock_sleep, mock_urlopen):
        import urllib.error
        # First two calls fail with 429, then succeed
        err_resp1 = io.BytesIO(b'{"error":"rate limit"}')
        err_resp2 = io.BytesIO(b'{"error":"rate limit"}')
        mock_urlopen.side_effect = [
            urllib.error.HTTPError(url="", code=429, msg="Rate Limit", hdrs={}, fp=err_resp1),
            urllib.error.HTTPError(url="", code=429, msg="Rate Limit", hdrs={}, fp=err_resp2),
            self._mock_urlopen('{"ok":true}'),
        ]
        result = self.c.request("GET", "/v1/devices")
        self.assertEqual(result, {"ok": True})
        self.assertEqual(mock_urlopen.call_count, 3)

    @patch("scripts.client.urllib.request.urlopen")
    def test_auth_header_included(self, mock_urlopen):
        mock_urlopen.return_value = self._mock_urlopen("{}")
        self.c.request("GET", "/v1/devices")
        req_obj = mock_urlopen.call_args[0][0]
        self.assertEqual(req_obj.get_header("Authorization"), "Bearer tok")

    @patch("scripts.client.urllib.request.urlopen")
    def test_generic_exception_raises_zededa_error(self, mock_urlopen):
        mock_urlopen.side_effect = ConnectionError("connection reset")
        with self.assertRaises(ZededaError):
            self.c.request("GET", "/v1/devices")


if __name__ == "__main__":
    unittest.main()
