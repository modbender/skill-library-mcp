"""Shared utilities for Kaggle competition report generation."""

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

# Rate limiting: seconds between API calls
API_DELAY = 3

# Root of the repo (five levels up from this file:
# skills/kaggle/modules/comp-report/scripts/utils.py)
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent.parent


def get_api():
    """Initialize and authenticate the Kaggle API client."""
    from kaggle.api.kaggle_api_extended import KaggleApi

    api = KaggleApi()
    api.authenticate()
    return api


def get_username() -> str:
    """Get the Kaggle username from env or kaggle.json."""
    username = os.getenv("KAGGLE_USERNAME")
    if username:
        return username
    kaggle_json = Path.home() / ".kaggle" / "kaggle.json"
    if kaggle_json.exists():
        creds = json.loads(kaggle_json.read_text())
        return creds.get("username", "")
    return ""


def get_kaggle_cli() -> str:
    """Find the kaggle CLI binary."""
    for path in [
        shutil.which("kaggle"),
        "/Library/Frameworks/Python.framework/Versions/3.12/bin/kaggle",
        str(Path.home() / ".local" / "bin" / "kaggle"),
    ]:
        if path and Path(path).exists():
            return path
    return "kaggle"


def check_credentials() -> bool:
    """Verify Kaggle credentials are configured and API authenticates."""
    # Check if kaggle.json exists
    kaggle_json = Path.home() / ".kaggle" / "kaggle.json"
    if not kaggle_json.exists():
        if not (os.getenv("KAGGLE_USERNAME") and os.getenv("KAGGLE_KEY")):
            print("ERROR: No Kaggle credentials found.")
            print("  Set KAGGLE_USERNAME + KAGGLE_KEY env vars, or create ~/.kaggle/kaggle.json")
            return False

    # Try to authenticate
    try:
        api = get_api()
        # Quick check: list competitions to verify auth works
        result = api.competitions_list(page=1, page_size=1)
        comps = unwrap_response(result, "competitions")
        username = get_username()
        print(f"OK: Kaggle API authenticated as '{username}'")
        print(f"  API returned {len(comps)} competition(s) in smoke test")
        return True
    except Exception as e:
        print(f"ERROR: Kaggle API authentication failed: {e}")
        return False


def unwrap_response(result, attr: str = "competitions") -> list:
    """Unwrap a Kaggle API response object to get the inner list.

    The newer kagglesdk returns response objects (e.g. ApiListCompetitionsResponse)
    with the actual data in a named attribute (e.g. .competitions). Older versions
    returned plain lists. This handles both.
    """
    if isinstance(result, list):
        return result
    if hasattr(result, attr):
        return getattr(result, attr) or []
    # Try common attributes
    for fallback in ["competitions", "files", "kernels", "results"]:
        if hasattr(result, fallback):
            return getattr(result, fallback) or []
    # Last resort: try to iterate
    try:
        return list(result)
    except TypeError:
        return []


def rate_limit():
    """Sleep for API_DELAY seconds to avoid throttling."""
    time.sleep(API_DELAY)


if __name__ == "__main__":
    ok = check_credentials()
    sys.exit(0 if ok else 1)
