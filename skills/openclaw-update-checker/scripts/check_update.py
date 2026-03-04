#!/usr/bin/env python3
"""
OpenClaw Update Checker

Compares the locally installed openclaw version against the npm registry
to determine if updates are available.

Read-only — no files are modified, no packages installed, no services restarted.
No subprocess calls — reads local package.json and queries the npm registry
API via HTTPS directly.

Usage:
    python3 check_update.py              # Human-readable text output
    python3 check_update.py --format json # Machine-readable JSON output
"""

import json
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path


# Known install locations for openclaw's package.json
_PACKAGE_JSON_PATHS = [
    Path("/usr/lib/node_modules/openclaw/package.json"),
    Path("/usr/local/lib/node_modules/openclaw/package.json"),
]

# npm public registry endpoint (read-only, no auth required)
_NPM_REGISTRY_URL = "https://registry.npmjs.org/openclaw"


def get_installed_version() -> str | None:
    """Read the installed openclaw version from its package.json."""
    for p in _PACKAGE_JSON_PATHS:
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            version = data.get("version")
            if version:
                return str(version)
        except (FileNotFoundError, PermissionError, json.JSONDecodeError):
            continue
    return None


def get_registry_versions() -> list[str] | None:
    """Fetch all published versions from the npm registry via HTTPS."""
    try:
        req = urllib.request.Request(
            _NPM_REGISTRY_URL,
            headers={"Accept": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            versions = list(data.get("versions", {}).keys())
            return versions if versions else None
    except (urllib.error.URLError, json.JSONDecodeError, OSError):
        return None


def parse_version(v: str) -> tuple[int, int, int, int]:
    """Parse YYYY.M.DD[-N] version string into a comparable tuple."""
    match = re.match(r"(\d+)\.(\d+)\.(\d+)(?:-(\d+))?", v)
    if not match:
        return (0, 0, 0, 0)
    return (
        int(match.group(1)),
        int(match.group(2)),
        int(match.group(3)),
        int(match.group(4)) if match.group(4) else 0,
    )


def get_latest_version(versions: list[str]) -> str | None:
    """Return the highest version from a list."""
    if not versions:
        return None
    return max(versions, key=parse_version)


def get_changelog_url(version: str) -> str:
    """Generate the GitHub release URL for a given version."""
    base = re.sub(r"-\d+$", "", version)
    return f"https://github.com/openclaw/openclaw/releases/tag/v{base}"


def main() -> None:
    output_format = "text"
    if "--format" in sys.argv:
        idx = sys.argv.index("--format")
        if idx + 1 < len(sys.argv):
            output_format = sys.argv[idx + 1]

    installed = get_installed_version()
    if not installed:
        msg = "Could not determine installed openclaw version"
        print(json.dumps({"error": msg}) if output_format == "json" else f"Error: {msg}")
        sys.exit(1)

    versions = get_registry_versions()
    if not versions:
        msg = "Could not fetch versions from npm registry"
        print(json.dumps({"error": msg}) if output_format == "json" else f"Error: {msg}")
        sys.exit(1)

    latest = get_latest_version(versions)
    installed_tuple = parse_version(installed)
    is_current = installed_tuple >= parse_version(latest)

    newer = sorted(
        [v for v in versions if parse_version(v) > installed_tuple],
        key=parse_version,
    )

    result = {
        "installed": installed,
        "latest": latest,
        "up_to_date": is_current,
        "newer_versions": newer,
        "changelog_url": get_changelog_url(latest),
    }

    if output_format == "json":
        print(json.dumps(result, indent=2))
    elif is_current:
        print(f"✅ OpenClaw is up to date: {installed}")
    else:
        print(f"⬆️  Update available: {installed} → {latest}")
        print(f"   Versions behind: {len(newer)}")
        shown = newer if len(newer) <= 5 else newer[-5:]
        for v in shown:
            print(f"   • {v}")
        if len(newer) > 5:
            print(f"   ... and {len(newer) - 5} more")
        print(f"   Release: {get_changelog_url(latest)}")


if __name__ == "__main__":
    main()
