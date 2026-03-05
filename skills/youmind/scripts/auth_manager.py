#!/usr/bin/env python3
"""
Authentication manager for Youmind.
Handles login state persistence for browser automation.
"""

import argparse
import json
import re
import shutil
import sys
import time
from pathlib import Path
from typing import Any, Dict

from patchright.sync_api import BrowserContext, sync_playwright

# Add scripts directory to import path
sys.path.insert(0, str(Path(__file__).parent))

from browser_utils import BrowserFactory
from config import (
    AUTH_INFO_FILE,
    BROWSER_STATE_DIR,
    DATA_DIR,
    STATE_FILE,
    YOUMIND_OVERVIEW_URL,
    YOUMIND_SIGN_IN_URL,
)


class AuthManager:
    """Manages Youmind authentication state and validation."""

    def __init__(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        BROWSER_STATE_DIR.mkdir(parents=True, exist_ok=True)

        self.state_file = STATE_FILE
        self.auth_info_file = AUTH_INFO_FILE
        self.browser_state_dir = BROWSER_STATE_DIR

    def is_authenticated(self) -> bool:
        """Return True if cookies are available via CDP or state.json."""
        # Prefer CDP: if the OpenClaw browser is running with a valid YouMind session,
        # authentication is always available regardless of state.json age.
        try:
            import sys as _sys, os as _os
            _sys.path.insert(0, _os.path.dirname(__file__))
            from cdp_auth import is_cdp_available, get_cdp_cookie_str
            if is_cdp_available() and get_cdp_cookie_str():
                return True
        except Exception:
            pass

        # Fall back to state.json
        if not self.state_file.exists():
            return False

        age_days = (time.time() - self.state_file.stat().st_mtime) / 86400
        if age_days > 7:
            print(f"⚠️ Browser state is {age_days:.1f} days old, re-auth may be required")

        return True

    def get_auth_info(self) -> Dict[str, Any]:
        """Return auth metadata and state age."""
        info = {
            "authenticated": self.is_authenticated(),
            "state_file": str(self.state_file),
            "state_exists": self.state_file.exists(),
        }

        # CDP status
        try:
            import sys as _sys, os as _os
            _sys.path.insert(0, _os.path.dirname(__file__))
            from cdp_auth import is_cdp_available, CACHE_FILE
            info["cdp_available"] = is_cdp_available()
            if CACHE_FILE.exists():
                import json as _json
                cache = _json.loads(CACHE_FILE.read_text())
                info["cdp_cache_age_hours"] = (time.time() - cache.get("saved_at", 0)) / 3600
            else:
                info["cdp_cache_age_hours"] = None
        except Exception:
            info["cdp_available"] = False
            info["cdp_cache_age_hours"] = None

        if self.auth_info_file.exists():
            try:
                with open(self.auth_info_file, "r") as f:
                    saved_info = json.load(f)
                info.update(saved_info)
            except Exception:
                pass

        if info["state_exists"]:
            info["state_age_hours"] = (time.time() - self.state_file.stat().st_mtime) / 3600

        return info

    def setup_auth(self, headless: bool = False, timeout_minutes: int = 10) -> bool:
        """Interactive sign-in flow for Youmind."""
        print("🔐 Starting Youmind authentication setup...")
        print(f"  Timeout: {timeout_minutes} minutes")
        print("  Browser should stay visible for manual login.")

        playwright = None
        context = None

        try:
            playwright = sync_playwright().start()
            context = BrowserFactory.launch_persistent_context(playwright, headless=headless)

            page = context.new_page()
            page.goto(YOUMIND_SIGN_IN_URL, wait_until="domcontentloaded")

            # Already logged in.
            if "youmind.com" in page.url and "sign-in" not in page.url:
                print("  ✅ Already authenticated")
                self._save_browser_state(context)
                self._save_auth_info()
                return True

            print("\n  ⏳ Please complete login in the opened browser window...")
            timeout_ms = int(timeout_minutes * 60 * 1000)

            # Wait until user leaves sign-in route.
            page.wait_for_url(re.compile(r"^https://youmind\.com/(?!.*sign-in).*"), timeout=timeout_ms)

            print("  ✅ Login successful")
            self._save_browser_state(context)
            self._save_auth_info()
            return True

        except Exception as e:
            print(f"  ❌ Authentication failed or timed out: {e}")
            return False

        finally:
            if context:
                try:
                    context.close()
                except Exception:
                    pass
            if playwright:
                try:
                    playwright.stop()
                except Exception:
                    pass

    def _save_browser_state(self, context: BrowserContext):
        """Persist browser storage state."""
        context.storage_state(path=str(self.state_file))
        print(f"  💾 Saved browser state: {self.state_file}")

    def _save_auth_info(self):
        """Persist auth metadata."""
        try:
            info = {
                "authenticated_at": time.time(),
                "authenticated_at_iso": time.strftime("%Y-%m-%d %H:%M:%S"),
            }
            with open(self.auth_info_file, "w") as f:
                json.dump(info, f, indent=2)
        except Exception:
            pass

    def clear_auth(self) -> bool:
        """Delete local auth state and browser profile cache."""
        print("🗑️ Clearing Youmind authentication data...")

        try:
            if self.state_file.exists():
                self.state_file.unlink()
                print("  ✅ Removed state.json")

            if self.auth_info_file.exists():
                self.auth_info_file.unlink()
                print("  ✅ Removed auth_info.json")

            if self.browser_state_dir.exists():
                shutil.rmtree(self.browser_state_dir)
                self.browser_state_dir.mkdir(parents=True, exist_ok=True)
                print("  ✅ Cleared browser_state/")

            return True

        except Exception as e:
            print(f"  ❌ Failed to clear auth data: {e}")
            return False

    def re_auth(self, headless: bool = False, timeout_minutes: int = 10) -> bool:
        """Clear and run setup again."""
        print("🔄 Starting re-authentication...")
        self.clear_auth()
        return self.setup_auth(headless=headless, timeout_minutes=timeout_minutes)

    def validate_auth(self) -> bool:
        """Validate that saved auth can access Youmind overview."""
        if not self.is_authenticated():
            return False

        print("🔍 Validating Youmind authentication...")

        playwright = None
        context = None

        try:
            playwright = sync_playwright().start()
            context = BrowserFactory.launch_persistent_context(playwright, headless=True)

            page = context.new_page()
            page.goto(YOUMIND_OVERVIEW_URL, wait_until="domcontentloaded", timeout=30000)

            if "youmind.com" in page.url and "sign-in" not in page.url:
                print("  ✅ Authentication is valid")
                return True

            print("  ❌ Authentication is invalid (redirected to sign-in)")
            return False

        except Exception as e:
            print(f"  ❌ Validation failed: {e}")
            return False

        finally:
            if context:
                try:
                    context.close()
                except Exception:
                    pass
            if playwright:
                try:
                    playwright.stop()
                except Exception:
                    pass


def main():
    parser = argparse.ArgumentParser(description="Manage Youmind authentication")

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    setup_parser = subparsers.add_parser("setup", help="Setup authentication")
    setup_parser.add_argument("--headless", action="store_true", help="Run browser headless")
    setup_parser.add_argument("--timeout", type=float, default=10, help="Login timeout minutes")

    subparsers.add_parser("status", help="Check authentication status")
    subparsers.add_parser("validate", help="Validate authentication")
    subparsers.add_parser("clear", help="Clear authentication")

    reauth_parser = subparsers.add_parser("reauth", help="Clear and setup again")
    reauth_parser.add_argument("--timeout", type=float, default=10, help="Login timeout minutes")

    args = parser.parse_args()

    auth = AuthManager()

    if args.command == "setup":
        if auth.setup_auth(headless=args.headless, timeout_minutes=args.timeout):
            print("\n✅ Youmind authentication setup complete")
        else:
            print("\n❌ Authentication setup failed")
            raise SystemExit(1)

    elif args.command == "status":
        info = auth.get_auth_info()
        print("\n🔐 Authentication Status:")
        print(f"  Authenticated: {'Yes' if info['authenticated'] else 'No'}")
        if info.get("state_age_hours") is not None:
            print(f"  State age: {info['state_age_hours']:.1f} hours")
        if info.get("authenticated_at_iso"):
            print(f"  Last auth: {info['authenticated_at_iso']}")
        print(f"  State file: {info['state_file']}")

    elif args.command == "validate":
        if auth.validate_auth():
            print("Authentication is valid")
        else:
            print("Authentication is invalid or expired")
            print("Run: python scripts/run.py auth_manager.py setup")
            raise SystemExit(1)

    elif args.command == "clear":
        if not auth.clear_auth():
            raise SystemExit(1)

    elif args.command == "reauth":
        if auth.re_auth(timeout_minutes=args.timeout):
            print("\n✅ Re-authentication complete")
        else:
            print("\n❌ Re-authentication failed")
            raise SystemExit(1)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
