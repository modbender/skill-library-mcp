#!/usr/bin/env python3
"""
OpenClaw Watch Dog — Self-healing gateway monitor.
Pings the gateway every 15 seconds, auto-fixes crashes, sends Telegram alerts.
"""

import asyncio
import json
import logging
import os
import platform
import subprocess
import sys
import time
import hashlib
import base64
from pathlib import Path
from datetime import datetime

import aiohttp

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
WATCHDOG_DIR = Path.home() / ".openclaw" / "watchdog"
CONFIG_FILE = WATCHDOG_DIR / "config.enc"
LOG_FILE = WATCHDOG_DIR / "watchdog.log"
STATE_FILE = WATCHDOG_DIR / "state.json"
GATEWAY_HEALTH = "http://127.0.0.1:3117/health"
APPROVE_REINSTALL = WATCHDOG_DIR / "approve-reinstall"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("watchdog")

# ---------------------------------------------------------------------------
# Encryption helpers (AES-256-CBC via openssl CLI — no extra deps)
# ---------------------------------------------------------------------------

def _machine_password() -> str:
    """Derive a machine-specific password from hardware identifiers."""
    parts = []
    if platform.system() == "Darwin":
        try:
            out = subprocess.check_output(
                ["ioreg", "-rd1", "-c", "IOPlatformExpertDevice"], text=True
            )
            for line in out.splitlines():
                if "IOPlatformUUID" in line:
                    parts.append(line.split('"')[-2])
                    break
        except Exception:
            pass
    # Fallback: hostname + username
    parts.extend([platform.node(), os.getenv("USER", "openclaw")])
    return hashlib.sha256(":".join(parts).encode()).hexdigest()


def decrypt_config() -> dict:
    """Decrypt config.enc → dict."""
    if not CONFIG_FILE.exists():
        log.error("Config file not found: %s", CONFIG_FILE)
        sys.exit(1)
    pw = _machine_password()
    try:
        result = subprocess.run(
            ["openssl", "enc", "-aes-256-cbc", "-d", "-pbkdf2",
             "-in", str(CONFIG_FILE), "-pass", f"pass:{pw}"],
            capture_output=True,
        )
        if result.returncode != 0:
            log.error("Decryption failed: %s", result.stderr.decode())
            sys.exit(1)
        return json.loads(result.stdout.decode())
    except Exception as e:
        log.error("Failed to decrypt config: %s", e)
        sys.exit(1)


# ---------------------------------------------------------------------------
# Telegram
# ---------------------------------------------------------------------------

async def send_telegram(session: aiohttp.ClientSession, cfg: dict, text: str):
    """Send a Telegram message."""
    token = cfg.get("telegram_token", "")
    chat_id = cfg.get("telegram_chat_id", "")
    if not token or not chat_id:
        log.warning("Telegram not configured, skipping alert")
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        async with session.post(url, json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
        }) as resp:
            if resp.status != 200:
                log.warning("Telegram send failed: %s", await resp.text())
    except Exception as e:
        log.warning("Telegram error: %s", e)


# ---------------------------------------------------------------------------
# Local Diagnostics (no external API calls — logs stay on device)
# ---------------------------------------------------------------------------

def diagnose_locally(logs: str) -> str:
    """Analyze logs locally using pattern matching. No data leaves the device."""
    lines = logs.lower()
    issues = []
    if "eaddrinuse" in lines:
        issues.append("Port already in use — another process may be bound to the gateway port")
    if "enomem" in lines or "out of memory" in lines:
        issues.append("Out of memory — consider freeing resources or restarting the machine")
    if "enoent" in lines or "not found" in lines:
        issues.append("Missing file or binary — OpenClaw may need reinstallation")
    if "permission denied" in lines or "eacces" in lines:
        issues.append("Permission denied — check file/directory permissions")
    if "segfault" in lines or "segmentation fault" in lines:
        issues.append("Segmentation fault — possible corrupted installation")
    if "module not found" in lines or "cannot find module" in lines:
        issues.append("Missing Node.js module — may need manual reinstallation")
    if not issues:
        issues.append("No obvious pattern detected — check logs manually")
    return "; ".join(issues)


# ---------------------------------------------------------------------------
# Log collection
# ---------------------------------------------------------------------------

def collect_logs(lines: int = 200) -> str:
    """Collect last N lines from OpenClaw gateway logs."""
    log_paths = [
        Path.home() / ".openclaw" / "gateway.log",
        Path.home() / ".openclaw" / "logs" / "gateway.log",
        Path("/tmp") / "openclaw-gateway.log",
    ]
    for p in log_paths:
        if p.exists():
            try:
                result = subprocess.run(
                    ["tail", f"-{lines}", str(p)], capture_output=True, text=True
                )
                if result.stdout.strip():
                    return result.stdout
            except Exception:
                continue

    # Try journalctl on Linux
    if platform.system() == "Linux":
        try:
            result = subprocess.run(
                ["journalctl", "--user", "-u", "openclaw-gateway", f"-n{lines}", "--no-pager"],
                capture_output=True, text=True,
            )
            if result.stdout.strip():
                return result.stdout
        except Exception:
            pass

    return "(no logs found)"


# ---------------------------------------------------------------------------
# Auto-fix
# ---------------------------------------------------------------------------

async def attempt_fix(session: aiohttp.ClientSession, cfg: dict, attempt: int) -> bool:
    """Try to fix the gateway. Returns True if health check passes after fix."""
    log.info("Auto-fix attempt #%d", attempt)

    if attempt <= 2:
        # Step 1-2: Simple restart
        log.info("Restarting gateway...")
        await send_telegram(session, cfg, "🔧 <b>Watch Dog:</b> Restarting gateway...")
        try:
            subprocess.run(["openclaw", "gateway", "restart"], timeout=30,
                           capture_output=True, text=True)
        except Exception as e:
            log.error("Restart command failed: %s", e)
            return False

        await asyncio.sleep(10)
        return await check_health(session)

    elif attempt == 3:
        # Step 3: Ask user for permission to reinstall
        log.info("Restart attempts exhausted, asking user for reinstall permission...")
        await send_telegram(session, cfg,
            "⚠️ <b>Watch Dog:</b> Gateway restart failed after 2 attempts.\n\n"
            "Reinstalling OpenClaw might fix the issue.\n"
            "To approve reinstall, run:\n"
            "<code>touch ~/.openclaw/watchdog/approve-reinstall</code>\n\n"
            "I'll check for your approval and proceed if given."
        )
        return False

    elif attempt <= 5 and APPROVE_REINSTALL.exists():
        # Step 4-5: User approved reinstall
        log.info("User approved reinstall, running npm install -g openclaw...")
        APPROVE_REINSTALL.unlink(missing_ok=True)
        await send_telegram(session, cfg, "🔧 <b>Watch Dog:</b> Reinstalling OpenClaw (approved by user)...")
        try:
            subprocess.run(["npm", "install", "-g", "openclaw"], timeout=120,
                           capture_output=True, text=True)
            await asyncio.sleep(5)
            subprocess.run(["openclaw", "gateway", "start"], timeout=30,
                           capture_output=True, text=True)
        except Exception as e:
            log.error("Reinstall failed: %s", e)
            return False

        await asyncio.sleep(10)
        return await check_health(session)

    else:
        # No approval or attempts exhausted — notify user
        log.info("Waiting for user action...")
        if attempt == 5:
            await send_telegram(session, cfg,
                "❌ <b>Watch Dog:</b> All auto-fix attempts exhausted.\n"
                "Manual intervention required:\n"
                "<code>openclaw gateway restart</code>"
            )
        return False


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

async def check_health(session: aiohttp.ClientSession) -> bool:
    """Ping the gateway health endpoint."""
    try:
        async with session.get(GATEWAY_HEALTH, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            return resp.status == 200
    except Exception:
        return False


# ---------------------------------------------------------------------------
# State management
# ---------------------------------------------------------------------------

def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {"consecutive_failures": 0, "fix_attempts": 0, "last_status": "unknown", "started_at": time.time()}


def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, indent=2))


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

async def main():
    WATCHDOG_DIR.mkdir(parents=True, exist_ok=True)

    cfg = decrypt_config()
    state = load_state()
    state["started_at"] = time.time()
    save_state(state)

    log.info("Watch Dog started — monitoring %s", GATEWAY_HEALTH)

    async with aiohttp.ClientSession() as session:
        await send_telegram(session, cfg, "🐕 <b>Watch Dog started</b>\nMonitoring gateway health every 15s.")

        while True:
            healthy = await check_health(session)

            if healthy:
                if state["last_status"] != "healthy":
                    log.info("Gateway is healthy ✓")
                    if state["consecutive_failures"] > 0 or state["fix_attempts"] > 0:
                        await send_telegram(session, cfg,
                            "✅ <b>Gateway recovered!</b>\n"
                            f"After {state['fix_attempts']} fix attempt(s)."
                        )
                    state["consecutive_failures"] = 0
                    state["fix_attempts"] = 0
                    state["last_status"] = "healthy"
                    save_state(state)
            else:
                state["consecutive_failures"] += 1
                state["last_status"] = "unhealthy"
                log.warning("Health check failed (%d consecutive)", state["consecutive_failures"])

                if state["consecutive_failures"] == 3:
                    # First failure notification with diagnostics
                    logs = collect_logs()
                    diagnosis = diagnose_locally(logs)
                    await send_telegram(session, cfg,
                        "🚨 <b>Gateway DOWN!</b>\n"
                        f"3 consecutive failures detected.\n\n"
                        f"<b>AI Diagnosis:</b>\n<code>{diagnosis[:500]}</code>\n\n"
                        "Attempting auto-fix..."
                    )

                if state["consecutive_failures"] >= 3:
                    state["fix_attempts"] += 1
                    fixed = await attempt_fix(session, cfg, state["fix_attempts"])
                    if fixed:
                        state["consecutive_failures"] = 0
                        state["fix_attempts"] = 0
                        state["last_status"] = "healthy"
                        log.info("Auto-fix succeeded!")
                        await send_telegram(session, cfg, "✅ <b>Auto-fix succeeded!</b> Gateway is back online.")
                    elif state["fix_attempts"] >= 5:
                        await send_telegram(session, cfg,
                            "❌ <b>Auto-fix exhausted</b> (5 attempts).\n"
                            "Manual intervention required!"
                        )
                        state["fix_attempts"] = 0
                        state["consecutive_failures"] = 0  # Reset to avoid spam

                save_state(state)

            await asyncio.sleep(15)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Watch Dog stopped by user")
    except Exception as e:
        log.exception("Watch Dog crashed: %s", e)
        sys.exit(1)
