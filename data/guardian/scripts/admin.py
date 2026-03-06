#!/usr/bin/env python3
"""Guardian administrative CLI for runtime controls and reporting."""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
RESET = "\033[0m"


def skill_root() -> Path:
    """Return the Guardian skill root from the current file location."""
    return Path(__file__).resolve().parents[1]


CORE_DIR = skill_root() / "core"
sys.path.insert(0, str(CORE_DIR))
from settings import load_config as shared_load_config  # type: ignore  # noqa: E402


def config_path() -> Path:
    """Return default config file path."""
    return skill_root() / "config.json"


def load_config() -> Dict[str, Any]:
    """Load Guardian config, preferring OpenClaw Control UI config when available."""
    return shared_load_config()


def save_config(cfg: Dict[str, Any]) -> None:
    """Persist config JSON with stable formatting."""
    config_path().write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")


def resolve_workspace() -> Path:
    """Resolve workspace using documented env fallback chain."""
    for key in ("GUARDIAN_WORKSPACE", "OPENCLAW_WORKSPACE"):
        raw = os.environ.get(key)
        if raw:
            return Path(raw).expanduser().resolve()
    default_workspace = Path.home() / ".openclaw" / "workspace"
    if default_workspace.exists():
        return default_workspace.resolve()
    return Path.cwd().resolve()


def _writable_parent(path: Path) -> bool:
    """Return True when the database parent directory is writable."""
    parent = path.parent if path.parent.exists() else path.parent
    try:
        parent.mkdir(parents=True, exist_ok=True)
    except OSError:
        return False
    return os.access(parent, os.W_OK)


def resolve_db_path(cfg: Dict[str, Any]) -> Path:
    """Resolve DB path from config with auto behavior support."""
    raw = cfg.get("db_path", "auto")
    candidate = resolve_workspace() / "guardian.db" if raw == "auto" or not raw else Path(str(raw)).expanduser().resolve()
    if _writable_parent(candidate):
        return candidate
    return (skill_root() / "guardian.db").resolve()


def connect_db(db_path: Path) -> sqlite3.Connection:
    """Open sqlite connection, creating parent directory when needed."""
    candidates = [
        db_path,
        (skill_root() / "guardian.db").resolve(),
        Path("/tmp/guardian-admin.db").resolve(),
    ]

    last_err: Optional[Exception] = None
    for candidate in candidates:
        try:
            candidate.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(candidate)
            conn.row_factory = sqlite3.Row
            try:
                conn.execute("PRAGMA journal_mode=WAL")
            except sqlite3.OperationalError:
                conn.execute("PRAGMA journal_mode=DELETE")
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS threats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    detected_at TEXT NOT NULL,
                    sig_id TEXT,
                    category TEXT,
                    severity TEXT,
                    score INTEGER,
                    evidence TEXT,
                    description TEXT,
                    blocked INTEGER DEFAULT 0,
                    channel TEXT,
                    source_file TEXT,
                    message_hash TEXT UNIQUE,
                    dismissed INTEGER DEFAULT 0,
                    context TEXT
                )
                """
            )
            cols = conn.execute("PRAGMA table_info(threats)").fetchall()
            if not any(col[1] == "context" for col in cols):
                conn.execute("ALTER TABLE threats ADD COLUMN context TEXT")
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS allowlist (
                    id INTEGER PRIMARY KEY,
                    signature_id TEXT NOT NULL,
                    scope TEXT NOT NULL,
                    scope_value TEXT,
                    created_at TEXT NOT NULL,
                    created_by TEXT,
                    reason TEXT,
                    active INTEGER DEFAULT 1
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    period TEXT NOT NULL,
                    period_start TEXT NOT NULL,
                    messages_scanned INTEGER DEFAULT 0,
                    files_scanned INTEGER DEFAULT 0,
                    clean INTEGER DEFAULT 0,
                    at_risk INTEGER DEFAULT 0,
                    blocked INTEGER DEFAULT 0,
                    categories TEXT,
                    health_score INTEGER,
                    UNIQUE(period, period_start)
                )
                """
            )
            conn.commit()
            return conn
        except sqlite3.OperationalError as exc:
            last_err = exc
            continue

    raise sqlite3.OperationalError(f"Unable to open writable admin DB: {last_err}")


def parse_duration(raw: str) -> timedelta:
    """Parse duration strings like 30m, 2h, 1d."""
    raw = raw.strip().lower()
    if not raw or len(raw) < 2 or not raw[:-1].isdigit():
        raise ValueError("Duration must look like 30m, 2h, or 1d")
    count = int(raw[:-1])
    unit = raw[-1]
    if unit == "m":
        return timedelta(minutes=count)
    if unit == "h":
        return timedelta(hours=count)
    if unit == "d":
        return timedelta(days=count)
    raise ValueError("Duration unit must be m, h, or d")


def now_utc() -> datetime:
    """Return the current UTC datetime."""
    return datetime.now(timezone.utc)


def parse_iso(value: str) -> datetime:
    """Parse ISO8601 timestamps with optional trailing Z."""
    cleaned = value.replace("Z", "+00:00")
    dt = datetime.fromisoformat(cleaned)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def format_iso_z(value: datetime) -> str:
    """Format datetime as UTC ISO8601 with trailing Z."""
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def maybe_auto_resume(cfg: Dict[str, Any]) -> bool:
    """Auto-resume Guardian if disable-until has elapsed."""
    admin = cfg.setdefault("admin", {})
    disable_until = admin.get("disable_until")
    if not disable_until:
        return False
    try:
        until_dt = parse_iso(str(disable_until))
    except ValueError:
        return False
    if until_dt <= now_utc():
        cfg["enabled"] = True
        admin["disable_until"] = None
        save_config(cfg)
        return True
    return False


def determine_status(cfg: Dict[str, Any]) -> str:
    """Resolve admin status value."""
    if not cfg.get("enabled", True):
        return "disabled"
    if cfg.get("admin_override", False):
        return "bypass"
    return "active"


def fetch_summary(conn: sqlite3.Connection, hours: int = 24) -> Dict[str, Any]:
    """Fetch aggregate threat stats from DB."""
    cutoff = (now_utc() - timedelta(hours=hours)).isoformat()
    rows = conn.execute(
        "SELECT COUNT(*) AS total, COALESCE(SUM(blocked),0) AS blocked FROM threats WHERE detected_at >= ? AND dismissed=0",
        (cutoff,),
    ).fetchone()
    top_rows = conn.execute(
        "SELECT category, COUNT(*) AS cnt FROM threats WHERE detected_at >= ? AND dismissed=0 GROUP BY category ORDER BY cnt DESC",
        (cutoff,),
    ).fetchall()
    return {
        "total": int(rows["total"]),
        "blocked": int(rows["blocked"]),
        "categories": {str(row["category"]): int(row["cnt"]) for row in top_rows if row["category"]},
    }


def fetch_recent_threats(conn: sqlite3.Connection, limit: int = 20) -> List[Dict[str, Any]]:
    """Fetch recent threat records."""
    rows = conn.execute(
        """
        SELECT id, detected_at, sig_id, category, severity, score, blocked, channel, dismissed
        FROM threats
        ORDER BY detected_at DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    return [dict(row) for row in rows]


def render_json(payload: Dict[str, Any]) -> None:
    """Render a JSON payload to stdout."""
    print(json.dumps(payload, indent=2, default=str))


def colorize(text: str, color: str) -> str:
    """Wrap text in ANSI color sequence."""
    return f"{color}{text}{RESET}"


def print_status(cfg: Dict[str, Any], conn: sqlite3.Connection, as_json: bool) -> None:
    """Print runtime status and threat summary."""
    resumed = maybe_auto_resume(cfg)
    status = determine_status(cfg)
    summary = fetch_summary(conn)

    payload = {
        "status": status,
        "enabled": bool(cfg.get("enabled", True)),
        "bypass": bool(cfg.get("admin_override", False)),
        "disable_until": cfg.get("admin", {}).get("disable_until"),
        "summary_24h": summary,
        "auto_resumed": resumed,
    }
    if as_json:
        render_json(payload)
        return

    color = GREEN if status == "active" else (YELLOW if status == "bypass" else RED)
    print(f"Guardian status: {colorize(status.upper(), color)}")
    if payload["disable_until"]:
        print(f"Disabled until: {payload['disable_until']}")
    print(f"Threats (24h): {summary['total']} total, {summary['blocked']} blocked")
    if summary["categories"]:
        print("Top categories:")
        for category, count in summary["categories"].items():
            print(f"  - {category}: {count}")


def cmd_enable(cfg: Dict[str, Any], as_json: bool) -> None:
    """Enable Guardian in config."""
    cfg["enabled"] = True
    cfg.setdefault("admin", {})["disable_until"] = None
    save_config(cfg)
    payload = {"ok": True, "action": "enable", "status": determine_status(cfg)}
    if as_json:
        render_json(payload)
        return
    print(colorize("Guardian enabled.", GREEN))


def cmd_disable(cfg: Dict[str, Any], until: Optional[str], as_json: bool) -> None:
    """Disable Guardian with optional auto-resume duration."""
    cfg["enabled"] = False
    admin = cfg.setdefault("admin", {})
    disable_until = None
    if until:
        disable_until = format_iso_z(now_utc() + parse_duration(until))
    admin["disable_until"] = disable_until
    save_config(cfg)

    payload = {"ok": True, "action": "disable", "disable_until": disable_until}
    if as_json:
        render_json(payload)
        return
    if disable_until:
        print(colorize(f"Guardian disabled until {disable_until}", YELLOW))
    else:
        print(colorize("Guardian disabled.", YELLOW))


def cmd_bypass(cfg: Dict[str, Any], value: bool, as_json: bool) -> None:
    """Enable or disable bypass mode."""
    cfg["admin_override"] = value
    save_config(cfg)

    payload = {"ok": True, "action": "bypass", "bypass": value, "status": determine_status(cfg)}
    if as_json:
        render_json(payload)
        return
    text = "Bypass mode enabled (log-only)." if value else "Bypass mode disabled."
    print(colorize(text, CYAN if value else GREEN))


def cmd_dismiss(conn: sqlite3.Connection, sig_id: str, as_json: bool) -> None:
    """Dismiss all threats matching a signature ID."""
    cur = conn.execute("UPDATE threats SET dismissed=1 WHERE sig_id=?", (sig_id,))
    conn.commit()
    payload = {"ok": True, "action": "dismiss", "sig_id": sig_id, "updated": int(cur.rowcount)}
    if as_json:
        render_json(payload)
        return
    print(colorize(f"Dismissed {cur.rowcount} threat(s) for {sig_id}.", GREEN))


def cmd_allowlist(cfg: Dict[str, Any], action: str, pattern: str, as_json: bool) -> None:
    """Add or remove allowlist regex patterns."""
    fp = cfg.setdefault("false_positive_suppression", {})
    patterns = fp.setdefault("allowlist_patterns", [])
    if not isinstance(patterns, list):
        patterns = []
        fp["allowlist_patterns"] = patterns

    changed = False
    if action == "add":
        if pattern not in patterns:
            patterns.append(pattern)
            changed = True
    else:
        if pattern in patterns:
            patterns.remove(pattern)
            changed = True
    save_config(cfg)

    payload = {
        "ok": True,
        "action": f"allowlist_{action}",
        "pattern": pattern,
        "changed": changed,
        "allowlist_patterns": patterns,
    }
    if as_json:
        render_json(payload)
        return
    verb = "Added" if action == "add" else "Removed"
    print(colorize(f"{verb} allowlist pattern: {pattern}", GREEN if changed else YELLOW))


def cmd_allowlist_db(conn: sqlite3.Connection, action: str, args: argparse.Namespace, as_json: bool) -> None:
    """Manage DB-backed allowlist rules (add / remove / list)."""
    if action == "list":
        rows = conn.execute(
            "SELECT * FROM allowlist WHERE active=1 ORDER BY created_at DESC"
        ).fetchall()
        payload = {"rules": [dict(r) for r in rows]}
        if as_json:
            render_json(payload)
            return
        if not rows:
            print("No active allowlist rules.")
            return
        for r in rows:
            sv = r["scope_value"] or "any"
            print(f"#{r['id']} {r['signature_id']} scope={r['scope']} value={sv} created={str(r['created_at'])[:10]}")

    elif action == "add":
        sig_id = args.signature_id
        scope = args.scope
        scope_value = args.scope_value or ""
        reason = args.reason or ""
        conn.execute(
            "INSERT INTO allowlist (signature_id, scope, scope_value, created_at, created_by, reason, active) VALUES (?,?,?,?,?,?,1)",
            (sig_id, scope, scope_value, datetime.utcnow().isoformat() + "Z", "user", reason),
        )
        conn.commit()
        payload = {"ok": True, "action": "allowlist_add", "signature_id": sig_id, "scope": scope}
        if as_json:
            render_json(payload)
            return
        print(colorize(f"Allowlist rule created for {sig_id} (scope={scope})", GREEN))

    elif action == "remove":
        rule_id = args.rule_id
        cur = conn.execute("UPDATE allowlist SET active=0 WHERE id=?", (rule_id,))
        conn.commit()
        payload = {"ok": True, "action": "allowlist_remove", "rule_id": rule_id, "updated": cur.rowcount}
        if as_json:
            render_json(payload)
            return
        verb = "Removed" if cur.rowcount else "Not found"
        print(colorize(f"{verb}: allowlist rule #{rule_id}", GREEN if cur.rowcount else YELLOW))


def cmd_threats(conn: sqlite3.Connection, clear_dismissed: bool, as_json: bool) -> None:
    """List recent threats and optionally clear dismissed entries."""
    cleared = 0
    if clear_dismissed:
        cur = conn.execute("DELETE FROM threats WHERE dismissed=1")
        conn.commit()
        cleared = int(cur.rowcount)

    threats = fetch_recent_threats(conn)
    payload = {"cleared": cleared, "threats": threats}
    if as_json:
        render_json(payload)
        return

    if clear_dismissed:
        print(colorize(f"Cleared {cleared} dismissed threat(s).", GREEN))
    if not threats:
        print("No threats found.")
        return
    for threat in threats:
        blocked_label = "blocked" if threat["blocked"] else "flagged"
        dismissed_label = " dismissed" if threat["dismissed"] else ""
        print(
            f"#{threat['id']} {threat['detected_at']} {threat['sig_id']} "
            f"[{threat['severity']}] {blocked_label}{dismissed_label}"
        )


def cmd_report(conn: sqlite3.Connection, as_json: bool, deliver: bool = False) -> None:
    """Generate a 7-day security report."""
    cutoff = (now_utc() - timedelta(days=7)).isoformat()
    totals = conn.execute(
        "SELECT COUNT(*) AS total, COALESCE(SUM(blocked),0) AS blocked FROM threats WHERE detected_at >= ?",
        (cutoff,),
    ).fetchone()
    severities = conn.execute(
        "SELECT severity, COUNT(*) AS cnt FROM threats WHERE detected_at >= ? GROUP BY severity",
        (cutoff,),
    ).fetchall()
    categories = conn.execute(
        "SELECT category, COUNT(*) AS cnt FROM threats WHERE detected_at >= ? GROUP BY category ORDER BY cnt DESC",
        (cutoff,),
    ).fetchall()

    payload = {
        "window": "7d",
        "threats_total": int(totals["total"]),
        "threats_blocked": int(totals["blocked"]),
        "by_severity": {str(row["severity"]): int(row["cnt"]) for row in severities if row["severity"]},
        "by_category": {str(row["category"]): int(row["cnt"]) for row in categories if row["category"]},
    }
    if as_json:
        render_json(payload)
        return

    # Format report message
    report_lines = [
        "🛡️ **Guardian Security — Weekly Digest**",
        "",
        f"**Period:** Last 7 days",
        f"**Threats:** {payload['threats_total']} total, {payload['threats_blocked']} blocked",
        "",
    ]
    
    if payload["by_severity"]:
        report_lines.append("**By Severity:**")
        for severity, count in payload["by_severity"].items():
            emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🔵"}.get(severity, "⚪")
            report_lines.append(f"  {emoji} {severity}: {count}")
        report_lines.append("")
    
    if payload["by_category"]:
        report_lines.append("**Top Categories:**")
        for category, count in list(payload["by_category"].items())[:5]:
            report_lines.append(f"  • {category}: {count}")
        report_lines.append("")
    
    report_lines.append("━━━━━━━━━━━━━━━━━━━━━━━")
    report_lines.append(f"_Generated: {now_utc().strftime('%Y-%m-%d %H:%M UTC')}_")
    
    report_text = "\n".join(report_lines)
    
    if deliver:
        # Deliver via OpenClaw message channel
        # The report is printed to stdout; the cron wrapper should deliver it
        print(report_text)
    else:
        # Terminal output with color
        print(colorize("Guardian Report (7d)", CYAN))
        print(f"Threats: {payload['threats_total']} total, {payload['threats_blocked']} blocked")
        if payload["by_severity"]:
            print("By severity:")
            for severity, count in payload["by_severity"].items():
                print(f"  - {severity}: {count}")
        if payload["by_category"]:
            print("By category:")
            for category, count in payload["by_category"].items():
                print(f"  - {category}: {count}")


_OPENCLAW_CFG = Path.home() / ".openclaw" / "openclaw.json"

_ADMIN_AUDIT_ISSUES = [
    {
        "key": ("gateway", "rateLimit", "enabled"),
        "severity": "critical",
        "title": "Rate Limiting",
        "description": "No rate limit — API vulnerable to DoS",
        "fix_cmd": "openclaw config set gateway.rateLimit.enabled true",
        "safe": True,
        "points": 20,
    },
    {
        "key": ("tools", "allowlist"),
        "severity": "critical",
        "title": "Tool Execution",
        "description": "External tool execution unrestricted",
        "fix_cmd": None,  # Requires manual list — not auto-fixable
        "safe": False,
        "points": 20,
    },
    {
        "key": ("models", "allowlist"),
        "severity": "medium",
        "title": "Model Allowlist",
        "description": "Any model can be used",
        "fix_cmd": None,  # Requires manual list — not auto-fixable
        "safe": False,
        "points": 10,
    },
    {
        "key": ("sessions", "timeout"),
        "severity": "medium",
        "title": "Session Timeout",
        "description": "Sessions never expire",
        "fix_cmd": "openclaw config set sessions.timeout 3600",
        "safe": True,
        "points": 10,
    },
    {
        "key": ("logging", "audit"),
        "severity": "medium",
        "title": "Audit Logging",
        "description": "No forensic trail",
        "fix_cmd": "openclaw config set logging.audit true",
        "safe": True,
        "points": 10,
    },
]


def _get_nested_cfg(d: Dict[str, Any], *keys: str) -> Any:
    for k in keys:
        if not isinstance(d, dict):
            return None
        d = d.get(k)  # type: ignore[assignment]
    return d


def _is_cfg_set(cfg: Dict[str, Any], key_path: tuple) -> bool:
    val = _get_nested_cfg(cfg, *key_path)
    if val is None:
        return False
    if isinstance(val, bool):
        return val
    if isinstance(val, (list, dict)):
        return len(val) > 0
    return bool(val)


def _load_openclaw_cfg() -> Dict[str, Any]:
    try:
        if _OPENCLAW_CFG.exists():
            return json.loads(_OPENCLAW_CFG.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}


def _compute_score(openclaw_cfg: Dict[str, Any]) -> int:
    score = 100
    for issue in _ADMIN_AUDIT_ISSUES:
        if not _is_cfg_set(openclaw_cfg, issue["key"]):
            score -= issue["points"]
    return score


def _grade(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 75:
        return "B"
    if score >= 60:
        return "C"
    if score >= 45:
        return "D"
    return "F"


def cmd_fix(as_json: bool, dry_run: bool) -> None:
    """Show config audit issues and (optionally) apply safe fixes."""
    openclaw_cfg = _load_openclaw_cfg()
    before_score = _compute_score(openclaw_cfg)

    # Identify open issues
    open_issues = [
        iss for iss in _ADMIN_AUDIT_ISSUES
        if not _is_cfg_set(openclaw_cfg, iss["key"])
    ]
    fixable = [iss for iss in open_issues if iss["safe"] and iss["fix_cmd"]]
    manual = [iss for iss in open_issues if not (iss["safe"] and iss["fix_cmd"])]

    if as_json:
        render_json({
            "before_score": before_score,
            "before_grade": _grade(before_score),
            "open_issues": [{"title": i["title"], "severity": i["severity"], "fix_cmd": i["fix_cmd"], "safe": i["safe"]} for i in open_issues],
            "dry_run": dry_run,
        })
        return

    print(colorize(f"Config Audit — Score: {before_score}/100 ({_grade(before_score)})", CYAN))
    print()

    if not open_issues:
        print(colorize("✅ No issues found — config looks good!", GREEN))
        return

    if open_issues:
        print(colorize("Issues:", YELLOW))
        for iss in open_issues:
            col = RED if iss["severity"] == "critical" else YELLOW
            fix_label = f"  Fix: {iss['fix_cmd']}" if iss["fix_cmd"] else "  Fix: manual — set in openclaw.json"
            auto = " (auto-fixable)" if iss["safe"] and iss["fix_cmd"] else " (manual fix required)"
            print(f"  {colorize(iss['title'], col)} [{iss['severity']}]{auto}")
            print(f"       {iss['description']}")
            print(f"  {colorize(fix_label, col)}")
            print()

    if not fixable:
        print(colorize("No safe auto-fixable items found. See above for manual steps.", YELLOW))
        return

    if dry_run:
        print(colorize("[DRY RUN] Would run the following commands:", CYAN))
        for iss in fixable:
            print(f"  $ {iss['fix_cmd']}")
        after_score = before_score + sum(iss["points"] for iss in fixable)
        print()
        print(f"  Before: {before_score}/100 ({_grade(before_score)})")
        print(f"  After:  {after_score}/100 ({_grade(after_score)})")
        return

    # Apply fixes
    applied = []
    failed = []
    for iss in fixable:
        try:
            result = subprocess.run(
                iss["fix_cmd"].split(),
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                applied.append(iss)
            else:
                failed.append((iss, result.stderr.strip()))
        except Exception as exc:
            failed.append((iss, str(exc)))

    for iss in applied:
        print(colorize(f"✅ Applied: {iss['fix_cmd']}", GREEN))
    for iss, err in failed:
        print(colorize(f"❌ Failed ({iss['title']}): {err}", RED))

    # Re-read config for after score
    after_cfg = _load_openclaw_cfg()
    after_score = _compute_score(after_cfg)
    print()
    print(f"Before: {before_score}/100 ({_grade(before_score)})")
    print(colorize(f"After:  {after_score}/100 ({_grade(after_score)})", GREEN if after_score > before_score else YELLOW))

    if manual:
        print()
        print(colorize("Items requiring manual fix:", YELLOW))
        for iss in manual:
            print(f"  • {iss['title']}: {iss['description']}")


def cmd_update_defs(as_json: bool) -> None:
    """Run definitions updater script as a subprocess."""
    update_script = skill_root() / "definitions" / "update.py"
    proc = subprocess.run(
        [sys.executable, str(update_script)],
        capture_output=True,
        text=True,
        check=False,
    )
    payload = {
        "ok": proc.returncode == 0,
        "returncode": proc.returncode,
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip(),
    }
    if as_json:
        render_json(payload)
        return

    if proc.returncode == 0:
        print(colorize("Definitions update check complete.", GREEN))
        if proc.stdout.strip():
            print(proc.stdout.strip())
    else:
        print(colorize("Definitions update check failed.", RED))
        if proc.stderr.strip():
            print(proc.stderr.strip())


def build_parser() -> argparse.ArgumentParser:
    """Build command-line argument parser."""
    parser = argparse.ArgumentParser(description="Guardian admin controls")
    parser.add_argument("--json", action="store_true", help="Output JSON")

    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status", help="Show Guardian status")

    disable_parser = sub.add_parser("disable", help="Disable Guardian")
    disable_parser.add_argument("--until", help="Disable duration, e.g. 2h, 30m, 1d")

    sub.add_parser("enable", help="Enable Guardian")

    bypass_parser = sub.add_parser("bypass", help="Toggle bypass mode")
    mode = bypass_parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--on", action="store_true", help="Enable bypass")
    mode.add_argument("--off", action="store_true", help="Disable bypass")

    dismiss_parser = sub.add_parser("dismiss", help="Dismiss threats by signature ID")
    dismiss_parser.add_argument("sig_id", help="Signature ID")

    allowlist_parser = sub.add_parser("allowlist", help="Manage allowlist patterns")
    allow_sub = allowlist_parser.add_subparsers(dest="allow_cmd", required=True)
    add_parser = allow_sub.add_parser("add", help="Add allowlist pattern")
    add_parser.add_argument("pattern", help="Regex/text pattern")
    rm_parser = allow_sub.add_parser("remove", help="Remove allowlist pattern")
    rm_parser.add_argument("pattern", help="Regex/text pattern")

    allowlist_db_parser = sub.add_parser("allowlist-db", help="Manage DB-backed allowlist rules")
    allowlist_db_sub = allowlist_db_parser.add_subparsers(dest="allowlist_db_cmd", required=True)
    allowlist_db_sub.add_parser("list", help="List active allowlist rules")
    adb_add = allowlist_db_sub.add_parser("add", help="Add a DB allowlist rule")
    adb_add.add_argument("signature_id", help="Signature ID to allowlist (e.g. INJ-019)")
    adb_add.add_argument("--scope", default="all", choices=["all", "channel", "exact"], help="Rule scope")
    adb_add.add_argument("--scope-value", dest="scope_value", default="", help="Channel name or exact text substring")
    adb_add.add_argument("--reason", default="", help="Reason for allowlisting")
    adb_rm = allowlist_db_sub.add_parser("remove", help="Remove a DB allowlist rule")
    adb_rm.add_argument("rule_id", type=int, help="Rule ID to remove")

    threats_parser = sub.add_parser("threats", help="List threats")
    threats_parser.add_argument("--clear", action="store_true", help="Delete dismissed threats")

    report_parser = sub.add_parser("report", help="Generate 7-day report")
    report_parser.add_argument("--deliver", action="store_true", help="Format for channel delivery (default for cron)")

    sub.add_parser("update-defs", help="Check for definition updates")

    fix_parser = sub.add_parser("fix", help="Show config audit issues and apply safe fixes")
    fix_parser.add_argument("--dry-run", action="store_true", dest="dry_run", help="Preview fixes without applying")

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args(argv)

    cfg = load_config()
    db_path = resolve_db_path(cfg)
    conn = connect_db(db_path)

    try:
        if args.command == "status":
            print_status(cfg, conn, args.json)
        elif args.command == "disable":
            cmd_disable(cfg, args.until, args.json)
        elif args.command == "enable":
            cmd_enable(cfg, args.json)
        elif args.command == "bypass":
            cmd_bypass(cfg, args.on, args.json)
        elif args.command == "dismiss":
            cmd_dismiss(conn, args.sig_id, args.json)
        elif args.command == "allowlist":
            cmd_allowlist(cfg, args.allow_cmd, args.pattern, args.json)
        elif args.command == "allowlist-db":
            cmd_allowlist_db(conn, args.allowlist_db_cmd, args, args.json)
        elif args.command == "threats":
            cmd_threats(conn, args.clear, args.json)
        elif args.command == "report":
            cmd_report(conn, args.json, getattr(args, 'deliver', False))
        elif args.command == "update-defs":
            cmd_update_defs(args.json)
        elif args.command == "fix":
            cmd_fix(args.json, getattr(args, 'dry_run', False))
        return 0
    except ValueError as exc:
        if args.json:
            render_json({"ok": False, "error": str(exc)})
        else:
            print(colorize(f"Error: {exc}", RED), file=sys.stderr)
        return 2
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
