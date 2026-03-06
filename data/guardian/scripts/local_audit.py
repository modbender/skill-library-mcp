#!/usr/bin/env python3
"""
Guardian BL-046 — Local Security Audit Pipeline
Runs config score, signature freshness, version check, false positive rate checks.
Auto-creates PM backlog items for HIGH/CRITICAL findings.
Outputs to dashboard/guardian-local-audit.json.
"""

from __future__ import annotations

import json
import os
import re
import sqlite3
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SKILL_DIR = Path(__file__).resolve().parents[1]
WORKSPACE = SKILL_DIR.parents[1]
DB_PATH = WORKSPACE / "guardian.db"
OPENCLAW_CONFIG = Path.home() / ".openclaw" / "openclaw.json"
DEFINITIONS_DIR = SKILL_DIR / "definitions"
BACKLOG_PATH = WORKSPACE / "skills" / "product-manager" / "data" / "guardian.json"
OUTPUT_PATH = WORKSPACE / "dashboard" / "guardian-local-audit.json"

KNOWN_LATEST_VERSION = "2026.2.24"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _nested_get(obj: Dict, *keys: str) -> Any:
    """Safely navigate nested dict keys. Returns None if any key is missing."""
    cur = obj
    for k in keys:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(k)
    return cur


def _score_to_grade(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 50:
        return "D"
    return "F"


# ---------------------------------------------------------------------------
# 1. Config Score Check
# ---------------------------------------------------------------------------

CONFIG_CHECKS = [
    {
        "key": "gateway.rateLimit",
        "title": "Rate limiting not configured",
        "description": "gateway.rateLimit is missing or disabled. Unthrottled requests can exhaust resources.",
        "severity": "high",
        "points": 20,
        "check": lambda cfg: bool(_nested_get(cfg, "gateway", "rateLimit")),
    },
    {
        "key": "tools.allowlist",
        "title": "Tool allowlist not configured",
        "description": "tools.allowlist is absent. Any tool can be invoked without restriction.",
        "severity": "high",
        "points": 15,
        "check": lambda cfg: bool(_nested_get(cfg, "tools", "allowlist")),
    },
    {
        "key": "models.allowlist",
        "title": "Model allowlist not configured",
        "description": "models.allowlist is absent. Any model can be selected, including untrusted providers.",
        "severity": "medium",
        "points": 15,
        "check": lambda cfg: bool(_nested_get(cfg, "models", "allowlist")),
    },
    {
        "key": "sessions.timeout",
        "title": "Session timeout not configured",
        "description": "sessions.timeout is missing. Sessions may run indefinitely, increasing attack surface.",
        "severity": "medium",
        "points": 15,
        "check": lambda cfg: bool(_nested_get(cfg, "sessions", "timeout")),
    },
    {
        "key": "logging.audit",
        "title": "Audit logging not enabled",
        "description": "logging.audit is absent or false. Security events are not being persisted for review.",
        "severity": "high",
        "points": 20,
        "check": lambda cfg: bool(_nested_get(cfg, "logging", "audit")),
    },
    {
        "key": "gateway.tls",
        "title": "TLS not configured on gateway",
        "description": "gateway.tls is missing. Gateway traffic may be transmitted unencrypted.",
        "severity": "medium",
        "points": 15,
        "check": lambda cfg: bool(_nested_get(cfg, "gateway", "tls")),
    },
]


def check_config_score() -> Tuple[int, str, List[Dict]]:
    """
    Read openclaw.json and score each config item.
    Returns (score/100, grade, issues_list).
    """
    issues: List[Dict] = []

    try:
        cfg = json.loads(OPENCLAW_CONFIG.read_text())
    except FileNotFoundError:
        return 0, "F", [
            {
                "severity": "critical",
                "key": "openclaw.json",
                "title": "openclaw.json not found",
                "description": f"Configuration file not found at {OPENCLAW_CONFIG}",
            }
        ]
    except json.JSONDecodeError as exc:
        return 0, "F", [
            {
                "severity": "critical",
                "key": "openclaw.json",
                "title": "openclaw.json parse error",
                "description": str(exc),
            }
        ]

    score = 100
    for check in CONFIG_CHECKS:
        passed = check["check"](cfg)
        if not passed:
            score -= check["points"]
            issues.append(
                {
                    "severity": check["severity"],
                    "key": check["key"],
                    "title": check["title"],
                    "description": check["description"],
                }
            )

    score = max(0, score)
    grade = _score_to_grade(score)
    return score, grade, issues


# ---------------------------------------------------------------------------
# 2. Signature Freshness
# ---------------------------------------------------------------------------

def check_signature_freshness() -> Tuple[Dict, List[Dict]]:
    """
    Check mtime of definitions/*.json files.
    Returns (freshness_info, issues_list).
    """
    issues: List[Dict] = []
    now = datetime.now(timezone.utc)

    json_files = list(DEFINITIONS_DIR.glob("*.json"))
    if not json_files:
        return (
            {"days_since_update": None, "status": "unknown", "last_updated": None},
            [
                {
                    "severity": "high",
                    "title": "No definition files found",
                    "description": f"No *.json files found in {DEFINITIONS_DIR}",
                }
            ],
        )

    oldest_mtime = min(f.stat().st_mtime for f in json_files)
    oldest_dt = datetime.fromtimestamp(oldest_mtime, tz=timezone.utc)
    days_old = (now - oldest_dt).days

    if days_old > 90:
        status = "stale"
        issues.append(
            {
                "severity": "high",
                "title": "Threat signatures critically outdated",
                "description": (
                    f"Oldest definition file is {days_old} days old (>90 days). "
                    "New attack patterns may not be covered."
                ),
            }
        )
    elif days_old > 30:
        status = "aging"
        issues.append(
            {
                "severity": "medium",
                "title": "Threat signatures need refresh",
                "description": (
                    f"Oldest definition file is {days_old} days old (>30 days). "
                    "Run `clawhub update guardian` to get latest signatures."
                ),
            }
        )
    else:
        status = "fresh"

    return (
        {
            "last_updated": oldest_dt.date().isoformat(),
            "days_since_update": days_old,
            "status": status,
        },
        issues,
    )


# ---------------------------------------------------------------------------
# 3. OpenClaw Version Check
# ---------------------------------------------------------------------------

def _fetch_latest_npm_version() -> Optional[str]:
    """Fetch latest openclaw version from npm registry."""
    try:
        req = urllib.request.Request(
            "https://registry.npmjs.org/openclaw/latest",
            headers={"User-Agent": "guardian-local-audit/1.0"},
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode())
            return data.get("version")
    except Exception:
        return None


def _parse_version(v: str) -> Tuple[int, ...]:
    """Parse a dotted version string into a tuple of ints for comparison."""
    parts = re.split(r"[\.\-]", v)
    result = []
    for p in parts:
        try:
            result.append(int(p))
        except ValueError:
            break
    return tuple(result)


def check_openclaw_version() -> Tuple[Dict, List[Dict]]:
    """
    Run `openclaw --version`, compare with known/fetched latest.
    Returns (version_info, issues_list).
    """
    issues: List[Dict] = []

    # Get running version
    running_version: Optional[str] = None
    try:
        result = subprocess.run(
            ["openclaw", "--version"],
            capture_output=True,
            text=True,
            timeout=8,
        )
        raw = (result.stdout or result.stderr or "").strip()
        # Parse "2026.2.26" or "openclaw/2026.2.26" etc.
        m = re.search(r"(\d{4}\.\d+\.\d+(?:[\-\.]\w+)*)", raw)
        if m:
            running_version = m.group(1)
        elif raw:
            running_version = raw
    except FileNotFoundError:
        issues.append(
            {
                "severity": "medium",
                "title": "openclaw binary not found",
                "description": "Could not run `openclaw --version`. Is OpenClaw installed and on PATH?",
            }
        )
    except Exception as exc:
        issues.append(
            {
                "severity": "low",
                "title": "openclaw version check failed",
                "description": str(exc),
            }
        )

    # Get latest version (try npm registry, fall back to hardcoded)
    latest_version = _fetch_latest_npm_version() or KNOWN_LATEST_VERSION

    up_to_date = False
    if running_version and latest_version:
        try:
            up_to_date = _parse_version(running_version) >= _parse_version(latest_version)
        except Exception:
            up_to_date = running_version == latest_version

        if not up_to_date:
            issues.append(
                {
                    "severity": "medium",
                    "title": "OpenClaw update available (pending user approval)",
                    "description": (
                        f"Running {running_version}, latest is {latest_version}. "
                        "Update requires user approval — run `openclaw update` when ready."
                    ),
                }
            )

    return (
        {
            "running": running_version,
            "latest": latest_version,
            "up_to_date": up_to_date,
        },
        issues,
    )


# ---------------------------------------------------------------------------
# 4. False Positive Rate
# ---------------------------------------------------------------------------

def check_false_positive_rate() -> Tuple[Dict, List[Dict]]:
    """
    Query guardian.db for 7-day threat counts and known FP patterns.
    Returns (fp_info, issues_list).
    """
    issues: List[Dict] = []

    db_path = DB_PATH
    if not db_path.exists():
        # Try skill-local DB
        db_path = SKILL_DIR / "guardian.db"

    if not db_path.exists():
        return (
            {"rate_pct": 0.0, "total_threats_7d": 0, "fp_count_7d": 0},
            [],
        )

    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row

        total_row = conn.execute(
            "SELECT count(*) as cnt FROM threats "
            "WHERE detected_at > datetime('now', '-7 days')"
        ).fetchone()
        total = total_row["cnt"] if total_row else 0

        fp_row = conn.execute(
            "SELECT count(*) as cnt FROM threats "
            "WHERE detected_at > datetime('now', '-7 days') "
            "AND (evidence LIKE '%SOUL.md%' "
            "  OR evidence LIKE '%GATEWAY_TOKEN%' "
            "  OR evidence LIKE '%gateway token%' "
            "  OR evidence LIKE '%soul.md%' "
            "  OR evidence LIKE '%openclaw.json%')"
        ).fetchone()
        fp_count = fp_row["cnt"] if fp_row else 0
        conn.close()
    except Exception as exc:
        return (
            {"rate_pct": 0.0, "total_threats_7d": 0, "fp_count_7d": 0},
            [
                {
                    "severity": "low",
                    "title": "Could not query guardian.db",
                    "description": str(exc),
                }
            ],
        )

    rate_pct = (fp_count / total * 100) if total > 0 else 0.0

    if rate_pct > 50:
        issues.append(
            {
                "severity": "high",
                "title": "False positive rate critically high",
                "description": (
                    f"{rate_pct:.1f}% of threats in the last 7 days are known false positives "
                    f"({fp_count}/{total}). Signature tuning urgently needed."
                ),
            }
        )
    elif rate_pct > 20:
        issues.append(
            {
                "severity": "medium",
                "title": "False positive rate elevated",
                "description": (
                    f"{rate_pct:.1f}% of threats in the last 7 days are known false positives "
                    f"({fp_count}/{total}). Consider tuning signatures."
                ),
            }
        )

    return (
        {
            "rate_pct": round(rate_pct, 1),
            "total_threats_7d": total,
            "fp_count_7d": fp_count,
        },
        issues,
    )


# ---------------------------------------------------------------------------
# 5. Auto-create PM Backlog Items
# ---------------------------------------------------------------------------

def _next_bl_id(backlog: List[Dict]) -> str:
    """Return the next BL-NNN id based on current max."""
    max_num = 0
    for item in backlog:
        m = re.match(r"BL-(\d+)$", str(item.get("id", "")))
        if m:
            max_num = max(max_num, int(m.group(1)))
    return f"BL-{max_num + 1:03d}"


def _existing_titles(backlog: List[Dict]) -> set:
    return {str(item.get("title", "")).strip() for item in backlog}


def auto_create_backlog_items(findings: List[Dict]) -> List[str]:
    """
    For each CRITICAL/HIGH finding not already in backlog, create a new item.
    Returns list of created BL-xxx ids.
    """
    try:
        pm_data = json.loads(BACKLOG_PATH.read_text())
    except Exception:
        return []

    backlog: List[Dict] = pm_data.get("backlog", [])
    existing = _existing_titles(backlog)
    created_ids: List[str] = []

    for finding in findings:
        severity = finding.get("severity", "").lower()
        if severity not in ("critical", "high"):
            continue

        title = finding.get("title", "")
        if title in existing:
            continue

        new_id = _next_bl_id(backlog)
        new_item: Dict[str, Any] = {
            "id": new_id,
            "title": title,
            "type": "security",
            "priority": "high" if severity == "critical" else "medium",
            "status": "open",
            "source": "local_audit",
            "version_target": "2.4.0",
            "description": finding.get("description", ""),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        backlog.append(new_item)
        existing.add(title)
        created_ids.append(new_id)

    if created_ids:
        pm_data["backlog"] = backlog
        BACKLOG_PATH.write_text(json.dumps(pm_data, indent=2) + "\n")

    return created_ids


# ---------------------------------------------------------------------------
# 6. Main
# ---------------------------------------------------------------------------

def run_audit() -> Dict[str, Any]:
    """Execute all audit checks and return the combined result dict."""
    timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    config_score, config_grade, config_issues = check_config_score()
    freshness_info, freshness_issues = check_signature_freshness()
    version_info, version_issues = check_openclaw_version()
    fp_info, fp_issues = check_false_positive_rate()

    # Combine all findings; tag each with their source for auto-logging
    all_findings: List[Dict] = []
    for issue in config_issues:
        all_findings.append({**issue, "source": "config_check", "auto_logged": False})
    for issue in freshness_issues:
        all_findings.append({**issue, "source": "signature_freshness", "auto_logged": False})
    for issue in version_issues:
        all_findings.append({**issue, "source": "version_check", "auto_logged": False})
    for issue in fp_issues:
        all_findings.append({**issue, "source": "false_positive_rate", "auto_logged": False})

    # Auto-create backlog items for HIGH/CRITICAL findings
    created_ids = auto_create_backlog_items(all_findings)

    # Mark findings that were auto-logged
    logged_titles = set()
    for item_id in created_ids:
        # Find which titles were just logged
        pass
    # Simpler: re-mark based on what was just created
    if created_ids:
        # Read back the backlog to find which titles were created
        try:
            pm_data = json.loads(BACKLOG_PATH.read_text())
            for item in pm_data.get("backlog", []):
                if item.get("id") in created_ids:
                    logged_titles.add(item.get("title", ""))
        except Exception:
            pass

    for f in all_findings:
        if f.get("title") in logged_titles:
            f["auto_logged"] = True

    output = {
        "timestamp": timestamp,
        "config_score": config_score,
        "config_grade": config_grade,
        "signature_freshness": freshness_info,
        "openclaw_version": version_info,
        "false_positive_rate": fp_info,
        "findings": all_findings,
        "backlog_items_created": created_ids,
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(output, indent=2) + "\n")

    return output


def main() -> None:
    result = run_audit()

    # Human-readable summary to stdout
    print(f"Guardian Local Audit — {result['timestamp']}")
    print(f"Config score: {result['config_score']}/100  Grade: {result['config_grade']}")
    freshness = result["signature_freshness"]
    print(
        f"Signature freshness: {freshness['status']}  "
        f"({freshness['days_since_update']} days since update)"
    )
    ver = result["openclaw_version"]
    print(
        f"OpenClaw version: {ver['running']} (latest: {ver['latest']})  "
        f"up_to_date={ver['up_to_date']}"
    )
    fp = result["false_positive_rate"]
    print(
        f"False positive rate (7d): {fp['rate_pct']}%  "
        f"({fp['fp_count_7d']}/{fp['total_threats_7d']} threats)"
    )

    findings = result["findings"]
    if findings:
        print(f"\nFindings ({len(findings)}):")
        for f in findings:
            marker = " [backlogged]" if f.get("auto_logged") else ""
            print(f"  [{f['severity'].upper()}] {f['title']}{marker}")
    else:
        print("\nNo findings.")

    if result["backlog_items_created"]:
        print(f"\nBacklog items created: {', '.join(result['backlog_items_created'])}")

    print(f"\nOutput written to: {OUTPUT_PATH}")
    print(
        "\nAdd to crontab: 0 7 * * * cd /home/bluemax/.openclaw/workspace && "
        "/home/bluemax/.openclaw/workspace/.venv/bin/python3 "
        "skills/guardian/scripts/local_audit.py "
        ">> /tmp/guardian-local-audit.log 2>&1"
    )


if __name__ == "__main__":
    main()
