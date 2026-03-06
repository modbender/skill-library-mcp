#!/usr/bin/env python3
"""
jwt_utils.py - HS256 JWT generation for Ghost Admin API auth.
Shared between ghost.py and setup.py. Stdlib only (no PyJWT).
"""

import base64
import hashlib
import hmac
import json
import time


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def make_jwt(key_id: str, secret_hex: str) -> str:
    """Generate a short-lived HS256 JWT for Ghost Admin API auth."""
    now = int(time.time())
    header  = {"alg": "HS256", "typ": "JWT", "kid": key_id}
    payload = {"iat": now, "exp": now + 300, "aud": "/admin/"}
    h = _b64url(json.dumps(header,  separators=(",", ":")).encode())
    p = _b64url(json.dumps(payload, separators=(",", ":")).encode())
    msg    = f"{h}.{p}".encode()
    secret = bytes.fromhex(secret_hex)
    sig    = hmac.new(secret, msg, hashlib.sha256).digest()
    return f"{h}.{p}.{_b64url(sig)}"
