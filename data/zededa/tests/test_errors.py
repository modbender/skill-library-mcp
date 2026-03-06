#!/usr/bin/env python3
"""Unit tests for scripts/errors.py — error hierarchy and status mapping."""

import unittest

from scripts.errors import (
    ZededaError,
    ZededaAuthError,
    ZededaValidationError,
    ZededaNotFoundError,
    ZededaConflictError,
    ZededaRateLimitError,
    ZededaServerError,
    NodeServiceError,
    NodeClusterServiceError,
    AppServiceError,
    AppProfileServiceError,
    StorageServiceError,
    NetworkServiceError,
    OrchestrationServiceError,
    KubernetesServiceError,
    DiagServiceError,
    JobServiceError,
    UserServiceError,
    error_for_status,
    STATUS_ERROR_MAP,
)


class TestErrorHierarchy(unittest.TestCase):
    """All custom errors descend from ZededaError."""

    def test_base_error_is_exception(self):
        self.assertTrue(issubclass(ZededaError, Exception))

    def test_http_errors_inherit_base(self):
        for cls in (ZededaAuthError, ZededaValidationError,
                    ZededaNotFoundError, ZededaConflictError,
                    ZededaRateLimitError, ZededaServerError):
            with self.subTest(cls=cls.__name__):
                self.assertTrue(issubclass(cls, ZededaError))

    def test_service_errors_inherit_base(self):
        service_errors = (
            NodeServiceError, NodeClusterServiceError, AppServiceError,
            AppProfileServiceError, StorageServiceError, NetworkServiceError,
            OrchestrationServiceError, KubernetesServiceError,
            DiagServiceError, JobServiceError, UserServiceError,
        )
        for cls in service_errors:
            with self.subTest(cls=cls.__name__):
                self.assertTrue(issubclass(cls, ZededaError))


class TestZededaErrorFields(unittest.TestCase):
    """ZededaError captures rich context."""

    def test_fields_are_stored(self):
        err = ZededaError(
            "something failed",
            endpoint="/v1/devices",
            method="GET",
            status_code=500,
            response_body='{"error":"bad"}',
            request_params={"id": "abc"},
        )
        self.assertEqual(str(err), "something failed")
        self.assertEqual(err.endpoint, "/v1/devices")
        self.assertEqual(err.method, "GET")
        self.assertEqual(err.status_code, 500)
        self.assertEqual(err.response_body, '{"error":"bad"}')
        self.assertEqual(err.request_params, {"id": "abc"})
        self.assertIn("Z", err.timestamp)

    def test_to_dict(self):
        err = ZededaError("msg", endpoint="/v1/foo", method="POST", status_code=400)
        d = err.to_dict()
        self.assertEqual(d["error_type"], "ZededaError")
        self.assertEqual(d["message"], "msg")
        self.assertEqual(d["endpoint"], "/v1/foo")
        self.assertEqual(d["method"], "POST")
        self.assertEqual(d["status_code"], 400)
        self.assertIn("timestamp", d)

    def test_defaults(self):
        err = ZededaError("x")
        self.assertEqual(err.endpoint, "")
        self.assertEqual(err.method, "")
        self.assertEqual(err.status_code, 0)
        self.assertEqual(err.response_body, "")
        self.assertEqual(err.request_params, {})


class TestErrorForStatus(unittest.TestCase):
    """error_for_status maps HTTP codes to error classes."""

    def test_400_validation(self):
        err = error_for_status(400, message="bad request")
        self.assertIsInstance(err, ZededaValidationError)

    def test_401_auth(self):
        err = error_for_status(401, message="unauthorized")
        self.assertIsInstance(err, ZededaAuthError)

    def test_403_auth(self):
        err = error_for_status(403, message="forbidden")
        self.assertIsInstance(err, ZededaAuthError)

    def test_404_not_found(self):
        err = error_for_status(404, message="not found")
        self.assertIsInstance(err, ZededaNotFoundError)

    def test_409_conflict(self):
        err = error_for_status(409, message="conflict")
        self.assertIsInstance(err, ZededaConflictError)

    def test_429_rate_limit(self):
        err = error_for_status(429, message="rate limit")
        self.assertIsInstance(err, ZededaRateLimitError)

    def test_500_server(self):
        err = error_for_status(500, message="server error")
        self.assertIsInstance(err, ZededaServerError)

    def test_502_server(self):
        err = error_for_status(502, message="bad gateway")
        self.assertIsInstance(err, ZededaServerError)

    def test_503_server(self):
        err = error_for_status(503, message="unavailable")
        self.assertIsInstance(err, ZededaServerError)

    def test_unknown_code_falls_back_to_base(self):
        err = error_for_status(418, message="teapot")
        self.assertIsInstance(err, ZededaError)
        self.assertNotIsInstance(err, ZededaServerError)

    def test_status_error_map_keys(self):
        self.assertIn(400, STATUS_ERROR_MAP)
        self.assertIn(401, STATUS_ERROR_MAP)
        self.assertIn(403, STATUS_ERROR_MAP)
        self.assertIn(404, STATUS_ERROR_MAP)
        self.assertIn(409, STATUS_ERROR_MAP)
        self.assertIn(429, STATUS_ERROR_MAP)


if __name__ == "__main__":
    unittest.main()
