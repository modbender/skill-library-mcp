#!/usr/bin/env python3
"""
init.py - Validation des capacites du skill veille.

Checks :
  1. Config file exists (~/.openclaw/config/veille/config.json)
  2. Data directories exist (creates them if missing)
  3. Fetch test on the first configured source (timeout 10s)

Sorties : OK / WARN / FAIL pour chaque check.
Exit code : 0 si tout OK ou WARN, 1 si au moins un FAIL.
"""

import json
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

# ---- Paths ------------------------------------------------------------------

SKILL_DIR   = Path(__file__).resolve().parent.parent
_CONFIG_DIR = Path.home() / ".openclaw" / "config" / "veille"
_DATA_DIR   = Path.home() / ".openclaw" / "data" / "veille"
CONFIG_FILE = _CONFIG_DIR / "config.json"

USER_AGENT  = "Mozilla/5.0 compatible Jarvis-veille/1.0"

# ---- Reporting --------------------------------------------------------------

_results = []


def _report(status: str, label: str, detail: str = ""):
    icon = {"OK": "[OK  ]", "WARN": "[WARN]", "FAIL": "[FAIL]"}.get(status, "[????]")
    msg = f"{icon} {label}"
    if detail:
        msg += f"\n         {detail}"
    print(msg)
    _results.append(status)


# ---- Checks -----------------------------------------------------------------


def check_config():
    """Check 1: config file exists and is valid JSON."""
    if not CONFIG_FILE.exists():
        _report("FAIL", "Config file",
                f"Not found: {CONFIG_FILE}\n"
                f"         Run: python3 setup.py")
        return None

    try:
        cfg = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        sources = cfg.get("sources", {})
        count = len(sources)
        _report("OK", "Config file", f"{CONFIG_FILE} ({count} sources)")
        return cfg
    except Exception as e:
        _report("FAIL", "Config file", f"Invalid JSON: {e}")
        return None


def check_data_dirs():
    """Check 2: data directories exist (create if needed)."""
    created = []
    for d in [_DATA_DIR]:
        if not d.exists():
            try:
                d.mkdir(parents=True, exist_ok=True)
                created.append(str(d))
            except Exception as e:
                _report("FAIL", "Data directory", f"Cannot create {d}: {e}")
                return

    if created:
        _report("WARN", "Data directories",
                f"Created: {', '.join(created)}")
    else:
        _report("OK", "Data directories", str(_DATA_DIR))


def check_fetch(cfg: dict):
    """Check 3: test fetch on first configured source."""
    sources = cfg.get("sources", {})
    if not sources:
        _report("WARN", "Network fetch", "No sources configured - skipping")
        return

    # Take first real source (skip _comment_* keys)
    real_sources = {k: v for k, v in sources.items() if not k.startswith("_")}
    if not real_sources:
        _report("WARN", "Network fetch", "No real sources configured - skipping")
        return
    first_name, first_url = next(iter(real_sources.items()))

    req = urllib.request.Request(first_url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read()
        # Try basic XML parse
        root = ET.fromstring(raw)
        tag = root.tag.lower()
        if "}" in tag:
            tag = tag.split("}", 1)[1]

        # Count items/entries
        count = 0
        if tag == "rss":
            channel = root.find("channel")
            if channel is not None:
                count = len(channel.findall("item"))
        else:
            ns = "http://www.w3.org/2005/Atom"
            count = len(root.findall(f"{{{ns}}}entry")) or len(root.findall("entry"))

        _report("OK", "Network fetch",
                f"{first_name}: {count} items found in feed")
    except urllib.error.URLError as e:
        _report("FAIL", "Network fetch",
                f"{first_name} ({first_url}): {e}")
    except ET.ParseError as e:
        _report("WARN", "Network fetch",
                f"{first_name}: feed fetched but XML parse failed: {e}")
    except Exception as e:
        _report("FAIL", "Network fetch",
                f"{first_name}: unexpected error: {e}")


# ---- Main -------------------------------------------------------------------


def main():
    print("=== OpenClaw Skill Veille - Init Check ===")
    print()

    cfg = check_config()
    check_data_dirs()

    if cfg is not None:
        check_fetch(cfg)
    else:
        _report("WARN", "Network fetch", "Skipped (config unavailable)")

    print()
    fails = _results.count("FAIL")
    warns = _results.count("WARN")

    if fails > 0:
        print(f"Result: {fails} FAIL, {warns} WARN - fix errors before using the skill")
        sys.exit(1)
    elif warns > 0:
        print(f"Result: {warns} WARN - skill usable but review warnings")
    else:
        print("Result: all checks passed - skill ready")


if __name__ == "__main__":
    main()
