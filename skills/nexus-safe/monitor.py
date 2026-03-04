import os, sys, subprocess, json, time, psutil, argparse
from datetime import datetime
from pathlib import Path

# --- CONFIG & POLICIES ---
STATE_DIR = Path.home() / ".nexus-safe"
STATE_FILE = STATE_DIR / "state.json"
AUDIT_LOG = STATE_DIR / "audit.log"

# Env Vars
ALLOW_RESTARTS = os.getenv("NEXUS_SAFE_ALLOW_RESTARTS", "false").lower() == "true"
ALLOWED_DOCKER = [x.strip() for x in os.getenv("NEXUS_SAFE_ALLOWED_DOCKER", "").split(",") if x.strip()]
ALLOWED_PM2 = [x.strip() for x in os.getenv("NEXUS_SAFE_ALLOWED_PM2", "").split(",") if x.strip()]
MAX_RESTARTS = int(os.getenv("NEXUS_SAFE_MAX_RESTARTS", "3"))
WINDOW = int(os.getenv("NEXUS_SAFE_RESTART_WINDOW_SECONDS", "3600"))
LOGS_REQ = os.getenv("NEXUS_SAFE_LOGS_REQUIRED", "true").lower() == "true"
LOGS_FRESH = int(os.getenv("NEXUS_SAFE_LOGS_FRESH_SECONDS", "300"))

# Timeouts
T_STATUS = int(os.getenv("NEXUS_SAFE_TIMEOUT_STATUS", "5"))
T_LOGS = int(os.getenv("NEXUS_SAFE_TIMEOUT_LOGS", "10"))
T_RESTART = int(os.getenv("NEXUS_SAFE_TIMEOUT_RESTART", "15"))

def exit_with_error(code, msg, as_json=False):
    if as_json: print(json.dumps({"error": msg, "code": code}))
    else: print(f"Error ({code}): {msg}", file=sys.stderr)
    sys.exit(code)

def log_audit(action, target, status, detail=""):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with open(AUDIT_LOG, "a") as f:
        f.write(f"{datetime.now().isoformat()} | {action} | {target} | {status} | {detail}\n")

def get_state():
    if not STATE_FILE.exists(): return {"restarts": [], "last_logs": {}}
    try: return json.loads(STATE_FILE.read_text())
    except: return {"restarts": [], "last_logs": {}}

def save_state(s):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(s))
    STATE_FILE.chmod(0o600)

def run_cmd(args, timeout):
    try:
        return subprocess.run(args, capture_output=True, text=True, timeout=timeout, check=True)
    except subprocess.CalledProcessError as e:
        return e
    except FileNotFoundError:
        exit_with_error(4, f"Binary not found: {args[0]}")
    except subprocess.TimeoutExpired:
        exit_with_error(5, f"Command timeout: {' '.join(args)}")

# --- ACTIONS ---
def cmd_status():
    vitals = {"cpu": psutil.cpu_percent(), "ram": psutil.virtual_memory().percent, "disk": psutil.disk_usage('/').percent}
    docker = []
    try:
        res = run_cmd(['docker', 'ps', '-a', '--format', '{{.Names}}|{{.Status}}'], T_STATUS)
        if isinstance(res, subprocess.CompletedProcess):
            docker = [line.split('|') for line in res.stdout.strip().split('\n') if '|' in line]
    except: pass
    
    pm2 = []
    try:
        res = run_cmd(['pm2', 'jlist'], T_STATUS)
        if isinstance(res, subprocess.CompletedProcess):
            pm2 = [{"name": p['name'], "status": p['pm2_env']['status']} for p in json.loads(res.stdout)]
    except: pass
    
    return {"vitals": vitals, "docker": docker, "pm2": pm2}

def cmd_logs(target, lines=50):
    res = run_cmd(['docker', 'inspect', target], T_STATUS)
    if isinstance(res, subprocess.CompletedProcess):
        out = run_cmd(['docker', 'logs', '--tail', str(lines), target], T_LOGS).stdout
    else:
        out = run_cmd(['pm2', 'logs', target, '--lines', str(lines), '--nostream'], T_LOGS).stdout
    
    state = get_state()
    state["last_logs"][target] = time.time()
    save_state(state)
    log_audit("LOGS", target, "OK")
    return out

def cmd_recover(target, force=False, dry_run=False):
    if not ALLOW_RESTARTS: exit_with_error(3, "Restarts disabled by policy")
    
    state = get_state()
    status_data = cmd_status()
    # Allowlist Check
    is_docker = any(target == c[0] for c in status_data['docker'])
    is_pm2 = any(target == p['name'] for p in status_data['pm2'])
    
    if is_docker and target not in ALLOWED_DOCKER: exit_with_error(3, f"{target} not in Docker Allowlist")
    if is_pm2 and target not in ALLOWED_PM2: exit_with_error(3, f"{target} not in PM2 Allowlist")
    if not is_docker and not is_pm2: exit_with_error(2, f"Service {target} not found")

    # Logs freshness check
    if LOGS_REQ and not force:
        if (time.time() - state["last_logs"].get(target, 0)) > LOGS_FRESH:
            exit_with_error(3, "Logs not reviewed recently. Check logs first or use --force")

    # Rate limiting (Sliding window)
    now = time.time()
    state["restarts"] = [t for t in state["restarts"] if (now - t) < WINDOW]
    if len(state["restarts"]) >= MAX_RESTARTS: exit_with_error(3, "Rate limit exceeded")

    args = ['docker', 'restart', target] if is_docker else ['pm2', 'restart', target]
    if dry_run: return f"Dry-run: would run {' '.join(args)}"
    
    run_cmd(args, T_RESTART)
    state["restarts"].append(now)
    save_state(state)
    log_audit("RECOVER", target, "SUCCESS")
    return {"status": "success", "target": target}

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    s = p.add_subparsers(dest="cmd")
    s.add_parser("status").add_argument("--json", action="store_true")
    l = s.add_parser("logs")
    l.add_argument("target")
    l.add_argument("--lines", type=int, default=50)
    r = s.add_parser("recover")
    r.add_argument("target")
    r.add_argument("--force", action="store_true")
    r.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    if args.cmd == "status": print(json.dumps(cmd_status(), indent=2))
    elif args.cmd == "logs": print(cmd_logs(args.target, args.lines))
    elif args.cmd == "recover": print(json.dumps(cmd_recover(args.target, args.force, args.dry_run), indent=2))
    else: p.print_help()
