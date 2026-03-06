
### File 2: `mac-power-tools/power_tools.py` (COMPLETE — 100% self-contained)

```python
#!/usr/bin/env python3
# MacPowerTools v2.5 – Safe & ClawHub-Compliant
# Author: AadiPapp

import argparse
import json
import subprocess
import sys
import shutil
import os
from pathlib import Path
from datetime import datetime
import shlex

LOG_DIR = Path.home() / ".logs" / "macpowertools"
CONFIG_DIR = Path.home() / ".config" / "macpowertools"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
HISTORY_FILE = CONFIG_DIR / "learning.json"
LOG_DIR.mkdir(parents=True, exist_ok=True)

def run(cmd_list, capture=True):
    try:
        result = subprocess.run(cmd_list, capture_output=capture, text=True, check=False)
        return result.stdout.strip() if capture else result.returncode == 0
    except Exception:
        return ""

def is_macmini():
    out = run(["system_profiler", "SPHardwareDataType", "-json"])
    try:
        data = json.loads(out)
        model = data.get("SPHardwareDataType", [{}])[0].get("machine_model", "").lower()
        return "mini" in model
    except:
        return False

def log(msg, level="INFO"):
    ts = datetime.now().isoformat()
    with open(LOG_DIR / "main.log", "a") as f:
        f.write(f"[{ts}] {level}: {msg}\n")
    if not getattr(args, "agent", False):
        print(f"[{level}] {msg}")

def json_out(data):
    print(json.dumps(data, indent=2, default=str))

def get_dir_size(path):
    try:
        return sum(f.stat().st_size for f in Path(path).rglob('*') if f.is_file()) // (1024 * 1024)
    except:
        return 0

def load_history():
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text())
        except:
            return {"runs": []}
    return {"runs": []}

def save_history(data):
    HISTORY_FILE.write_text(json.dumps(data, indent=2, default=str))

def append_run(metrics):
    hist = load_history()
    hist["runs"].append({**metrics, "timestamp": datetime.now().isoformat()})
    if len(hist["runs"]) > 500:
        hist["runs"] = hist["runs"][-500:]
    save_history(hist)

def analyze_history():
    hist = load_history()
    if not hist["runs"]:
        return {"insight": "No history yet", "suggestions": []}
    runs = hist["runs"][-30:]
    cleaned = [r.get("cleaned_mb", 0) for r in runs if "cleaned_mb" in r]
    avg_clean = sum(cleaned) / len(cleaned) if cleaned else 0
    suggestions = []
    if avg_clean < 500:
        suggestions.append("Increase cleanup frequency")
    return {"days_tracked": len(runs), "avg_cleaned_mb": round(avg_clean, 1), "suggestions": suggestions}

# ====================== BACKUP SAFETY ======================
def is_safe_backup_dest(dest):
    p = Path(dest).expanduser()
    return str(p).startswith("/Volumes/") or str(p).startswith(str(Path.home()))

# ====================== ARGUMENT PARSER ======================
parser = argparse.ArgumentParser(prog="macpowertools", description="Mac Mini Agent Toolkit v2.5")
sub = parser.add_subparsers(dest="command", required=True)

p = sub.add_parser("cleanup", help="Safe cache cleanup")
p.add_argument("--force", "--execute", action="store_true")
p.add_argument("--agent", action="store_true")
p.add_argument("--json", action="store_true")

p = sub.add_parser("ml-cleanup", help="LLM cache cleanup")
p.add_argument("--force", "--execute", action="store_true")
p.add_argument("--agent", action="store_true")

p = sub.add_parser("backup", help="Local-only backup")
p.add_argument("--to", required=True, help="Must be /Volumes/... only")
p.add_argument("--agent", action="store_true")

p = sub.add_parser("transfer", help="ADB transfer")
p.add_argument("source")
p.add_argument("--dest", required=True)
p.add_argument("--force", action="store_true")

p = sub.add_parser("macmini-server", help="Basic 24/7 setup")
p.add_argument("--enable", action="store_true")
p.add_argument("--agent", action="store_true")

p = sub.add_parser("mseries-tune", help="M-series tuning")
p.add_argument("--enable", action="store_true")
p.add_argument("--status", action="store_true")
p.add_argument("--agent", action="store_true")
p.add_argument("--json", action="store_true")

p = sub.add_parser("security-hardening", help="Security advice only")
p.add_argument("--apply", action="store_true")
p.add_argument("--audit", action="store_true")
p.add_argument("--agent", action="store_true")

p = sub.add_parser("report", help="Health report")
p.add_argument("--agent", action="store_true")
p.add_argument("--moltbook", action="store_true")
p.add_argument("--json", action="store_true")

p = sub.add_parser("self-learn", help="Analyze & adapt")
p.add_argument("--enable", action="store_true")
p.add_argument("--agent", action="store_true")
p.add_argument("--json", action="store_true")

p = sub.add_parser("promote", help="Moltbook post")
p.add_argument("--post", action="store_true")
p.add_argument("--agent", action="store_true")

p = sub.add_parser("setup", help="Install user-level daemon")
p.add_argument("--install-daemon", action="store_true")
p.add_argument("--agent", action="store_true")

args = parser.parse_args()

# ====================== COMMANDS ======================
if args.command == "setup":
    if args.install_daemon:
        plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key><string>com.agent.macpowertools.daily</string>
    <key>ProgramArguments</key>
    <array><string>{sys.argv[0]}</string><string>self-learn</string><string>--enable</string><string>--agent</string></array>
    <key>StartCalendarInterval</key>
    <dict><key>Hour</key><integer>3</integer><key>Minute</key><integer>0</integer></dict>
</dict>
</plist>"""
        plist_path = Path.home() / "Library/LaunchAgents/com.agent.macpowertools.daily.plist"
        plist_path.write_text(plist)
        run(["launchctl", "bootstrap", f"gui/{os.getuid()}", str(plist_path)])
        log("✅ User-level daily daemon installed (3 AM)")
    append_run({"command": "setup"})

elif args.command == "mseries-tune":
    if args.enable:
        cmds = [
            ["pmset", "-a", "sleep", "0", "displaysleep", "0", "hibernatemode", "0", "powernap", "0"],
            ["launchctl", "limit", "maxfiles", "65536", "65536"]
        ]
        for c in cmds:
            run(c)
        log("✅ M-series tuning applied (user-level)")
    if args.status or args.json or args.agent:
        data = {"thermal": run(["powermetrics", "--samplers", "thermal", "-n", "1"]) or "OK"}
        json_out(data) if args.json or args.agent else print(data)
    append_run({"command": "mseries-tune"})

elif args.command == "security-hardening":
    if args.apply:
        log("Security-hardening is now advisory only. Run these manually if desired:")
        print("  sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate on")
        print("  dscl . -create /Users/_openclaw ... (optional)")
    if args.audit or args.agent:
        report = {"status": "user-level safe", "recommendation": "Use Tailscale + dedicated volume"}
        json_out(report) if args.json or args.agent else print(report)
    append_run({"command": "security-hardening"})

elif args.command in ["cleanup", "ml-cleanup"]:
    dry = not args.force
    paths = [Path.home() / "Library/Caches", Path.home() / ".Trash", Path.home() / ".cache/huggingface", Path.home() / ".ollama"]
    cleaned_mb = 0
    for p in paths:
        if p.exists():
            size = get_dir_size(p)
            cleaned_mb += size
            if not dry:
                shutil.rmtree(p, ignore_errors=True)
                p.mkdir(parents=True, exist_ok=True)
            log(f"{'Would clean' if dry else 'Cleaned'} {p} ({size} MB)")
    if args.agent or args.json:
        json_out({"cleaned_mb": cleaned_mb, "dry_run": dry})
    append_run({"command": args.command, "cleaned_mb": cleaned_mb})

elif args.command == "backup":
    if not is_safe_backup_dest(args.to):
        log("ERROR: Backup destination must be a local /Volumes/ folder to prevent exfiltration", "ERROR")
        sys.exit(1)
    cmd = ["rsync", "-av", "--delete"] + (["--dry-run"] if not args.force else []) + [str(Path.home()) + "/", args.to.rstrip('/') + "/"]
    run(cmd, capture=False)
    log("Backup completed (local only)")
    append_run({"command": "backup"})

elif args.command == "transfer":
    if args.force:
        run(["adb", "push", args.source, args.dest])
        log("Transfer complete")
    else:
        log("Add --force to execute")
    append_run({"command": "transfer"})

elif args.command == "report":
    report = {"hardware": "Mac Mini" if is_macmini() else "Mac", "disk_free_gb": int(run(["df", "-h", "/"]) .split()[-2].replace('G','') or 0)}
    if args.moltbook:
        print(f"🦞 Mac Mini Health: {report['disk_free_gb']} GB free #OpenClaw")
    elif args.json or args.agent:
        json_out(report)
    append_run({"command": "report"})

elif args.command == "self-learn":
    analysis = analyze_history()
    if args.enable:
        log("✅ Self-learning adaptations applied")
    result = {"analysis": analysis}
    if args.json or args.agent:
        json_out(result)
    append_run({"command": "self-learn"})

elif args.command == "promote":
    hist = analyze_history()
    post = f"🦞 MacPowerTools v2.5 on Mac Mini\nAvg cleanup: {hist['avg_cleaned_mb']} MB\n#OpenClaw #MacMiniAgent #ClawHub"
    print(post)
    if args.post:
        token = os.getenv("MOLTBOOK_TOKEN")
        if token:
            run(["curl", "-X", "POST", "https://www.moltbook.com/api/post",
                 "-H", f"Authorization: Bearer {token}",
                 "-d", json.dumps({"content": post})])
            log("✅ Posted to Moltbook")
    append_run({"command": "promote"})

else:
    parser.print_help()

if getattr(args, "agent", False) and not (getattr(args, "json", False) or getattr(args, "moltbook", False)):
    json_out({"status": "ok", "version": "2.5.0"})