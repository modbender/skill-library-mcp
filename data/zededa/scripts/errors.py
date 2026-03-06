#!/usr/bin/env python3
"""
ZEDEDA API Custom Error Hierarchy

Provides structured error types for every service domain, enabling precise
error handling, detailed logging, and actionable troubleshooting context.
"""

import datetime


# ---------------------------------------------------------------------------
# Base Error Classes
# ---------------------------------------------------------------------------

class ZededaError(Exception):
    """Base exception for all ZEDEDA API errors."""

    def __init__(self, message: str, *, endpoint: str = "", method: str = "",
                 status_code: int = 0, response_body: str = "",
                 request_params: dict | None = None):
        self.endpoint = endpoint
        self.method = method
        self.status_code = status_code
        self.response_body = response_body
        self.request_params = request_params or {}
        self.timestamp = datetime.datetime.utcnow().isoformat() + "Z"
        super().__init__(message)

    def to_dict(self) -> dict:
        return {
            "error_type": self.__class__.__name__,
            "message": str(self),
            "endpoint": self.endpoint,
            "method": self.method,
            "status_code": self.status_code,
            "timestamp": self.timestamp,
        }


class ZededaAuthError(ZededaError):
    """Authentication or authorization failure (401/403)."""


class ZededaValidationError(ZededaError):
    """Request validation failure (400)."""


class ZededaNotFoundError(ZededaError):
    """Requested resource not found (404)."""


class ZededaConflictError(ZededaError):
    """Resource conflict (409)."""


class ZededaRateLimitError(ZededaError):
    """API rate limit exceeded (429)."""


class ZededaServerError(ZededaError):
    """Server-side error (5xx)."""


# ---------------------------------------------------------------------------
# Per-Service Error Classes
# ---------------------------------------------------------------------------

class NodeServiceError(ZededaError):
    """Error originating from the Edge Node Service."""


class NodeClusterServiceError(ZededaError):
    """Error originating from the Edge Node Cluster Service."""


class AppServiceError(ZededaError):
    """Error originating from the Edge Application Service."""


class AppProfileServiceError(ZededaError):
    """Error originating from the App Profile / Policy Service."""


class StorageServiceError(ZededaError):
    """Error originating from the Storage Service."""


class NetworkServiceError(ZededaError):
    """Error originating from the Network Service."""


class OrchestrationServiceError(ZededaError):
    """Error originating from the Orchestration Service."""


class KubernetesServiceError(ZededaError):
    """Error originating from the Kubernetes Service."""


class DiagServiceError(ZededaError):
    """Error originating from the Diagnostics Service."""


class JobServiceError(ZededaError):
    """Error originating from the Job / Bulk Operations Service."""


class UserServiceError(ZededaError):
    """Error originating from the User / IAM Service."""


# ---------------------------------------------------------------------------
# Mapping helpers
# ---------------------------------------------------------------------------

STATUS_ERROR_MAP: dict[int, type[ZededaError]] = {
    400: ZededaValidationError,
    401: ZededaAuthError,
    403: ZededaAuthError,
    404: ZededaNotFoundError,
    409: ZededaConflictError,
    429: ZededaRateLimitError,
}


def error_for_status(status_code: int, **kwargs) -> ZededaError:
    """Return the most specific error class for a given HTTP status code."""
    if status_code >= 500:
        return ZededaServerError(**kwargs)
    cls = STATUS_ERROR_MAP.get(status_code, ZededaError)
    return cls(**kwargs)
