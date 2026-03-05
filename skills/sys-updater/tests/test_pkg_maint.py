#!/usr/bin/env python3
"""Unit tests for pkg_maint refactor paths.

Covers:
- pnpm no-importer fallback handling
- auto-plan of long-pending items
- brew link recovery path in upgrade_mode
"""

import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

# Add scripts dir to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import pkg_maint


class TestPkgMaint(unittest.TestCase):
    def test_check_pnpm_no_importer_manifest(self):
        """pnpm global store not initialized should not be treated as error."""
        with patch.object(pkg_maint, "sh") as mock_sh:
            mock_sh.side_effect = [
                (0, "10.30.0", ""),
                (1, "ERR_PNPM_NO_IMPORTER_MANIFEST_FOUND No package.json", ""),
            ]

            result = pkg_maint.check_pnpm()

        self.assertTrue(result["installed"])
        self.assertEqual(result["outdated"], [])

    def test_auto_plan_long_pending(self):
        """Old pending items should be escalated to planned=true."""
        now = datetime.now(timezone.utc)
        tracked = {
            "items": {
                "old_pending": {
                    "firstSeenAt": (now - timedelta(days=7)).isoformat().replace("+00:00", "Z"),
                    "reviewResult": "pending",
                    "planned": False,
                    "blocked": False,
                    "note": "Pending: manual review recommended",
                },
                "fresh_pending": {
                    "firstSeenAt": (now - timedelta(days=1)).isoformat().replace("+00:00", "Z"),
                    "reviewResult": "pending",
                    "planned": False,
                    "blocked": False,
                    "note": "Pending: manual review recommended",
                },
            }
        }

        changed = pkg_maint.auto_plan_long_pending(tracked, "brew", days=4)

        self.assertEqual(changed, 1)
        self.assertTrue(tracked["items"]["old_pending"]["planned"])
        self.assertFalse(tracked["items"]["fresh_pending"]["planned"])

    def test_upgrade_mode_brew_link_recovery(self):
        """When brew upgrade fails on link step, link retry should recover."""
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            npm_path = base / "npm_tracked.json"
            pnpm_path = base / "pnpm_tracked.json"
            brew_path = base / "brew_tracked.json"

            npm_path.write_text(json.dumps({"items": {}}))
            pnpm_path.write_text(json.dumps({"items": {}}))
            brew_path.write_text(
                json.dumps(
                    {
                        "items": {
                            "zlib": {
                                "firstSeenAt": "2026-02-10T00:00:00Z",
                                "planned": True,
                                "blocked": False,
                                "reviewResult": "ok",
                                "manager": "brew",
                                "currentVersion": "1.3.1_1",
                                "latestVersion": "1.3.2",
                            }
                        }
                    }
                )
            )

            def sh_side_effect(cmd, check=False, timeout=60):
                if cmd[:3] == ["brew", "upgrade", "zlib"]:
                    return 1, "", "Error: The `brew link` step did not complete successfully"
                if cmd[:4] == ["brew", "link", "--overwrite", "zlib"]:
                    return 0, "linked", ""
                if cmd[:2] == ["npm", "--version"]:
                    return 0, "10", ""
                if cmd[:4] == ["npm", "outdated", "-g", "--json"]:
                    return 0, "{}", ""
                if cmd[:2] == ["pnpm", "--version"]:
                    return 0, "10", ""
                if cmd[:4] == ["pnpm", "outdated", "-g", "--json"]:
                    return 0, "{}", ""
                if cmd[:2] == ["brew", "--version"]:
                    return 0, "Homebrew", ""
                if cmd[:3] == ["brew", "outdated", "--json"]:
                    return 0, json.dumps({"formulae": [], "casks": []}), ""
                return 0, "", ""

            with (
                patch.object(pkg_maint, "NPM_TRACK_PATH", npm_path),
                patch.object(pkg_maint, "PNPM_TRACK_PATH", pnpm_path),
                patch.object(pkg_maint, "BREW_TRACK_PATH", brew_path),
                patch.dict(
                    pkg_maint.MANAGER_TRACK_PATHS,
                    {"npm": npm_path, "pnpm": pnpm_path, "brew": brew_path},
                    clear=True,
                ),
                patch.object(pkg_maint, "sh", side_effect=sh_side_effect),
            ):
                report = pkg_maint.upgrade_mode(dry_run=False)

            self.assertIn("✅ brew: zlib", report)

            updated = json.loads(brew_path.read_text())
            # After successful recovery + post-upgrade recheck the item may be removed
            # from tracking (no longer outdated). If still present, it must be unplanned.
            if "zlib" in updated.get("items", {}):
                item = updated["items"]["zlib"]
                self.assertFalse(item["planned"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
