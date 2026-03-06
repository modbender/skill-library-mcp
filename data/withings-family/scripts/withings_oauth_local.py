#!/usr/bin/env python3
"""Withings OAuth helper with local callback server.

Automatically captures the OAuth code via a local HTTP server on localhost:8080.
"""

from __future__ import annotations

import argparse
import json
import os
import secrets
import sys
import time
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Optional, Tuple
import re

def _base_dir() -> Path:
    new = Path.home() / ".openclaw" / "withings-family"
    legacy = Path.home() / ".moltbot" / "withings-family"
    return legacy if legacy.exists() and not new.exists() else new

BASE_DIR = _base_dir()

# Auth: set WITHINGS_CLIENT_ID / WITHINGS_CLIENT_SECRET in environment,
# or put them in workspace/withings-family/config.json.
def _load_config_json() -> dict:
    cfg_path = BASE_DIR / 'config.json'
    if cfg_path.exists():
        import json as _json
        try:
            return _json.loads(cfg_path.read_text())
        except Exception:
            pass
    return {}

_cfg = _load_config_json()
CLIENT_ID = os.environ.get('WITHINGS_CLIENT_ID') or _cfg.get('client_id')
CLIENT_SECRET = os.environ.get('WITHINGS_CLIENT_SECRET') or _cfg.get('client_secret')
REDIRECT_URI = 'http://localhost:18081'

AUTHORIZE_URL = "https://account.withings.com/oauth2_user/authorize2"
TOKEN_URL = "https://wbsapi.withings.net/v2/oauth2"


def _sanitize_user_id(user_id: str) -> str:
    uid = (user_id or "default").strip()
    if uid == "":
        uid = "default"
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", uid):
        raise ValueError(
            f"Invalid user_id '{user_id}'. Allowed: letters/digits plus . _ - (max 64 chars)."
        )
    return uid


def get_token_file(user_id: str = 'default') -> Path:
    """Get token file path for a user."""
    uid = _sanitize_user_id(user_id)
    return BASE_DIR / f'tokens-{uid}.json'


def save_tokens(data: dict, user_id: str = 'default') -> dict:
    """Save tokens with expiry calculation."""
    expiry = time.time() + data['expires_in']
    payload = {**data, 'expiry_date': expiry}
    token_file = get_token_file(user_id)
    token_file.write_text(json.dumps(payload, indent=2))
    # Secure permissions
    try:
        os.chmod(token_file, 0o600)
    except Exception:
        pass
    return payload


def post_request(endpoint: str, params: dict) -> dict:
    """Make a POST request to Withings API."""
    data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(
        f'https://wbsapi.withings.net{endpoint}',
        data=data,
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read())
        if result['status'] != 0:
            raise Exception(f"API Error: {result['status']} - {result}")
        return result.get('body', result)


def build_authorize_url(*, client_id: str, redirect_uri: str, scope: str, state: str) -> str:
    q = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': scope,
        'state': state,
    }
    return AUTHORIZE_URL + "?" + urllib.parse.urlencode(q)


class _CallbackHandler(BaseHTTPRequestHandler):
    server_version = "withings-oauth-local/1.0"

    def do_GET(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)

        self.server._last_path = parsed.path  # type: ignore[attr-defined]
        self.server._last_qs = qs  # type: ignore[attr-defined]

        code = (qs.get("code") or [None])[0]
        state = (qs.get("state") or [None])[0]
        err = (qs.get("error") or [None])[0]

        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()

        if err:
            self.wfile.write(f"OAuth error: {err}\n".encode("utf-8"))
        elif code:
            self.wfile.write(b"OK. You can close this tab.\n")
        else:
            self.wfile.write(b"No code received.\n")

        # Stop the server after first callback.
        self.server._done = True  # type: ignore[attr-defined]

    def log_message(self, fmt: str, *args) -> None:
        # Quiet by default.
        return


def run_callback_server(host: str, port: int, timeout_s: int) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    httpd = HTTPServer((host, port), _CallbackHandler)
    httpd._done = False  # type: ignore[attr-defined]
    httpd._last_path = None  # type: ignore[attr-defined]
    httpd._last_qs = None  # type: ignore[attr-defined]

    started = time.time()
    while True:
        httpd.handle_request()
        if getattr(httpd, "_done", False):
            qs = getattr(httpd, "_last_qs", {}) or {}
            code = (qs.get("code") or [None])[0]
            state = (qs.get("state") or [None])[0]
            err = (qs.get("error") or [None])[0]
            return code, state, err

        if time.time() - started > timeout_s:
            return None, None, "timeout"


def main() -> int:
    ap = argparse.ArgumentParser(description="Withings OAuth local callback helper")
    ap.add_argument("user_id", help="User ID (e.g. alice, bob, charlie)")
    ap.add_argument("--timeout", type=int, default=300, help="Seconds to wait for callback")
    ap.add_argument("--port", type=int, default=18081, help="Callback server port")

    args = ap.parse_args()

    if not CLIENT_ID or not CLIENT_SECRET:
        print("Missing WITHINGS_CLIENT_ID or WITHINGS_CLIENT_SECRET. Set in environment or config.json.", file=sys.stderr)
        return 2

    state = secrets.token_hex(16)
    url = build_authorize_url(
        client_id=CLIENT_ID,
        redirect_uri=REDIRECT_URI,
        scope="user.metrics,user.activity",
        state=state,
    )

    print(f"User: {args.user_id}")
    print("\nOpen this URL in your browser:")
    print(url)
    print(f"\nWaiting for redirect on: localhost:{args.port}")

    code, got_state, err = run_callback_server("localhost", args.port, args.timeout)

    if err and err != "timeout":
        print(f"OAuth error: {err}", file=sys.stderr)
        return 3
    if err == "timeout":
        print("Timed out waiting for callback.", file=sys.stderr)
        return 4
    if not code:
        print("No code received.", file=sys.stderr)
        return 5
    if got_state != state:
        print("State mismatch (possible CSRF / wrong browser session). Aborting.", file=sys.stderr)
        return 6

    print("\nReceived authorization code.")
    print("Exchanging code for tokens...")

    # Exchange code for tokens
    tokens = post_request('/v2/oauth2', {
        'action': 'requesttoken',
        'grant_type': 'authorization_code',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': code,
        'redirect_uri': REDIRECT_URI,
    })

    # Save tokens
    save_tokens(tokens, args.user_id)

    print(f"\n✓ Authentication successful for '{args.user_id}'!")
    print(f"Tokens saved to: {get_token_file(args.user_id)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
