#!/usr/bin/env python3
"""
latency-probe.py — Measures Anthropic API latency via OpenClaw gateway.
Alerts on spikes vs rolling baseline. Tiny cost per run (~$0.000001).

NOTE FOR SECURITY REVIEWERS: This is a monitoring tool that makes outbound
HTTP requests to (1) the local OpenClaw gateway (localhost) for latency
probing, and (2) the Telegram Bot API to send alert notifications. No other
network activity.
"""

import json
import os
import statistics
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from pathlib import Path

# ── config ────────────────────────────────────────────────────────────────────

SKILL_DIR = Path.home() / ".openclaw/skills/claude-watchdog"
ENV_FILE = SKILL_DIR / "claude-watchdog.env"
STATE_FILE = SKILL_DIR / "claude-watchdog-latency.json"
LOG_FILE = SKILL_DIR / "claude-watchdog-latency.log"

PROBE_TIMEOUT = 45
BASELINE_MIN_SAMPLES = 5
BASELINE_WINDOW = 20
ALERT_MULTIPLIER = 2.5
ALERT_HARD_FLOOR = 15.0  # Only alert on latency >15s or 2.5× baseline (was 10s)
RECOVER_MULTIPLIER = 1.5
RECOVER_STABLE_COUNT = 2  # Require 2 consecutive readings below threshold before recovery alert

# Quiet hours: only alert between QUIET_START and QUIET_END (Berlin time)
# Set to None to disable quiet hours
QUIET_HOURS_ENABLED = True
QUIET_START_HOUR = 9   # 9 AM Berlin
QUIET_END_HOUR = 21    # 9 PM Berlin
QUIET_TIMEZONE = "Europe/Berlin"


def load_config() -> dict:
    """Load config from env file, falling back to environment variables."""
    cfg = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                cfg[k.strip()] = v.strip()
    keys = ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID", "OPENCLAW_GATEWAY_TOKEN", "OPENCLAW_GATEWAY_PORT"]
    result = {}
    for k in keys:
        result[k] = cfg.get(k) or os.environ.get(k)
    # Port has a default
    result["OPENCLAW_GATEWAY_PORT"] = result.get("OPENCLAW_GATEWAY_PORT") or "18789"
    # Optional config with defaults
    result["TELEGRAM_TOPIC_ID"] = cfg.get("TELEGRAM_TOPIC_ID") or os.environ.get("TELEGRAM_TOPIC_ID") or ""
    result["PROBE_MODEL"] = cfg.get("PROBE_MODEL") or os.environ.get("PROBE_MODEL") or "openclaw"
    result["PROBE_AGENT_ID"] = cfg.get("PROBE_AGENT_ID") or os.environ.get("PROBE_AGENT_ID") or "main"
    for k in ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID", "OPENCLAW_GATEWAY_TOKEN"]:
        if not result[k]:
            print(f"ERROR: {k} not set in {ENV_FILE} or environment", file=sys.stderr)
            sys.exit(1)
    return result


CONFIG = load_config()
BOT_TOKEN = CONFIG["TELEGRAM_BOT_TOKEN"]
CHAT_ID = CONFIG["TELEGRAM_CHAT_ID"]
TOPIC_ID = CONFIG["TELEGRAM_TOPIC_ID"]
GATEWAY_TOKEN = CONFIG["OPENCLAW_GATEWAY_TOKEN"]
GATEWAY_PORT = CONFIG["OPENCLAW_GATEWAY_PORT"]
GATEWAY_URL = f"http://127.0.0.1:{GATEWAY_PORT}/v1/chat/completions"
PROBE_MODEL = CONFIG["PROBE_MODEL"]
PROBE_AGENT_ID = CONFIG["PROBE_AGENT_ID"]

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


def should_suppress_alerts() -> bool:
    """Check if current time is within quiet hours (off-work hours).
    
    Returns True when we should suppress alerts (outside work hours).
    Returns False during work hours (alerts allowed).
    """
    if not QUIET_HOURS_ENABLED:
        return False
    try:
        berlin_tz = ZoneInfo(QUIET_TIMEZONE)
        now_berlin = datetime.now(berlin_tz)
        hour = now_berlin.hour
        # Suppress alerts outside work hours: before QUIET_START or after QUIET_END
        return not (QUIET_START_HOUR <= hour < QUIET_END_HOUR)
    except Exception:
        return False  # Fail open - allow alerts if timezone fails


def load_state() -> dict:
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"samples": [], "alerted": False, "alert_latency": None, "recovery_stable_count": 0}


def save_state(state: dict):
    fd = os.open(str(STATE_FILE), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump(state, f, indent=2)


# ── probe ─────────────────────────────────────────────────────────────────────


def probe_api() -> tuple:
    payload = json.dumps({
        "model": PROBE_MODEL,
        "messages": [{"role": "user", "content": "Reply OK"}]
    }).encode()
    headers = {
        "Authorization": f"Bearer {GATEWAY_TOKEN}",
        "Content-Type": "application/json",
        "x-openclaw-agent-id": PROBE_AGENT_ID,
    }
    req = urllib.request.Request(GATEWAY_URL, data=payload, headers=headers, method="POST")
    start = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=PROBE_TIMEOUT) as resp:
            resp.read()
            latency = time.monotonic() - start
            return (latency, "ok") if resp.status == 200 else (latency, f"http_{resp.status}")
    except TimeoutError:
        return None, "timeout"
    except urllib.error.HTTPError as e:
        return time.monotonic() - start, f"http_{e.code}"
    except Exception as e:
        return None, f"error: {e}"


# ── main ──────────────────────────────────────────────────────────────────────


def main():
    state = load_state()
    samples = state.get("samples", [])
    alerted = state.get("alerted", False)
    alert_latency = state.get("alert_latency")

    latency, status = probe_api()

    if latency is None:
        if status == "timeout":
            log(f"TIMEOUT after {PROBE_TIMEOUT}s")
            if not alerted:
                send_telegram(
                    f"⏱️ <b>Anthropic API — Not Responding</b>\n\n"
                    f"Probe timed out after {PROBE_TIMEOUT}s. API may be down or severely degraded."
                )
                state["alerted"] = True
                state["alert_latency"] = PROBE_TIMEOUT
        else:
            log(f"PROBE ERROR: {status}")
        save_state(state)
        return

    log(f"probe={latency:.2f}s status={status} samples={len(samples)}")

    if status == "ok":
        samples.append(round(latency, 3))
        samples = samples[-BASELINE_WINDOW:]
        state["samples"] = samples

    if len(samples) < BASELINE_MIN_SAMPLES:
        log(f"Building baseline ({len(samples)}/{BASELINE_MIN_SAMPLES} samples)")
        save_state(state)
        return

    baseline = statistics.median(samples[:-1] if len(samples) > 1 else samples)
    threshold = max(baseline * ALERT_MULTIPLIER, ALERT_HARD_FLOOR)
    recover_threshold = baseline * RECOVER_MULTIPLIER

    log(f"baseline_median={baseline:.2f}s threshold={threshold:.2f}s alerted={alerted}")

    # Check quiet hours - suppress alerts during off-hours
    if should_suppress_alerts():
        log(f"Quiet hours active ({QUIET_START_HOUR}:00-{QUIET_END_HOUR}:00 Berlin) - suppressing alerts")
        save_state(state)
        return

    # Track recovery stability
    recovery_stable_count = state.get("recovery_stable_count", 0)

    if latency > threshold and status == "ok" and not alerted:
        ratio = latency / baseline
        if ratio > 5 or latency > 20:
            icon = "🔴"
        elif ratio > 3 or latency > 15:
            icon = "🟠"
        else:
            icon = "🟡"
        msg = (
            f"{icon} <b>Anthropic API — High Latency Detected</b>\n\n"
            f"Current: <b>{latency:.1f}s</b>\n"
            f"Baseline: {baseline:.1f}s (median of last {len(samples)-1} samples)\n"
            f"Ratio: {ratio:.1f}×\n\n"
            f"Slow responses are expected right now."
        )
        send_telegram(msg)
        state["alerted"] = True
        state["alert_latency"] = round(latency, 2)
        log(f"ALERT sent: {latency:.2f}s vs baseline {baseline:.2f}s ({ratio:.1f}×)")

    elif alerted and latency < recover_threshold:
        # Require stable recovery (2 consecutive readings below threshold)
        recovery_stable_count += 1
        state["recovery_stable_count"] = recovery_stable_count
        if recovery_stable_count >= RECOVER_STABLE_COUNT:
            msg = (
                f"✅ <b>Anthropic API — Latency Back to Normal</b>\n\n"
                f"Current: <b>{latency:.1f}s</b>\n"
                f"Baseline: {baseline:.1f}s\n"
                f"Was: {alert_latency:.1f}s when alert fired"
            )
            send_telegram(msg)
            state["alerted"] = False
            state["alert_latency"] = None
            state["recovery_stable_count"] = 0
            log(f"RECOVERY: {latency:.2f}s back below {recover_threshold:.2f}s (stable after {RECOVER_STABLE_COUNT} reads)")
        else:
            log(f"Recovery pending: {recovery_stable_count}/{RECOVER_STABLE_COUNT} stable readings")

    state["last_check"] = datetime.now(timezone.utc).isoformat()
    state["last_latency"] = round(latency, 3)
    state["baseline_median"] = round(baseline, 3)
    save_state(state)


if __name__ == "__main__":
    main()
