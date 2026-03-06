#!/usr/bin/env python3
import json
import sys
from typing import Any, Dict, Optional

import os
from pathlib import Path

import requests


def _load_config() -> Dict[str, Any]:
    """Load config.json from skill root, with env var overrides."""
    skill_root = Path(__file__).resolve().parents[1]
    cfg_path = skill_root / "config.json"
    cfg: Dict[str, Any] = {}
    if cfg_path.exists():
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))

    api_key = os.environ.get("UNIFI_API_KEY") or cfg.get("api_key")
    if not api_key:
        raise SystemExit(
            "Missing UniFi API key. Set UNIFI_API_KEY or create config.json (see config.json.example)."
        )

    base_url = os.environ.get("UNIFI_BASE_URL") or cfg.get("base_url") or "https://api.ui.com"

    cfg["api_key"] = api_key
    cfg["base_url"] = base_url
    return cfg


CONFIG = _load_config()
API_KEY = CONFIG["api_key"]
BASE_URL = CONFIG["base_url"]

# Test both EA (Early Access) and v1 (Official) endpoints
ENDPOINTS_TO_TEST = [
    "/v1/hosts",
    "/v1/sites",
    "/v1/devices", 
    "/ea/devices",
    "/v1/clients",
    "/ea/clients",
    "/v1/stations",
    "/ea/stations",
]


def _request(base_url: str, path: str) -> Dict[str, Any]:
    url = f"{base_url.rstrip('/')}{path}"
    headers = {
        "X-API-KEY": API_KEY,
        "Accept": "application/json",
    }
    try:
        resp = requests.get(url, headers=headers, timeout=15)
    except requests.RequestException as exc:
        return {"ok": False, "error": f"request_error: {exc}", "url": url}

    try:
        data = resp.json()
    except ValueError:
        data = {"raw": resp.text}

    if not resp.ok:
        return {
            "ok": False,
            "status": resp.status_code,
            "error": data,
            "url": url,
        }

    return {"ok": True, "status": resp.status_code, "data": data, "url": url}


def list_hosts() -> Dict[str, Any]:
    """List all UniFi hosts/controllers"""
    return _request(BASE_URL, "/v1/hosts")


def list_devices() -> Dict[str, Any]:
    """List all devices (try EA endpoint)"""
    return _request(BASE_URL, "/ea/devices")


def main() -> int:
    print(f"=== Testing UniFi Site Manager API at {BASE_URL} ===\n")
    
    # Test all endpoints to find which ones work
    for endpoint in ENDPOINTS_TO_TEST:
        print(f"\n-- Testing: {endpoint}")
        result = _request(BASE_URL, endpoint)
        print(json.dumps(result, indent=2))
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
