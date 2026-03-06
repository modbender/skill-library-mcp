#!/usr/bin/env python3
"""
OAuth Handler — manages OAuth tokens for social platforms.

Stores tokens in ~/.nanobot/oauth_tokens.json.
Uses the system keyring for encryption when available, falls back to
plaintext with a warning.

Importable as a module or runnable as CLI:
    python3 oauth_handler.py status --platform twitter --json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import urlencode

TOKEN_DIR = Path.home() / ".nanobot"
TOKEN_FILE = TOKEN_DIR / "oauth_tokens.json"

SUPPORTED_PLATFORMS = ("twitter", "linkedin", "facebook", "instagram")

PLATFORM_ENDPOINTS: Dict[str, Dict[str, str]] = {
    "twitter": {
        "authorize_url": "https://twitter.com/i/oauth2/authorize",
        "token_url": "https://api.twitter.com/2/oauth2/token",
        "scopes": "tweet.read tweet.write users.read offline.access",
    },
    "linkedin": {
        "authorize_url": "https://www.linkedin.com/oauth/v2/authorization",
        "token_url": "https://www.linkedin.com/oauth/v2/accessToken",
        "scopes": "r_liteprofile w_member_social",
    },
    "facebook": {
        "authorize_url": "https://www.facebook.com/v18.0/dialog/oauth",
        "token_url": "https://graph.facebook.com/v18.0/oauth/access_token",
        "scopes": "pages_manage_posts pages_read_engagement",
    },
    "instagram": {
        "authorize_url": "https://api.instagram.com/oauth/authorize",
        "token_url": "https://api.instagram.com/oauth/access_token",
        "scopes": "user_profile user_media",
    },
}


def _try_keyring():
    """Return the keyring module if available, else None."""
    try:
        import keyring  # type: ignore[import-untyped]
        return keyring
    except ImportError:
        return None


class OAuthHandler:
    """Manage OAuth tokens for social platforms."""

    def __init__(self, token_file: Optional[Path] = None):
        self.token_file = token_file or TOKEN_FILE
        self.token_file.parent.mkdir(parents=True, exist_ok=True)
        self._keyring = _try_keyring()
        self._tokens: Dict[str, Any] = self._load_tokens()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _load_tokens(self) -> Dict[str, Any]:
        if self._keyring:
            raw = self._keyring.get_password("openclaw_oauth", "tokens")
            if raw:
                try:
                    return json.loads(raw)
                except json.JSONDecodeError:
                    pass
        if self.token_file.exists():
            try:
                return json.loads(self.token_file.read_text())
            except json.JSONDecodeError:
                pass
        return {}

    def _save_tokens(self) -> None:
        payload = json.dumps(self._tokens, indent=2)
        if self._keyring:
            self._keyring.set_password("openclaw_oauth", "tokens", payload)
        else:
            self.token_file.write_text(payload)
            self.token_file.chmod(0o600)
            print(
                "WARNING: keyring not available — tokens stored as plaintext in "
                f"{self.token_file}",
                file=sys.stderr,
            )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_token(self, platform: str) -> Optional[Dict[str, Any]]:
        """Return the stored token data for *platform*, or None."""
        return self._tokens.get(platform)

    def store_token(self, platform: str, token_data: Dict[str, Any]) -> None:
        """Persist *token_data* for *platform*."""
        token_data["stored_at"] = time.time()
        self._tokens[platform] = token_data
        self._save_tokens()

    def refresh_token(self, platform: str) -> Dict[str, Any]:
        """Attempt to refresh an expired token.

        Returns the new token data on success, or an error dict.
        """
        existing = self.get_token(platform)
        if not existing or "refresh_token" not in existing:
            return {"ok": False, "error": "No refresh token available"}

        endpoint = PLATFORM_ENDPOINTS.get(platform, {})
        if not endpoint:
            return {"ok": False, "error": f"Unsupported platform: {platform}"}

        try:
            import urllib.request

            data = urlencode({
                "grant_type": "refresh_token",
                "refresh_token": existing["refresh_token"],
                "client_id": existing.get("client_id", ""),
            }).encode()

            req = urllib.request.Request(
                endpoint["token_url"],
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                new_token = json.loads(resp.read().decode())

            new_token["client_id"] = existing.get("client_id", "")
            if "refresh_token" not in new_token:
                new_token["refresh_token"] = existing["refresh_token"]
            self.store_token(platform, new_token)
            return {"ok": True, "token": new_token}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    def is_authenticated(self, platform: str) -> bool:
        """Return True if a non-expired token exists for *platform*."""
        token = self.get_token(platform)
        if not token or "access_token" not in token:
            return False
        expires_at = token.get("expires_at")
        if expires_at and time.time() > expires_at:
            return False
        expires_in = token.get("expires_in")
        stored_at = token.get("stored_at", 0)
        if expires_in and stored_at and time.time() > stored_at + expires_in:
            return False
        return True

    def initiate_flow(
        self, platform: str, callback_url: str, client_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Start an OAuth flow.  Returns the authorization URL to open."""
        endpoint = PLATFORM_ENDPOINTS.get(platform)
        if not endpoint:
            return {"ok": False, "error": f"Unsupported platform: {platform}"}

        cid = client_id or os.environ.get(f"{platform.upper()}_CLIENT_ID", "")
        if not cid:
            return {
                "ok": False,
                "error": f"No client_id — set {platform.upper()}_CLIENT_ID env var",
            }

        params = {
            "response_type": "code",
            "client_id": cid,
            "redirect_uri": callback_url,
            "scope": endpoint["scopes"],
            "state": f"openclaw_{platform}_{int(time.time())}",
        }

        if platform == "twitter":
            params["code_challenge"] = "challenge"
            params["code_challenge_method"] = "plain"

        auth_url = f"{endpoint['authorize_url']}?{urlencode(params)}"
        return {"ok": True, "auth_url": auth_url, "state": params["state"]}

    def complete_flow(
        self,
        platform: str,
        auth_code: str,
        callback_url: str = "",
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Exchange an authorization code for tokens."""
        endpoint = PLATFORM_ENDPOINTS.get(platform)
        if not endpoint:
            return {"ok": False, "error": f"Unsupported platform: {platform}"}

        cid = client_id or os.environ.get(f"{platform.upper()}_CLIENT_ID", "")
        secret = client_secret or os.environ.get(f"{platform.upper()}_CLIENT_SECRET", "")

        try:
            import urllib.request

            data = urlencode({
                "grant_type": "authorization_code",
                "code": auth_code,
                "redirect_uri": callback_url,
                "client_id": cid,
                "client_secret": secret,
            }).encode()

            if platform == "twitter":
                data = urlencode({
                    "grant_type": "authorization_code",
                    "code": auth_code,
                    "redirect_uri": callback_url,
                    "client_id": cid,
                    "code_verifier": "challenge",
                }).encode()

            req = urllib.request.Request(
                endpoint["token_url"],
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                token_data = json.loads(resp.read().decode())

            token_data["client_id"] = cid
            if "expires_in" in token_data:
                token_data["expires_at"] = time.time() + token_data["expires_in"]
            self.store_token(platform, token_data)
            return {"ok": True, "token": token_data}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

    def status(self, platform: Optional[str] = None) -> Dict[str, Any]:
        """Return authentication status for one or all platforms."""
        platforms = [platform] if platform else list(SUPPORTED_PLATFORMS)
        result: Dict[str, Any] = {}
        for p in platforms:
            token = self.get_token(p)
            result[p] = {
                "authenticated": self.is_authenticated(p),
                "has_token": token is not None,
                "has_refresh": bool(token and "refresh_token" in token) if token else False,
                "stored_at": token.get("stored_at") if token else None,
            }
        return {"ok": True, "platforms": result}


# ======================================================================
# CLI
# ======================================================================

def main() -> None:
    parser = argparse.ArgumentParser(description="OAuth Handler for social platforms")
    sub = parser.add_subparsers(dest="command", required=True)

    # status
    st = sub.add_parser("status", help="Check authentication status")
    st.add_argument("--platform", choices=SUPPORTED_PLATFORMS)
    st.add_argument("--json", action="store_true", dest="json_out")

    # initiate
    init = sub.add_parser("initiate", help="Start OAuth flow")
    init.add_argument("--platform", required=True, choices=SUPPORTED_PLATFORMS)
    init.add_argument("--callback-url", required=True)
    init.add_argument("--client-id")
    init.add_argument("--json", action="store_true", dest="json_out")

    # complete
    comp = sub.add_parser("complete", help="Complete OAuth flow with auth code")
    comp.add_argument("--platform", required=True, choices=SUPPORTED_PLATFORMS)
    comp.add_argument("--code", required=True)
    comp.add_argument("--callback-url", default="")
    comp.add_argument("--client-id")
    comp.add_argument("--client-secret")
    comp.add_argument("--json", action="store_true", dest="json_out")

    # refresh
    ref = sub.add_parser("refresh", help="Refresh an expired token")
    ref.add_argument("--platform", required=True, choices=SUPPORTED_PLATFORMS)
    ref.add_argument("--json", action="store_true", dest="json_out")

    args = parser.parse_args()
    handler = OAuthHandler()

    if args.command == "status":
        result = handler.status(args.platform)
    elif args.command == "initiate":
        result = handler.initiate_flow(
            args.platform, args.callback_url, client_id=args.client_id
        )
    elif args.command == "complete":
        result = handler.complete_flow(
            args.platform,
            args.code,
            callback_url=args.callback_url,
            client_id=args.client_id,
            client_secret=args.client_secret,
        )
    elif args.command == "refresh":
        result = handler.refresh_token(args.platform)
    else:
        result = {"ok": False, "error": f"Unknown command: {args.command}"}

    if getattr(args, "json_out", False):
        json.dump(result, sys.stdout, indent=2)
        print()
    else:
        for key, val in result.items():
            print(f"{key}: {val}")

    sys.exit(0 if result.get("ok", True) else 1)


if __name__ == "__main__":
    main()
