"""Documentation fetcher for OpenClaw error codes and references."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from .utils import DATA_DIR, save_json


class DocFetcher:
    """Fetch and update OpenClaw documentation references."""

    DOCS_BASE = "https://docs.openclaw.ai"
    ERROR_CODES_URL = f"{DOCS_BASE}/api/error-codes.json"

    def __init__(self):
        """Initialize doc fetcher."""
        self.error_patterns_file = DATA_DIR / "error-patterns.json"

    def check_reachability(self) -> bool:
        """
        Check if OpenClaw docs are reachable.

        Returns:
            True if docs can be reached
        """
        try:
            result = subprocess.run(
                ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", self.DOCS_BASE],
                capture_output=True,
                text=True,
                timeout=10,
                check=False
            )
            return result.stdout.strip() == "200"
        except Exception:
            return False

    def fetch_error_codes(self) -> dict | None:
        """
        Fetch latest error codes from docs.

        Returns:
            Error codes data or None if fetch failed
        """
        try:
            result = subprocess.run(
                ["curl", "-s", self.ERROR_CODES_URL],
                capture_output=True,
                text=True,
                timeout=30,
                check=False
            )

            if result.returncode == 0 and result.stdout.strip():
                return json.loads(result.stdout)
        except Exception:
            pass

        return None

    def update_error_patterns(self) -> tuple[bool, int]:
        """
        Update local error patterns with new codes from docs.

        Returns:
            Tuple of (success, new_codes_count)
        """
        # Load current patterns
        current_data = {}
        if self.error_patterns_file.exists():
            try:
                with open(self.error_patterns_file, 'r') as f:
                    current_data = json.load(f)
            except Exception:
                pass

        current_patterns = current_data.get("patterns", [])
        current_codes = {p.get("code") for p in current_patterns if p.get("code")}

        # Fetch latest from docs
        remote_data = self.fetch_error_codes()
        if not remote_data:
            return False, 0

        remote_patterns = remote_data.get("patterns", [])
        new_count = 0

        # Merge new patterns
        for pattern in remote_patterns:
            code = pattern.get("code")
            if code and code not in current_codes:
                current_patterns.append(pattern)
                current_codes.add(code)
                new_count += 1

        # Save updated patterns
        if new_count > 0:
            updated_data = {"patterns": current_patterns}
            if save_json(self.error_patterns_file, updated_data):
                return True, new_count

        return new_count == 0, new_count

    def get_version_info(self) -> dict:
        """
        Get current OpenClaw version information.

        Returns:
            Dict with version, latest, update_available
        """
        try:
            # Get current version
            result = subprocess.run(
                ["openclaw", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False
            )

            current = "unknown"
            if result.returncode == 0:
                current = result.stdout.strip().split()[-1]

            # Get latest from npm
            result = subprocess.run(
                ["npm", "view", "openclaw", "version"],
                capture_output=True,
                text=True,
                timeout=10,
                check=False
            )

            latest = "unknown"
            if result.returncode == 0:
                latest = result.stdout.strip()

            return {
                "current": current,
                "latest": latest,
                "update_available": current != "unknown" and latest != "unknown" and current != latest
            }
        except Exception:
            return {
                "current": "unknown",
                "latest": "unknown",
                "update_available": False
            }
