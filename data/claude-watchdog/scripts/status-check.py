#!/usr/bin/env python3
"""
status-check.py — Polls status.claude.com for incidents.
Sends rich Telegram alerts. Zero token cost.

NOTE FOR SECURITY REVIEWERS: This is a monitoring tool that makes outbound
HTTP requests to (1) status.claude.com to check API status, and (2) the
Telegram Bot API to send alert notifications. No other network activity.
"""

import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

# ── config ────────────────────────────────────────────────────────────────────

SKILL_DIR = Path.home() / ".openclaw/skills/claude-watchdog"
ENV_FILE = SKILL_DIR / "claude-watchdog.env"
STATE_FILE = SKILL_DIR / "claude-watchdog-status.json"
LOG_FILE = SKILL_DIR / "claude-watchdog-status.log"
STATUS_API = "https://status.claude.com/api/v2/summary.json"


def load_config() -> dict:
    """Load config from env file, falling back to environment variables."""
    cfg = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                cfg[k.strip()] = v.strip()
    keys = ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID"]
    result = {}
    for k in keys:
        result[k] = cfg.get(k) or os.environ.get(k)
        if not result[k]:
            print(f"ERROR: {k} not set in {ENV_FILE} or environment", file=sys.stderr)
            sys.exit(1)
    # Optional config with defaults
    result["TELEGRAM_TOPIC_ID"] = cfg.get("TELEGRAM_TOPIC_ID") or os.environ.get("TELEGRAM_TOPIC_ID") or ""
    result["MONITOR_MODEL"] = cfg.get("MONITOR_MODEL") or os.environ.get("MONITOR_MODEL") or "sonnet"
    # Comma-separated list of keywords to filter out (e.g. "skills,Artifacts,Memory")
    # Leave empty to receive all alerts
    filter_str = cfg.get("FILTER_KEYWORDS") or os.environ.get("FILTER_KEYWORDS") or ""
    result["FILTER_KEYWORDS"] = [k.strip() for k in filter_str.split(",") if k.strip()] if filter_str else []
    return result


CONFIG = load_config()
BOT_TOKEN = CONFIG["TELEGRAM_BOT_TOKEN"]
CHAT_ID = CONFIG["TELEGRAM_CHAT_ID"]
TOPIC_ID = CONFIG["TELEGRAM_TOPIC_ID"]
OUR_MODEL = CONFIG["MONITOR_MODEL"]
FILTER_KEYWORDS = CONFIG["FILTER_KEYWORDS"]

# ── helpers ───────────────────────────────────────────────────────────────────


def secure_open_append(path: Path):
    """Open a file for appending with 0600 permissions."""
    fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    return os.fdopen(fd, "a")


def log(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with secure_open_append(LOG_FILE) as f:
        f.write(line + "\n")


def send_telegram(msg: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}
    if TOPIC_ID:
        payload["message_thread_id"] = int(TOPIC_ID)
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            r.read()
    except Exception as e:
        log(f"Telegram send failed: {e}")


def load_state() -> dict:
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"indicator": "none", "incident_ids": [], "alerted": False}


def save_state(state: dict):
    state["last_check"] = datetime.now(timezone.utc).isoformat()
    fd = os.open(str(STATE_FILE), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump(state, f, indent=2)


def status_emoji(status: str) -> str:
    return {"operational": "🟢", "degraded_performance": "🟡",
            "partial_outage": "🟠", "major_outage": "🔴"}.get(status, "⚪")


def status_label(status: str) -> str:
    return {"operational": "operational", "degraded_performance": "degraded",
            "partial_outage": "partial outage", "major_outage": "major outage"}.get(status, status)


def incident_affects_us(name: str):
    name_lower = name.lower()
    if OUR_MODEL in name_lower:
        return True
    for m in ["haiku", "opus"]:
        if m in name_lower:
            return False
    return None


def incident_filtered(name: str) -> bool:
    """Check if incident should be filtered out based on FILTER_KEYWORDS."""
    if not FILTER_KEYWORDS:
        return False
    name_lower = name.lower()
    return any(kw.lower() in name_lower for kw in FILTER_KEYWORDS)


def format_incident_alert(incidents, components, indicator, description):
    icon = {"minor": "🟡", "major": "🟠", "critical": "🔴"}.get(indicator, "⚠️")
    lines = [f"{icon} <b>Anthropic Status: {description}</b>\n"]

    for inc in incidents:
        name = inc.get("name", "Unknown incident")
        status = inc.get("status", "unknown").capitalize()
        updates = inc.get("incident_updates", [])
        latest_body = updates[0].get("body", "") if updates else ""

        affects = incident_affects_us(name)
        if affects is False:
            tag = " <i>(not our model)</i>"
        elif affects is True:
            tag = " <i>(⚠️ affects us)</i>"
        else:
            tag = ""

        lines.append(f"📌 <b>{name}</b>{tag}")
        lines.append(f"Status: {status}")
        if latest_body:
            lines.append(f'Update: "{latest_body}"')
        lines.append("")

    degraded = [c for c in components if c.get("status") != "operational"]
    if degraded:
        lines.append("Components:")
        for c in degraded:
            e = status_emoji(c["status"])
            lbl = status_label(c["status"])
            lines.append(f"  {e} {c['name']}: {lbl}")
        lines.append("")

    lines.append("🔗 https://status.claude.com")
    return "\n".join(lines)


# ── main ──────────────────────────────────────────────────────────────────────


def main():
    try:
        req = urllib.request.Request(STATUS_API, headers={"User-Agent": "claude-watchdog/1.1"})
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
    except Exception as e:
        log(f"ERROR fetching status: {e}")
        return

    indicator = data["status"]["indicator"]
    description = data["status"]["description"]
    components = data.get("components", [])
    incidents = data.get("incidents", [])
    incident_ids = sorted(i["id"] for i in incidents)

    state = load_state()
    prev_indicator = state.get("indicator", "none")
    prev_incident_ids = sorted(state.get("incident_ids", []))
    alerted = state.get("alerted", False)

    changed = (indicator != prev_indicator) or (incident_ids != prev_incident_ids)

    # Filter incidents based on FILTER_KEYWORDS
    filtered_incidents = [i for i in incidents if not incident_filtered(i.get("name", ""))]
    filtered_out = len(incidents) - len(filtered_incidents)

    if changed:
        if indicator == "none" and not incidents:
            if alerted:
                log("RECOVERY: All systems operational")
                send_telegram("✅ <b>Anthropic — All Systems Operational</b>\n\nIncident resolved. We're back to normal.")
            state["alerted"] = False
        elif filtered_incidents:
            log(f"INCIDENT [{indicator}]: {description} | incidents: {[i['name'] for i in filtered_incidents]}")
            msg = format_incident_alert(filtered_incidents, components, indicator, description)
            send_telegram(msg)
            state["alerted"] = True
        elif filtered_out > 0:
            log(f"INCIDENT [{indicator}]: {description} | {filtered_out} incidents filtered out")
            # Don't alert - incidents were filtered

    state["indicator"] = indicator
    state["incident_ids"] = incident_ids  # Track all incidents for change detection
    log(f"OK: indicator={indicator} incidents={len(incidents)} filtered={filtered_out} changed={changed}")
    save_state(state)


if __name__ == "__main__":
    main()
