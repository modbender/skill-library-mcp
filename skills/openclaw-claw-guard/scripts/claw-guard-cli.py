#!/usr/bin/env python3
"""
ClawGuard CLI — Register tasks for PID + log monitoring.
"""
import json, os, sys, argparse, time, shutil, glob
from pathlib import Path

DATA_DIR = Path(os.path.expanduser("~/.openclaw/workspace/tools/claw-guard"))
STATE_FILE = DATA_DIR / "state.json"
OC_CONFIG = Path(os.path.expanduser("~/.openclaw/openclaw.json"))
BACKUP_DIR = DATA_DIR / "config_backups"
MAX_BACKUPS = 5


def load():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except:
            pass
    return {"tasks": {}}


def save(state):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    tmp = STATE_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2))
    tmp.rename(STATE_FILE)


def cmd_register(args):
    state = load()
    tasks = state.get("tasks", {})
    tasks[args.id] = {
        "pid": args.pid,
        "target": args.target,
        "log": args.log or "",
        "watch_dir": args.watch_dir or "",
        "timeout": args.timeout,
        "command": args.command or "",
        "registered_at": time.time(),
        "status": "watching",
        "stale_notified": False,
        "last_dir_count": None,
    }
    state["tasks"] = tasks
    save(state)
    print(f"🛡️ Registered '{args.id}' (PID {args.pid}) → {args.target}")
    if args.log:
        print(f"   Log: {args.log} (stale after {args.timeout}s)")
    if args.watch_dir:
        print(f"   Watch dir: {args.watch_dir} (stale after {args.timeout}s)")


def cmd_register_restart(args):
    """Snapshot current config and tell ClawGuard to watch the gateway restart."""
    state = load()
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    # Save timestamped backup
    if OC_CONFIG.exists():
        ts = time.strftime("%Y%m%d_%H%M%S")
        backup = BACKUP_DIR / f"openclaw_{ts}.json"
        shutil.copy2(str(OC_CONFIG), str(backup))
        print(f"📸 Config backed up → {backup.name}")

        # Prune old backups, keep newest MAX_BACKUPS
        backups = sorted(BACKUP_DIR.glob("openclaw_*.json"), key=lambda f: f.stat().st_mtime, reverse=True)
        for old in backups[MAX_BACKUPS:]:
            old.unlink()
            print(f"   Pruned old backup: {old.name}")
    else:
        print("⚠️ No openclaw.json found to back up")

    state["watching_restart"] = True
    state["restart_registered_at"] = time.time()
    state["restart_target"] = args.target or ""
    save(state)
    print("🛡️ Gateway restart registered — ClawGuard will watch for failure")


def cmd_status(args):
    state = load()
    restart = state.get("watching_restart", False)
    print(f"Gateway restart watch: {'ACTIVE' if restart else 'off'}")
    # Show available backups
    if BACKUP_DIR.exists():
        backups = sorted(BACKUP_DIR.glob("openclaw_*.json"), key=lambda f: f.stat().st_mtime, reverse=True)
        if backups:
            print(f"Config backups ({len(backups)}):")
            for b in backups:
                age_min = (time.time() - b.stat().st_mtime) / 60
                print(f"  {b.name} ({age_min:.0f}m ago)")
    tasks = state.get("tasks", {})
    if not tasks:
        print("No tasks registered.")
        return
    for tid, t in tasks.items():
        status = t.get("status", "?")
        icon = {"watching": "👀", "pid_gone": "💀"}.get(status, "❓")
        pid = t.get("pid", "?")
        age = ""
        if t.get("registered_at"):
            mins = (time.time() - t["registered_at"]) / 60
            age = f" ({mins:.0f}m)"
        target = t.get("target", "?")
        print(f"  {icon} {tid:25s} PID={pid:>8} {status:10s}{age}  → {target[:30]}  {t.get('command', '')[:30]}")


def cmd_remove(args):
    state = load()
    tasks = state.get("tasks", {})
    if args.id in tasks:
        del tasks[args.id]
        state["tasks"] = tasks
        save(state)
        print(f"Removed '{args.id}'")
    else:
        print(f"Not found: '{args.id}'")


def cmd_clear_done(args):
    state = load()
    tasks = state.get("tasks", {})
    active = {k: v for k, v in tasks.items() if v.get("status") == "watching"}
    removed = len(tasks) - len(active)
    state["tasks"] = active
    save(state)
    print(f"Cleared {removed}, {len(active)} active")


def main():
    parser = argparse.ArgumentParser(prog="claw-guard")
    sub = parser.add_subparsers(dest="cmd")

    p = sub.add_parser("register", help="Register a task for monitoring")
    p.add_argument("--id", required=True)
    p.add_argument("--pid", type=int, required=True)
    p.add_argument("--target", required=True, help="Notification target (room:!id:server, telegram:id, etc.)")
    p.add_argument("--log", default="", help="Log file path (checks mtime only)")
    p.add_argument("--watch-dir", default="", dest="watch_dir", help="Directory to watch for new file creation")
    p.add_argument("--timeout", type=int, default=180, help="Stale timeout in seconds for log/dir (default: 180)")
    p.add_argument("--command", default="", help="Command description")

    p_restart = sub.add_parser("register-restart", help="Snapshot config and watch gateway restart")
    p_restart.add_argument("--target", default="", help="Notification target for restart failure alerts")
    sub.add_parser("status", help="Show watched tasks")

    p_rm = sub.add_parser("remove", help="Remove a task")
    p_rm.add_argument("--id", required=True)

    sub.add_parser("clear-done", help="Remove non-watching tasks")

    args = parser.parse_args()
    cmds = {"register": cmd_register, "register-restart": cmd_register_restart,
            "status": cmd_status, "remove": cmd_remove, "clear-done": cmd_clear_done}
    if args.cmd in cmds:
        cmds[args.cmd](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
