"""
prob.trade API client — Public Analytics + Trading API (HMAC-secured)
"""

import urllib.request
import urllib.parse
import json
import sys
import os
import hmac
import hashlib
import time
from typing import Optional

_HOST = "https://api.prob.trade"
API_BASE = f"{_HOST}/api/public"
TRADING_BASE = f"{_HOST}/api/trading"


def fetch(endpoint: str, params: Optional[dict] = None) -> dict:
    """Make a GET request to the prob.trade Public API (authenticated with PTK key)."""
    url = f"{API_BASE}{endpoint}"
    if params:
        filtered = {k: v for k, v in params.items() if v is not None}
        if filtered:
            url += "?" + urllib.parse.urlencode(filtered)

    req = urllib.request.Request(url)
    req.add_header("User-Agent", "probtrade-openclaw-skill/1.0")

    # Public API requires authentication — sign with PTK key if available
    config = _load_config()
    if config.get("api_key") and config.get("api_secret"):
        path = f"/api/public{endpoint}"
        auth_headers = _sign(config["api_secret"], "GET", path)
        req.add_header("X-PTK-Key", config["api_key"])
        for k, v in auth_headers.items():
            req.add_header(k, v)

    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode())
            if not data.get("success"):
                print(f"API error: {data.get('error', 'Unknown error')}", file=sys.stderr)
                sys.exit(1)
            return data.get("data", {})
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        try:
            err = json.loads(body)
            print(f"API error ({e.code}): {err.get('error', body)}", file=sys.stderr)
        except json.JSONDecodeError:
            print(f"API error ({e.code}): {body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Connection error: {e.reason}", file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# Trading API client (HMAC-SHA256 authenticated)
# ---------------------------------------------------------------------------

def _load_config() -> dict:
    """Load API key config from ~/.openclaw/skills/probtrade/config.yaml or env vars."""
    api_key = os.environ.get("PROBTRADE_API_KEY", "")
    api_secret = os.environ.get("PROBTRADE_API_SECRET", "")

    if api_key and api_secret:
        return {"api_key": api_key, "api_secret": api_secret}

    # Try config.yaml (simple key: value parsing, no yaml dependency)
    config_paths = [
        os.path.join(os.path.dirname(__file__), "..", "config.yaml"),
        os.path.expanduser("~/.openclaw/skills/probtrade/config.yaml"),
    ]
    for path in config_paths:
        if os.path.exists(path):
            with open(path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("#") or ":" not in line:
                        continue
                    key, _, value = line.partition(":")
                    value = value.strip().strip('"').strip("'")
                    if key.strip() == "api_key":
                        api_key = value
                    elif key.strip() == "api_secret":
                        api_secret = value
            if api_key and api_secret:
                return {"api_key": api_key, "api_secret": api_secret}

    return {}


def _sign(api_secret: str, method: str, path: str, body: str = "") -> dict:
    """Generate HMAC-SHA256 authentication headers."""
    timestamp = str(int(time.time() * 1000))
    message = timestamp + method.upper() + path + body
    signature = hmac.new(
        api_secret.encode(), message.encode(), hashlib.sha256
    ).hexdigest()
    return {
        "X-PTK-Timestamp": timestamp,
        "X-PTK-Signature": signature,
    }


def trading_request(method: str, endpoint: str, body: Optional[dict] = None) -> dict:
    """Make an authenticated request to the prob.trade Trading API."""
    config = _load_config()
    if not config.get("api_key") or not config.get("api_secret"):
        print(
            "Error: Trading API key not configured.\n"
            "Set PROBTRADE_API_KEY and PROBTRADE_API_SECRET env vars,\n"
            "or create config.yaml with api_key and api_secret.",
            file=sys.stderr,
        )
        sys.exit(1)

    path = f"/api/trading{endpoint}"
    url = f"{_HOST}{path}"
    body_str = json.dumps(body) if body and method.upper() not in ("GET", "DELETE") else ""

    headers = _sign(config["api_secret"], method, path, body_str)
    headers["X-PTK-Key"] = config["api_key"]
    headers["Content-Type"] = "application/json"
    headers["User-Agent"] = "probtrade-openclaw-skill/1.0"

    req = urllib.request.Request(url, method=method.upper(), headers=headers)
    if body_str:
        req.data = body_str.encode()

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode())
            if not data.get("success"):
                err = data.get("error", {})
                msg = err.get("message", str(err)) if isinstance(err, dict) else str(err)
                print(f"Trading API error: {msg}", file=sys.stderr)
                sys.exit(1)
            return data.get("data", {})
    except urllib.error.HTTPError as e:
        body_resp = e.read().decode() if e.fp else ""
        try:
            err = json.loads(body_resp)
            err_obj = err.get("error", {})
            code = err_obj.get("code", "") if isinstance(err_obj, dict) else ""
            msg = err_obj.get("message", str(err_obj)) if isinstance(err_obj, dict) else str(err_obj)
            print(f"Trading API error ({e.code}) [{code}]: {msg}", file=sys.stderr)
        except json.JSONDecodeError:
            print(f"Trading API error ({e.code}): {body_resp}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Connection error: {e.reason}", file=sys.stderr)
        sys.exit(1)
