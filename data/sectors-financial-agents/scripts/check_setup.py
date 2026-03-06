#!/usr/bin/env python3
"""
Verify that SECTORS_API_KEY is set and can authenticate with the Sectors API.

Usage:
    python scripts/check_setup.py

Exit codes:
    0 - API key is valid and API is reachable
    1 - SECTORS_API_KEY environment variable is not set
    2 - API key is invalid (403 Forbidden)
    3 - API is unreachable or returned an unexpected error
"""

import os
import sys

ENV_VAR = "SECTORS_API_KEY"
BASE_URL = "https://api.sectors.app/v1"
TEST_ENDPOINT = "/subsectors/"


def main():
    # 1. Check environment variable
    api_key = os.environ.get(ENV_VAR)
    if not api_key:
        print(f"ERROR: {ENV_VAR} environment variable is not set.")
        print()
        print("Set it with one of:")
        print(f'  export {ENV_VAR}="your-api-key-here"')
        print(f'  echo \'export {ENV_VAR}="your-api-key-here"\' >> ~/.bashrc')
        print()
        print("Get your API key at: https://sectors.app/api")
        sys.exit(1)

    print(f"[ok] {ENV_VAR} is set ({len(api_key)} characters)")

    # 2. Check requests is installed
    try:
        import requests
    except ImportError:
        print("[!!] 'requests' library is not installed.")
        print("     Install it with: pip install requests")
        sys.exit(3)

    print("[ok] requests library is available")

    # 3. Test API connectivity
    url = f"{BASE_URL}{TEST_ENDPOINT}"
    headers = {"Authorization": api_key}

    try:
        resp = requests.get(url, headers=headers, timeout=15)
    except requests.exceptions.ConnectionError:
        print(f"[!!] Cannot reach {BASE_URL}. Check your network connection.")
        sys.exit(3)
    except requests.exceptions.Timeout:
        print(f"[!!] Request to {BASE_URL} timed out.")
        sys.exit(3)
    except Exception as e:
        print(f"[!!] Unexpected error: {e}")
        sys.exit(3)

    if resp.status_code == 403:
        print("[!!] API key is invalid (403 Forbidden).")
        print("     Double-check your key at: https://sectors.app/api")
        sys.exit(2)

    if not resp.ok:
        print(f"[!!] API returned status {resp.status_code}: {resp.text[:200]}")
        sys.exit(3)

    # 4. Validate response is JSON
    try:
        data = resp.json()
    except ValueError:
        print("[!!] API returned non-JSON response.")
        sys.exit(3)

    print(f"[ok] API is reachable and authenticated ({len(data)} subsectors found)")
    print()
    print("Setup is complete. Your agent can now use the Sectors API skill.")
    sys.exit(0)


if __name__ == "__main__":
    main()
