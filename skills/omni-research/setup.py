#!/usr/bin/env python3
"""Setup helper for omni-research.

Checks prerequisites and creates default config.
Browser login is not needed — the skill uses your existing browser sessions.
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "omni-research"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "cdp_port": 9222,
    "cliproxy_url": "http://127.0.0.1:8317/v1",
    "cliproxy_key": "",
    "synthesis_model": "glm-4.7",
    "gemini_api_model": "gemini-2.5-flash",
}


def check_agent_browser() -> bool:
    return shutil.which("agent-browser") is not None


def check_cdp(port: int = 9222) -> bool:
    try:
        import httpx
        resp = httpx.get(f"http://127.0.0.1:{port}/json/version", timeout=2)
        return resp.status_code == 200
    except Exception:
        return False


def main():
    print("omni-research setup")
    print("=" * 40)

    # Check agent-browser
    if check_agent_browser():
        print("[OK] agent-browser installed")
    else:
        print("[!!] agent-browser not found")
        print("     Install: npm install -g agent-browser")

    # Check CDP
    if check_cdp():
        print("[OK] Browser CDP available on port 9222")
    else:
        print("[!!] Browser CDP not available")
        print("     Start Chrome/Edge with: --remote-debugging-port=9222")

    # Create config
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.exists():
        with open(CONFIG_FILE, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
        print(f"[OK] Config created: {CONFIG_FILE}")
    else:
        print(f"[OK] Config exists: {CONFIG_FILE}")

    print()
    print("To use:")
    print("  python3 research.py 'your query here'")
    print()
    print("For API-only mode (no browser):")
    print("  python3 research.py --sources gemini-api 'query'")


if __name__ == "__main__":
    main()
