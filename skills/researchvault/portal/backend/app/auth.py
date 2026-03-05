from __future__ import annotations

import base64
import hashlib
import hmac
import os
import time
from dataclasses import dataclass
from typing import Optional
import json

from fastapi import Cookie, HTTPException, status


SESSION_COOKIE_NAME = "rv_session"
SESSION_TTL_S = 12 * 60 * 60  # 12h


@dataclass
class Session:
    created_at: float


def _expected_token() -> str:
    expected = os.getenv("RESEARCHVAULT_PORTAL_TOKEN")
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Portal token not configured (set RESEARCHVAULT_PORTAL_TOKEN; start_portal.sh exports it from .portal_auth).",
        )
    return expected


def _b64url_encode(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode("ascii")


def _b64url_decode(s: str) -> bytes:
    pad = "=" * ((4 - (len(s) % 4)) % 4)
    return base64.urlsafe_b64decode((s + pad).encode("ascii"))


def _sign(payload_b64: str, secret: str) -> str:
    sig = hmac.new(secret.encode("utf-8"), payload_b64.encode("utf-8"), hashlib.sha256).digest()
    return _b64url_encode(sig)


def _issue_session(secret: str) -> str:
    now = int(time.time())
    payload = {"v": 1, "iat": now, "exp": now + int(SESSION_TTL_S)}
    payload_b64 = _b64url_encode(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8"))
    return f"{payload_b64}.{_sign(payload_b64, secret)}"


def _verify_session(token: str, secret: str) -> Session:
    if not token or "." not in token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    payload_b64, sig = token.split(".", 1)
    expected_sig = _sign(payload_b64, secret)
    if not hmac.compare_digest(sig, expected_sig):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    try:
        raw = _b64url_decode(payload_b64)
        payload = json.loads(raw.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    exp = payload.get("exp")
    iat = payload.get("iat")
    if not isinstance(exp, int) or not isinstance(iat, int):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    now = int(time.time())
    if now >= exp:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")

    return Session(created_at=float(iat))


def create_session(provided_token: str) -> str:
    expected = _expected_token()
    if not provided_token or not hmac.compare_digest(provided_token, expected):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return _issue_session(expected)


def revoke_session(session_id: str) -> None:
    # Stateless sessions: logout is handled by clearing the cookie on the client.
    # (We intentionally do not maintain a server-side denylist for this local app.)
    return None


def require_session(rv_session: Optional[str] = Cookie(default=None, alias=SESSION_COOKIE_NAME)) -> None:
    if not rv_session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    _verify_session(rv_session, _expected_token())
