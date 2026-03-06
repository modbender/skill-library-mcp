#!/usr/bin/env python3
"""
ClawGuard daemon — monitors registered PIDs, log/dir freshness, and gateway restarts.
Cross-platform: Linux (systemd) and macOS (launchd).

After notifying, the registered entry is removed — no duplicate notifications possible.
On service restart, registry is cleared (all monitored processes are gone anyway).
Only config backups persist on disk.
"""
import json, os, time, subprocess, sys, signal, shutil, platform
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(os.path.expanduser("~/.openclaw/workspace/tools/claw-guard"))
REGISTRY = DATA_DIR / "state.json"
LOG_FILE = DATA_DIR / "claw-guard.log"
OC_CONFIG = Path(os.path.expanduser("~/.openclaw/openclaw.json"))
BACKUP_DIR = DATA_DIR / "config_backups"
CHECK_INTERVAL = 15
GATEWAY_RECOVER_TIMEOUT = 30
IS_MACOS = platform.system() == "Darwin"

DATA_DIR.mkdir(parents=True, exist_ok=True)


def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")
    if LOG_FILE.exists() and LOG_FILE.stat().st_size > 500_000:
        LOG_FILE.rename(LOG_FILE.with_suffix(".log.old"))


def read_registry():
    if not REGISTRY.exists():
        return {"tasks": {}, "watching_restart": False}
    try:
        return json.loads(REGISTRY.read_text())
    except:
        return {"tasks": {}, "watching_restart": False}


def write_registry(data):
    tmp = REGISTRY.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2))
    tmp.rename(REGISTRY)


def notify(target, message):
    try:
        if target:
            cmd = ["openclaw", "message", "send", "--target", target, "--message", message]
            if ":" in target and not target.startswith("room:"):
                parts = target.split(":", 1)
                cmd = ["openclaw", "message", "send", "--channel", parts[0],
                       "--target", parts[1], "--message", message]
        else:
            # No target — let OpenClaw route to default channel
            cmd = ["openclaw", "message", "send", "--message", message]
        subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    except Exception as e:
        log(f"  Notify error: {e}")


def pid_alive(pid):
    try:
        os.kill(int(pid), 0)
        return True
    except (OSError, ProcessLookupError, ValueError):
        return False


def gateway_active():
    try:
        if IS_MACOS:
            r = subprocess.run(["launchctl", "list"], capture_output=True, text=True, timeout=5)
            return "openclaw" in r.stdout.lower()
        else:
            r = subprocess.run(
                ["systemctl", "--user", "is-active", "openclaw-gateway.service"],
                capture_output=True, text=True, timeout=5)
            return r.stdout.strip() == "active"
    except:
        return False


def gateway_status_error():
    try:
        if IS_MACOS:
            r = subprocess.run(["launchctl", "list", "com.openclaw.gateway"],
                              capture_output=True, text=True, timeout=10)
            return (r.stdout or r.stderr)[-500:]
        else:
            r = subprocess.run(
                ["systemctl", "--user", "status", "openclaw-gateway.service"],
                capture_output=True, text=True, timeout=10)
            return r.stdout[-500:] if r.stdout else "no output"
    except:
        return "could not read status"


def gateway_journal():
    try:
        if IS_MACOS:
            log_dir = Path("/tmp/openclaw")
            if log_dir.exists():
                logs = sorted(log_dir.glob("openclaw-*.log"), key=lambda f: f.stat().st_mtime, reverse=True)
                if logs:
                    return logs[0].read_text()[-500:]
            return ""
        else:
            r = subprocess.run(
                ["journalctl", "--user-unit", "openclaw-gateway.service", "-n", "20", "--no-pager"],
                capture_output=True, text=True, timeout=10)
            return r.stdout[-500:] if r.stdout else ""
    except:
        return ""


def restart_gateway():
    try:
        if IS_MACOS:
            uid = os.getuid()
            subprocess.run(["launchctl", "kickstart", "-k", f"gui/{uid}/com.openclaw.gateway"],
                          capture_output=True, text=True, timeout=30)
        else:
            subprocess.run(["systemctl", "--user", "restart", "openclaw-gateway.service"],
                          capture_output=True, text=True, timeout=30)
    except Exception as e:
        log(f"  Restart command failed: {e}")


def get_config_backups():
    if not BACKUP_DIR.exists():
        return []
    return sorted(BACKUP_DIR.glob("openclaw_*.json"), key=lambda f: f.stat().st_mtime, reverse=True)


def try_revert_and_restart():
    backups = get_config_backups()
    if not backups:
        log("  No config backups available")
        return False
    for i, backup in enumerate(backups):
        log(f"  Trying backup {i+1}/{len(backups)}: {backup.name}")
        try:
            shutil.copy2(str(backup), str(OC_CONFIG))
        except Exception as e:
            log(f"  Copy failed: {e}")
            continue
        restart_gateway()
        time.sleep(5)
        if gateway_active():
            log(f"  ✅ Gateway recovered with {backup.name}")
            return True
        log(f"  ❌ Still down with {backup.name}")
    return False


def check_restart(reg):
    if not reg.get("watching_restart"):
        return

    if gateway_active():
        log("✅ Gateway restart succeeded")
        # Remove the restart watch
        reg["watching_restart"] = False
        reg.pop("restart_registered_at", None)
        reg.pop("restart_target", None)
        write_registry(reg)
        return

    registered = reg.get("restart_registered_at", 0)
    if time.time() - registered < GATEWAY_RECOVER_TIMEOUT:
        return

    error = gateway_status_error()
    journal = gateway_journal()
    log("🚨 Gateway restart FAILED")

    recovered = try_revert_and_restart()
    target = reg.get("restart_target", "")

    detail = error[:300]
    if journal:
        detail += f"\n\nJournal:\n{journal[:200]}"

    if recovered:
        notify(target, f"🚨 Gateway restart failed — ClawGuard reverted config and recovered.\n\nWhy:\n{detail}")
    else:
        notify(target, f"🚨 Gateway DOWN — all config backups failed! Manual intervention needed.\n\nWhy:\n{detail}")

    # Remove the restart watch after notifying — prevents duplicate
    reg["watching_restart"] = False
    reg.pop("restart_registered_at", None)
    reg.pop("restart_target", None)
    write_registry(reg)


def check_tasks(reg):
    tasks = reg.get("tasks", {})
    to_remove = []

    for task_id, task in tasks.items():
        if task.get("status") != "watching":
            continue

        pid = task.get("pid")
        target = task.get("target", "")
        timeout = task.get("timeout", 180)

        # PID gone → notify and remove
        if pid and not pid_alive(pid):
            log(f"📢 Task '{task_id}' — PID {pid} gone")
            notify(target,
                   f"📢 Task '{task_id}' — PID {pid} disappeared.\n"
                   f"Command: {task.get('command', '?')}\n"
                   f"Please confirm: success or failure?")
            to_remove.append(task_id)
            continue

        # Log freshness → notify and remove
        log_path = task.get("log")
        if log_path and timeout > 0:
            lp = Path(os.path.expanduser(log_path))
            if lp.exists() and (time.time() - lp.stat().st_mtime) > timeout:
                age = int(time.time() - lp.stat().st_mtime)
                log(f"📢 Task '{task_id}' — log stale {age}s")
                notify(target,
                       f"📢 Task '{task_id}' — log not updated for {age}s (timeout: {timeout}s).\n"
                       f"PID {pid}: {'alive' if pid_alive(pid) else 'gone'}")
                to_remove.append(task_id)
                continue

        # Dir freshness → notify and remove
        watch_dir = task.get("watch_dir")
        if watch_dir and timeout > 0:
            dp = Path(os.path.expanduser(watch_dir))
            if dp.exists() and dp.is_dir():
                newest = max((f.stat().st_mtime for f in dp.iterdir() if f.is_file()), default=0)
                if newest > 0 and (time.time() - newest) > timeout:
                    age = int(time.time() - newest)
                    log(f"📢 Task '{task_id}' — dir stale {age}s")
                    notify(target,
                           f"📢 Task '{task_id}' — no new files in {watch_dir} for {age}s (timeout: {timeout}s).\n"
                           f"PID {pid}: {'alive' if pid_alive(pid) else 'gone'}")
                    to_remove.append(task_id)
                    continue

    # Remove notified tasks — prevents duplicates
    if to_remove:
        for tid in to_remove:
            del tasks[tid]
        reg["tasks"] = tasks
        write_registry(reg)


def handle_signal(signum, frame):
    log(f"ClawGuard signal {signum}, exiting")
    sys.exit(0)


def main():
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)
    log(f"🛡️ ClawGuard started ({platform.system()})")

    # Clear registry on start — all old processes are gone after reboot
    write_registry({"tasks": {}, "watching_restart": False})
    log("  Registry cleared (fresh start)")

    while True:
        try:
            reg = read_registry()
            check_restart(reg)
            if reg.get("tasks"):
                check_tasks(reg)
        except Exception as e:
            log(f"Error: {e}")
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
