"""Bearer token authentication middleware."""

from __future__ import annotations

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

_bearer = HTTPBearer()

# Will be set at startup from config
_valid_token: str = ""


def set_token(token: str) -> None:
    global _valid_token
    _valid_token = token


async def require_token(
    creds: HTTPAuthorizationCredentials = Security(_bearer),
) -> str:
    """Dependency — rejects requests without a valid bearer token."""
    if creds.credentials != _valid_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing bearer token",
        )
    return creds.credentials
