#!/usr/bin/env python3
"""
Gateway Guard skill — OpenClaw gateway auth consistency.

- Detect gateway auth drift (config vs running gateway process).
- Optionally fix by restarting gateway with config credentials.
- Write gateway.auth to openclaw.json only when it is missing or wrong.
- Output machine-readable JSON for orchestration.
"""

import argparse
import hashlib
import json
import os
import re
import secrets
import signal
import socket
import subprocess
import sys
import time
from pathlib import Path


def _run(cmd, timeout=8):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def _openclaw_home():
    return Path(os.environ.get("OPENCLAW_HOME") or os.path.expanduser("~/.openclaw"))


def _guard_state_path():
    return _openclaw_home() / "logs" / "gateway-guard.state.json"


def _continue_state_path():
    return _openclaw_home() / "logs" / "gateway-guard.continue-state.json"


# Log line that triggers auto "continue" to the agent (run error from API/stream).
RUN_ERROR_PATTERN = "Unhandled stop reason: error"
GATEWAY_LOG = _openclaw_home() / "logs" / "gateway.log"
CONTINUE_COOLDOWN_SEC = 90  # Don't trigger again for the same error within this window
WAIT_FOR_PORT_TIMEOUT_SEC = 30
WAIT_FOR_PORT_INTERVAL_SEC = 1.0


def _gateway_port_open(port):
    """Probe gateway by TCP connect to port. Returns True if connection succeeds."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            s.connect(("127.0.0.1", int(port)))
        return True
    except (OSError, socket.error):
        return False


def _wait_for_gateway_port(port, timeout_sec=WAIT_FOR_PORT_TIMEOUT_SEC, interval_sec=WAIT_FOR_PORT_INTERVAL_SEC):
    """Wait until gateway port is open or timeout. Returns True if port became open."""
    deadline = time.monotonic() + timeout_sec
    while time.monotonic() < deadline:
        if _gateway_port_open(port):
            return True
        time.sleep(interval_sec)
    return False


def _secret_hash(secret):
    return hashlib.sha256((secret or "").encode("utf-8")).hexdigest()


def _load_guard_state():
    p = _guard_state_path()
    if not p.exists():
        return None
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _save_guard_state(pid, mode, port, secret):
    p = _guard_state_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    state = {
        "pid": pid,
        "mode": mode,
        "port": port,
        "secretHash": _secret_hash(secret),
        "updatedAt": int(time.time()),
    }
    with open(p, "w", encoding="utf-8") as f:
        json.dump(state, f)


def load_openclaw_config():
    cfg_path = _openclaw_home() / "openclaw.json"
    with open(cfg_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return cfg_path, data


def auth_from_config(data):
    gateway = data.get("gateway") or {}
    auth = gateway.get("auth") or {}
    mode = auth.get("mode", "token")
    port = int(gateway.get("port", 18789))
    secret = auth.get("token") if mode == "token" else auth.get("password")
    return {
        "mode": mode,
        "port": port,
        "secret": secret,
    }


def write_gateway_auth_only_if_incorrect(cfg_path, data, mode, port, secret):
    """
    Write gateway.auth to openclaw.json only when it is missing or wrong.
    Returns True if a write was performed, False if config was already correct.
    """
    gateway = data.get("gateway") or {}
    auth = gateway.get("auth") or {}
    current_mode = auth.get("mode", "token")
    current_secret = auth.get("token") if current_mode == "token" else auth.get("password")
    port_val = int(gateway.get("port", 18789))
    incorrect = (
        not current_secret
        or current_mode != mode
        or port_val != port
        or current_secret != secret
    )
    if not incorrect:
        return False
    if "gateway" not in data:
        data["gateway"] = {}
    if "auth" not in data["gateway"]:
        data["gateway"]["auth"] = {}
    data["gateway"]["port"] = port
    data["gateway"]["auth"]["mode"] = mode
    if mode == "token":
        data["gateway"]["auth"]["token"] = secret
        data["gateway"]["auth"].pop("password", None)
    else:
        data["gateway"]["auth"]["password"] = secret
        data["gateway"]["auth"].pop("token", None)
    with open(cfg_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    return True


def _extract_pid_on_port(port):
    # macOS-friendly way to get listener PID(s)
    proc = _run(["lsof", "-nP", f"-iTCP:{port}", "-sTCP:LISTEN", "-t"])
    if proc.returncode != 0 or not proc.stdout.strip():
        return None
    first = proc.stdout.strip().splitlines()[0].strip()
    try:
        return int(first)
    except ValueError:
        return None


def _extract_gateway_secret_from_cmd(cmd, mode):
    if not cmd:
        return None
    if mode == "token":
        # --token abc OR --token=abc
        m = re.search(r"--token(?:=|\s+)(\S+)", cmd)
        return m.group(1) if m else None
    if mode == "password":
        # --password abc OR --password=abc
        m = re.search(r"--password(?:=|\s+)(\S+)", cmd)
        return m.group(1) if m else None
    return None


def gateway_runtime_status(port, mode, expected_secret):
    pid = _extract_pid_on_port(port)
    if not pid:
        return {
            "running": False,
            "pid": None,
            "cmd": None,
            "runtimeSecretDetected": None,
            "secretMatchesConfig": False,
            "reason": "gateway_not_running",
        }

    # Try to get command line via ps, but handle permission errors gracefully
    cmd = ""
    runtime_secret = None
    try:
        ps = _run(["ps", "-p", str(pid), "-o", "command="])
        cmd = ps.stdout.strip() if ps.returncode == 0 else ""
        runtime_secret = _extract_gateway_secret_from_cmd(cmd, mode)
    except (PermissionError, OSError) as e:
        # macOS may restrict ps access - fall back to guard state check
        cmd = None
        runtime_secret = None
    
    if runtime_secret:
        matches = bool(expected_secret and expected_secret == runtime_secret)
        reason = "ok" if matches else "secret_mismatch"
    else:
        # Some gateway binaries do not expose auth secrets in process args.
        # Also fallback when ps fails due to permissions
        state = _load_guard_state()
        if (
            state
            and state.get("pid") == pid
            and state.get("mode") == mode
            and int(state.get("port", -1)) == int(port)
            and state.get("secretHash") == _secret_hash(expected_secret)
        ):
            matches = True
            reason = "ok_guard_state"
        else:
            matches = False
            reason = "secret_not_detectable"
    return {
        "running": True,
        "pid": pid,
        "cmd": cmd,
        "runtimeSecretDetected": runtime_secret,
        "secretMatchesConfig": matches,
        "reason": reason,
    }


def _kill_pid(pid):
    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    except PermissionError:
        return
    time.sleep(0.7)
    try:
        os.kill(pid, 0)
    except OSError:
        return
    try:
        os.kill(pid, signal.SIGKILL)
    except OSError:
        pass


def _mask_cmd_for_log(cmd):
    """Return a safe string for logging: mask --token/--password values."""
    out = []
    i = 0
    while i < len(cmd):
        arg = cmd[i]
        if arg in ("--token", "--password") and i + 1 < len(cmd):
            out.append(arg)
            out.append("***")
            i += 2
            continue
        out.append(arg)
        i += 1
    return " ".join(out)


def _restart_gateway(port, mode, secret):
    _run(["openclaw", "gateway", "stop"], timeout=10)

    stale = _extract_pid_on_port(port)
    if stale:
        _kill_pid(stale)

    cmd = ["openclaw", "gateway", "--port", str(port), "--auth", mode]
    if mode == "token":
        cmd += ["--token", secret]
    elif mode == "password":
        cmd += ["--password", secret]
    else:
        raise ValueError(f"Unsupported auth mode: {mode}")

    log_path = _openclaw_home() / "logs" / "gateway-guard.restart.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as logf:
        logf.write(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] restart: {_mask_cmd_for_log(cmd)}\n")
    # Run gateway process without redirecting its output to the log (avoids any risk of logging secrets)
    subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    try:
        log_path.chmod(0o600)
    except OSError:
        pass

    time.sleep(2.0)
    status = gateway_runtime_status(port, mode, secret)
    if status.get("running") and status.get("pid"):
        _save_guard_state(status["pid"], mode, port, secret)
        # Recheck once state is recorded for binaries that hide secrets.
        status = gateway_runtime_status(port, mode, secret)
    return status


def build_result(cfg_path, mode, port, runtime, fixed=False):
    return {
        "ok": runtime.get("secretMatchesConfig", False),
        "fixed": fixed,
        "configPath": str(cfg_path),
        "authMode": mode,
        "gatewayPort": port,
        "running": runtime.get("running"),
        "pid": runtime.get("pid"),
        "reason": runtime.get("reason"),
        "secretMatchesConfig": runtime.get("secretMatchesConfig"),
        "recommendedAction": (
            "none"
            if runtime.get("secretMatchesConfig")
            else "run gateway_guard.py ensure --apply and restart client session"
        ),
    }


# --- continue-on-error: auto-prompt "continue" when run error appears in logs ---

def _load_continue_state():
    p = _continue_state_path()
    if not p.exists():
        return {"lastTriggeredAt": 0, "lastMatchedLine": ""}
    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"lastTriggeredAt": 0, "lastMatchedLine": ""}


def _save_continue_state(last_triggered_at, last_matched_line):
    p = _continue_state_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump({
            "lastTriggeredAt": last_triggered_at,
            "lastMatchedLine": last_matched_line or "",
        }, f, indent=2)


def _trigger_continue_message():
    """Send 'continue' to the agent via openclaw agent --message continue --deliver."""
    openclaw_bin = os.environ.get("OPENCLAW_BIN", "openclaw")
    env = {**os.environ, "OPENCLAW_HOME": str(_openclaw_home())}
    cmd = [openclaw_bin, "agent", "--message", "continue", "--deliver"]
    try:
        r = subprocess.run(cmd, env=env, cwd=str(_openclaw_home()), timeout=60, capture_output=True, text=True)
        if r.returncode != 0:
            subprocess.run(
                ["bash", "-l", "-c", f'exec "{openclaw_bin}" agent --message "continue" --deliver'],
                env={**env, "OPENCLAW_HOME": str(_openclaw_home())},
                cwd=str(_openclaw_home()),
                timeout=60,
                capture_output=True,
            )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass


def _read_log_tail(path, max_lines=200):
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()
    return lines[-max_lines:] if len(lines) > max_lines else lines


def check_and_trigger_continue_once():
    """
    Check gateway.log for RUN_ERROR_PATTERN. If found and not recently triggered, send 'continue' to the agent.
    Returns dict with triggered (bool), reason (str), and optional error (str).
    """
    state = _load_continue_state()
    now_ts = int(time.time())
    if now_ts - state.get("lastTriggeredAt", 0) < CONTINUE_COOLDOWN_SEC:
        return {"triggered": False, "reason": "cooldown"}

    for line in _read_log_tail(GATEWAY_LOG, 300):
        if RUN_ERROR_PATTERN in line and line.strip() != state.get("lastMatchedLine"):
            _trigger_continue_message()
            _save_continue_state(now_ts, line.strip())
            return {"triggered": True, "reason": "run_error_detected"}
    return {"triggered": False, "reason": "no_match"}


def main():
    parser = argparse.ArgumentParser(description="Gateway auth consistency guard")
    sub = parser.add_subparsers(dest="command", required=True)

    p_status = sub.add_parser("status", help="Check gateway auth consistency")
    p_status.add_argument("--json", action="store_true", help="JSON output")

    p_ensure = sub.add_parser("ensure", help="Ensure gateway auth consistency")
    p_ensure.add_argument("--apply", action="store_true", help="Auto-fix by restart")
    p_ensure.add_argument("--wait", action="store_true", help="After starting gateway, wait until port is open (default 30s)")
    p_ensure.add_argument("--json", action="store_true", help="JSON output")

    p_continue = sub.add_parser("continue-on-error", help="When run error (Unhandled stop reason: error) appears in gateway.log, send 'continue' to the agent")
    p_continue.add_argument("--once", action="store_true", help="Check once and exit (default)")
    p_continue.add_argument("--loop", action="store_true", help="Loop every --interval seconds")
    p_continue.add_argument("--interval", type=int, default=30, help="Seconds between checks when --loop (default 30)")
    p_continue.add_argument("--json", action="store_true", help="JSON output")

    p_watch = sub.add_parser("watch", help="Single combined daemon: gateway-back (what-just-happened) + continue-on-error. Run once per LaunchAgent interval.")
    p_watch.add_argument("--json", action="store_true", help="JSON output (summary of both checks)")

    args = parser.parse_args()

    if args.command == "watch":
        # 0) Proactive token sync (status + ensure --apply when mismatch) — keeps gateway auth in sync so TUI doesn't hit device_token_mismatch
        ensure_ok = None
        try:
            r = subprocess.run(
                [sys.executable, str(Path(__file__).resolve()), "ensure", "--apply", "--json"],
                env={**os.environ, "OPENCLAW_HOME": str(_openclaw_home())},
                cwd=str(_openclaw_home()),
                timeout=25,
                capture_output=True,
                text=True,
            )
            if r.returncode == 0 and r.stdout.strip():
                try:
                    ensure_ok = json.loads(r.stdout.strip()).get("ok", False)
                except json.JSONDecodeError:
                    ensure_ok = False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        # 1) Gateway back (what-just-happened): run the other skill's watcher script
        wjh_script = _openclaw_home() / "workspace" / "skills" / "what-just-happened" / "scripts" / "gateway_back_watcher.py"
        wjh_ran = False
        if wjh_script.exists():
            try:
                subprocess.run(
                    [sys.executable, str(wjh_script)],
                    env={**os.environ, "OPENCLAW_HOME": str(_openclaw_home())},
                    cwd=str(_openclaw_home()),
                    timeout=25,
                    capture_output=True,
                )
                wjh_ran = True
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
        # 2) Continue-on-error
        cont_result = check_and_trigger_continue_once()
        if getattr(args, "json", False):
            print(json.dumps({"ensureOk": ensure_ok, "gatewayBackRan": wjh_ran, "continueOnError": cont_result}))
        raise SystemExit(0)

    if args.command == "continue-on-error":
        if args.loop:
            while True:
                result = check_and_trigger_continue_once()
                if args.json:
                    print(json.dumps(result), flush=True)
                elif result.get("triggered"):
                    print("Triggered: sent 'continue' to agent (run error detected).", flush=True)
                time.sleep(args.interval)
        else:
            result = check_and_trigger_continue_once()
            if args.json:
                print(json.dumps(result))
            else:
                if result.get("triggered"):
                    print("Triggered: sent 'continue' to agent (run error detected).")
                else:
                    print(f"No trigger: {result.get('reason', 'no_match')}.")
        raise SystemExit(0)

    cfg_path, cfg = load_openclaw_config()
    auth = auth_from_config(cfg)
    mode, port, secret = auth["mode"], auth["port"], auth["secret"]

    if mode not in ("token", "password"):
        out = {
            "ok": False,
            "error": f"Unsupported gateway auth mode: {mode}",
            "configPath": str(cfg_path),
        }
        print(json.dumps(out) if getattr(args, "json", False) else out["error"])
        raise SystemExit(2)

    # If secret is missing, generate one and write to config only then (overwrite only when incorrect).
    if not secret:
        if mode != "token":
            out = {
                "ok": False,
                "error": f"Missing gateway auth secret in openclaw.json for mode={mode}",
                "configPath": str(cfg_path),
            }
            print(json.dumps(out) if getattr(args, "json", False) else out["error"])
            raise SystemExit(2)
        secret = secrets.token_hex(24)
        written = write_gateway_auth_only_if_incorrect(cfg_path, cfg, mode, port, secret)
        if written:
            cfg_path, cfg = load_openclaw_config()
            auth = auth_from_config(cfg)
            mode, port, secret = auth["mode"], auth["port"], auth["secret"]

    runtime = gateway_runtime_status(port, mode, secret)
    if args.command == "status":
        result = build_result(cfg_path, mode, port, runtime, fixed=False)
        if args.json:
            print(json.dumps(result))
        else:
            print(f"Auth mode: {mode}")
            print(f"Gateway port: {port}")
            print(f"Running: {result['running']} (pid={result['pid']})")
            print(f"Secret matches config: {result['secretMatchesConfig']}")
            print(f"Reason: {result['reason']}")
        raise SystemExit(0 if result["ok"] else 1)

    # ensure
    if runtime.get("secretMatchesConfig"):
        result = build_result(cfg_path, mode, port, runtime, fixed=False)
        if args.json:
            print(json.dumps(result))
        else:
            print("Gateway auth is already consistent.")
        raise SystemExit(0)

    if not args.apply:
        result = build_result(cfg_path, mode, port, runtime, fixed=False)
        if args.json:
            print(json.dumps(result))
        else:
            print("Gateway auth mismatch detected.")
            print("Re-run with --apply to restart gateway using openclaw.json auth.")
        raise SystemExit(2)

    after = _restart_gateway(port, mode, secret)
    if getattr(args, "wait", False):
        if _wait_for_gateway_port(port):
            after = gateway_runtime_status(port, mode, secret)
            if not after.get("running"):
                after["running"] = True
                after["reason"] = "ok_after_wait"
        else:
            if not args.json:
                print("Gateway started but port not open within timeout.", file=sys.stderr)
    result = build_result(cfg_path, mode, port, after, fixed=True)
    if args.json:
        print(json.dumps(result))
    else:
        print("Gateway restart attempted.")
        print(f"Secret matches config: {result['secretMatchesConfig']}")
        print(f"PID: {result['pid']}")
    raise SystemExit(0 if result["ok"] else 2)


if __name__ == "__main__":
    main()
