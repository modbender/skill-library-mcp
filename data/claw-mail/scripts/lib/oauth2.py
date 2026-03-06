"""OAuth2 (XOAUTH2) support for IMAP and SMTP authentication.

Handles token loading, refresh, and SASL XOAUTH2 string generation
for Gmail and Outlook 365.

Config layout (per-account)::

    accounts:
      gmail:
        imap:
          host: imap.gmail.com
          port: 993
          username: user@gmail.com
          auth: oauth2
          oauth2:
            client_id: "..."
            client_secret: "..."
            refresh_token: "..."
            token_uri: "https://oauth2.googleapis.com/token"
            # Optional: cached access token
            access_token: "..."
            access_token_expiry: "2026-01-01T00:00:00"
        smtp:
          host: smtp.gmail.com
          port: 587
          username: user@gmail.com
          auth: oauth2
          oauth2:
            # Same fields, or reference the IMAP oauth2 block
            ...

Well-known token URIs:
  - Gmail:   https://oauth2.googleapis.com/token
  - Outlook: https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token
"""

from __future__ import annotations

import base64
import json
import logging
from datetime import datetime, timedelta
from typing import Any
from urllib.request import Request, urlopen
from urllib.error import URLError
from urllib.parse import urlencode

from . import credential_store

logger = logging.getLogger("clawMail.oauth2")


def build_xoauth2_string(username: str, access_token: str) -> str:
    """Build the XOAUTH2 SASL string for IMAP/SMTP AUTH.

    Format: "user=<user>\\x01auth=Bearer <token>\\x01\\x01"
    """
    auth_str = f"user={username}\x01auth=Bearer {access_token}\x01\x01"
    return auth_str


def build_xoauth2_bytes(username: str, access_token: str) -> bytes:
    """Build base64-encoded XOAUTH2 string for IMAP AUTHENTICATE."""
    raw = build_xoauth2_string(username, access_token)
    return base64.b64encode(raw.encode("ascii"))


def refresh_access_token(
    client_id: str,
    client_secret: str,
    refresh_token: str,
    token_uri: str,
    scopes: list[str] | None = None,
) -> dict[str, Any]:
    """Refresh an OAuth2 access token using a refresh token.

    Returns dict with: access_token, expires_in, token_type, and optionally scope.
    Raises RuntimeError on failure.
    """
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }
    if scopes:
        data["scope"] = " ".join(scopes)

    encoded = urlencode(data).encode("utf-8")
    req = Request(token_uri, data=encoded, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")

    try:
        with urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except (URLError, OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"OAuth2 token refresh failed: {exc}") from exc

    if "access_token" not in body:
        error = body.get("error_description", body.get("error", "unknown error"))
        raise RuntimeError(f"OAuth2 token refresh failed: {error}")

    return body


class OAuth2Manager:
    """Manage OAuth2 tokens for an account, with automatic refresh."""

    def __init__(self, oauth2_config: dict[str, Any]) -> None:
        self.client_id: str = oauth2_config.get("client_id", "")
        self.client_secret: str = credential_store.resolve(
            oauth2_config.get("client_secret", "")
        )
        self.refresh_token: str = credential_store.resolve(
            oauth2_config.get("refresh_token", "")
        )
        self.token_uri: str = oauth2_config.get("token_uri", "")
        self._access_token: str = oauth2_config.get("access_token", "")
        self._scopes: list[str] = oauth2_config.get("scopes", [])

        expiry_str = oauth2_config.get("access_token_expiry", "")
        if expiry_str:
            try:
                self._expiry = datetime.fromisoformat(expiry_str)
            except (ValueError, TypeError):
                self._expiry = datetime.min
        else:
            self._expiry = datetime.min

    @property
    def is_configured(self) -> bool:
        return bool(self.client_id and self.refresh_token and self.token_uri)

    @property
    def access_token(self) -> str:
        """Get a valid access token, refreshing if needed."""
        if self._is_expired():
            self._refresh()
        return self._access_token

    def _is_expired(self) -> bool:
        if not self._access_token:
            return True
        # Refresh 5 minutes before actual expiry
        return datetime.now() >= (self._expiry - timedelta(minutes=5))

    def _refresh(self) -> None:
        if not self.is_configured:
            raise RuntimeError(
                "OAuth2 not configured: client_id, refresh_token, "
                "and token_uri are required"
            )
        logger.info("Refreshing OAuth2 access token via %s", self.token_uri)
        result = refresh_access_token(
            client_id=self.client_id,
            client_secret=self.client_secret,
            refresh_token=self.refresh_token,
            token_uri=self.token_uri,
            scopes=self._scopes or None,
        )
        self._access_token = result["access_token"]
        expires_in = result.get("expires_in", 3600)
        self._expiry = datetime.now() + timedelta(seconds=expires_in)
        logger.info("OAuth2 token refreshed, expires in %ds", expires_in)
