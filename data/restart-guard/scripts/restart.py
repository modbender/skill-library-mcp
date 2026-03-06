#!/usr/bin/env python3
"""
restart-guard: restart.py
Main restart orchestrator.
"""

import argparse
import copy
import json
import os
import shutil
import signal
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_MAIN_SESSION = "agent:main:main"


def main():
    parser = argparse.ArgumentParser(description="Restart OpenClaw Gateway")
    parser.add_argument("--config", required=True, help="Path to restart-guard.yaml")
    parser.add_argument("--reason", default="", help="Restart reason")
    parser.add_argument("--force", action="store_true", help="Ignore cooldown lock")
    parser.add_argument(
        "--notify-mode",
        default="origin",
        help="Notification mode: origin|selected|all (default: origin)",
    )
    parser.add_argument(
        "--origin-session-key",
        default="",
        help="Source session key to receive restart ACK (default from env/context)",
    )
    parser.add_argument("--channel", default="", help="Selected notification channel")
    parser.add_argument("--target", default="", help="Selected notification target")
    # Legacy compatibility
    parser.add_argument("--notify-channel", default="", help=argparse.SUPPRESS)
    parser.add_argument("--notify-target", default="", help=argparse.SUPPRESS)
    args = parser.parse_args()

    config = load_config(args.config)
    paths = config.get("paths", {}) or {}
    safety = config.get("safety", {}) or {}
    gateway_cfg = config.get("gateway", {}) or {}
    notif_base = config.get("notification", {}) or {}

    context_path = expand(paths.get("context_file", "~/.openclaw/custom/work/restart-context.md"))
    lock_path = expand(paths.get("lock_file", "/tmp/restart-guard.lock"))
    log_path = expand(paths.get("restart_log", "~/.openclaw/custom/work/restart.log"))
    backup_dir = expand(paths.get("backup_dir", "~/.openclaw/custom/work/restart-backup"))
    oc_config = expand(paths.get("openclaw_config", "~/.openclaw/openclaw.json"))
    oc_bin = find_openclaw(paths.get("openclaw_bin", ""))

    cooldown = int(safety.get("cooldown_seconds", 600))
    max_failures = int(safety.get("max_consecutive_failures", 3))
    do_backup = to_bool(safety.get("backup_config", True))

    host = str(gateway_cfg.get("host", "127.0.0.1"))
    port = str(gateway_cfg.get("port", "18789"))
    delay_ms = int(gateway_cfg.get("restart_delay_ms", 3000))
    auth_token_env = str(gateway_cfg.get("auth_token_env", "GATEWAY_AUTH_TOKEN"))
    auth_token = os.environ.get(auth_token_env, "") or dotenv_get(auth_token_env)

    if not os.path.isfile(context_path) or os.path.getsize(context_path) == 0:
        die(f"Restart context missing or empty: {context_path}\nWrite context first (write_context.py)")
    if not oc_bin:
        die("Cannot find 'openclaw' binary. Set paths.openclaw_bin or ensure it is in PATH.")

    notify_mode = normalize_notify_mode(args.notify_mode)
    selected_channel = (args.channel or args.notify_channel or "").strip()
    selected_target = (args.target or args.notify_target or "").strip()
    origin_session_key, origin_source = resolve_origin_session_key(
        explicit=args.origin_session_key,
        context_path=context_path,
        oc_bin=oc_bin,
    )
    if not origin_session_key:
        origin_session_key = DEFAULT_MAIN_SESSION
        origin_source = "fallback-main"
    restart_id = make_restart_id()
    effective_notify_plan = build_effective_notify_plan(
        config=config,
        notify_mode=notify_mode,
        selected_channel=selected_channel,
        selected_target=selected_target,
        origin_session_key=origin_session_key,
    )

    if os.path.exists(lock_path) and not args.force:
        try:
            age = time.time() - os.path.getmtime(lock_path)
            if age < cooldown:
                die(f"Cooldown active ({int(cooldown - age)}s remaining). Use --force to override.")
        except OSError:
            pass

    failures = count_recent_failures(log_path, max_failures)
    if failures >= max_failures and not args.force:
        die(f"Consecutive failures ({failures}) >= max ({max_failures}). Manual intervention required.")

    try:
        with open(lock_path, "w", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "pid": os.getpid(),
                        "restart_id": restart_id,
                        "started_at": iso_now(),
                        "reason": args.reason,
                        "origin_session_key": origin_session_key,
                        "origin_source": origin_source,
                        "notify_mode": notify_mode,
                    },
                    ensure_ascii=False,
                )
            )
    except OSError as e:
        die(f"Cannot acquire lock: {e}")

    if do_backup and os.path.isfile(oc_config):
        os.makedirs(backup_dir, exist_ok=True)
        backup_path = os.path.join(backup_dir, "openclaw.json")
        shutil.copy2(oc_config, backup_path)
        log_entry(log_path, "backup", f"config backed up to {backup_path}", restart_id)

    selection_payload = {
        "channel": selected_channel,
        "target": selected_target,
    }
    context_updates = {
        "restart_id": restart_id,
        "origin_session_key": origin_session_key,
        "notify_mode": notify_mode,
        "channel_selection": selection_payload,
        "effective_notify_plan": effective_notify_plan,
        "state_timestamps": {"context_saved_at": iso_now()},
    }
    upsert_context_metadata(context_path, context_updates)
    snapshot_path = write_restart_snapshot(
        context_path=context_path,
        restart_id=restart_id,
        reason=args.reason or "(see context)",
        origin_session_key=origin_session_key,
        notify_mode=notify_mode,
        selection=selection_payload,
        effective_notify_plan=effective_notify_plan,
    )
    log_entry(log_path, "context_saved", f"snapshot={snapshot_path}", restart_id)

    rc = subprocess.call(
        [oc_bin, "doctor", "--non-interactive"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if rc != 0:
        log_entry(log_path, "precheck_fail", f"openclaw doctor rc={rc}", restart_id)
        runtime_notif = select_runtime_notification(
            notif_base, notify_mode, selected_channel, selected_target
        )
        notify(runtime_notif, config, oc_bin, f"[restart-guard] restart aborted: precheck failed (rc={rc})")
        cleanup_lock(lock_path)
        sys.exit(1)
    log_entry(log_path, "precheck_ok", "", restart_id)

    guardian_py = os.path.join(SCRIPT_DIR, "guardian.py")
    guardian_log = os.path.join(os.path.dirname(context_path), "guardian.log")
    guardian_cmd = [
        sys.executable,
        guardian_py,
        "--config",
        args.config,
        "--restart-id",
        restart_id,
        "--context-path",
        context_path,
        "--context-snapshot",
        snapshot_path,
        "--origin-session-key",
        origin_session_key,
        "--notify-mode",
        notify_mode,
    ]
    if selected_channel:
        guardian_cmd.extend(["--channel", selected_channel])
    if selected_target:
        guardian_cmd.extend(["--target", selected_target])

    with open(guardian_log, "a", encoding="utf-8") as glog:
        guardian_proc = subprocess.Popen(
            guardian_cmd,
            stdout=glog,
            stderr=glog,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
        )
    log_entry(
        log_path,
        "guardian_spawned",
        f"pid={guardian_proc.pid} mode={notify_mode} channel={selected_channel or '-'}",
        restart_id,
    )
    log_entry(log_path, "origin_session", f"source={origin_source}; key={origin_session_key}", restart_id)

    announce_disaster_route(
        oc_bin=oc_bin,
        origin_session_key=origin_session_key,
        restart_id=restart_id,
        reason=args.reason or "(see context file)",
        effective_notify_plan=effective_notify_plan,
        log_path=log_path,
    )

    pre_notif = select_runtime_notification(notif_base, notify_mode, selected_channel, selected_target)
    if should_send_pre_notification(notify_mode, selected_channel):
        notify(
            pre_notif,
            config,
            oc_bin,
            (
                "[restart-guard] preparing restart\n"
                f"- restart_id: {restart_id}\n"
                f"- reason: {args.reason or '(see context file)'}\n"
                f"- notify_mode: {notify_mode}"
            ),
        )

    ok, method, detail = trigger_restart(host, port, delay_ms, auth_token, oc_bin)
    if ok:
        log_entry(log_path, "triggered", f"method={method}; {detail}", restart_id)
        print(f"Restart triggered ({method}). Guardian is monitoring. restart_id={restart_id}")
        sys.exit(0)

    log_entry(log_path, "trigger_failed", detail, restart_id)
    ack_ok, ack_note = report_trigger_failure_to_origin(
        oc_bin=oc_bin,
        origin_session_key=origin_session_key,
        restart_id=restart_id,
        detail=detail,
    )
    if ack_ok:
        log_entry(log_path, "trigger_failed_ack_origin", ack_note, restart_id)
    else:
        log_entry(log_path, "trigger_failed_ack_origin_failed", ack_note, restart_id)
    notify(pre_notif, config, oc_bin, f"[restart-guard] restart trigger failed: {detail}")
    # Keep guardian alive for fallback recovery and deterministic failure delivery.
    print(
        "Restart trigger failed, guardian fallback remains active. "
        f"restart_id={restart_id}; detail={detail}"
    )
    sys.exit(0)


def normalize_notify_mode(raw):
    mode = (raw or "").strip().lower()
    if mode not in {"origin", "selected", "all"}:
        return "origin"
    return mode


def to_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


def should_send_pre_notification(notify_mode, channel):
    if notify_mode == "all":
        return True
    if notify_mode == "selected":
        return (channel or "").strip().lower() not in {"", "none", "off", "disabled", "webui"}
    return False


def build_effective_notify_plan(config, notify_mode, selected_channel, selected_target, origin_session_key):
    channels_payload = discover_notify_channels(config)
    external = []
    targets = {}
    seen = set()
    for item in channels_payload.get("choices", []):
        if not isinstance(item, dict):
            continue
        if item.get("enabled") is not True:
            continue
        cid = str(item.get("id", "")).strip().lower()
        if not cid or cid in {"webui", "none", "off", "disabled"}:
            continue
        if cid not in seen:
            seen.add(cid)
            external.append(cid)
        st = str(item.get("suggestedTarget", "")).strip()
        if st:
            targets[cid] = st
    return {
        "mode": notify_mode,
        "origin_session_key": origin_session_key,
        "selected": {"channel": selected_channel, "target": selected_target},
        "emergency_policy": "origin_then_all",
        "emergency_route": ["origin_session", DEFAULT_MAIN_SESSION, "external_broadcast"],
        "external_channels": external,
        "external_targets": targets,
    }


def discover_notify_channels(config):
    try:
        sys.path.insert(0, SCRIPT_DIR)
        from discover_channels import discover_channels as _discover

        payload = _discover(config)
        if isinstance(payload, dict):
            return payload
    except Exception:
        pass
    return {"choices": []}


def announce_disaster_route(
    oc_bin,
    origin_session_key,
    restart_id,
    reason,
    effective_notify_plan,
    log_path,
):
    session_key = (origin_session_key or "").strip() or DEFAULT_MAIN_SESSION
    external = effective_notify_plan.get("external_channels", [])
    ext_text = ", ".join(external) if external else "(none configured)"
    msg = (
        "[restart-guard] restart accepted\n"
        f"- restart_id: {restart_id}\n"
        f"- origin_session_key: {session_key}\n"
        f"- reason: {reason}\n"
        "- disaster_delivery_route: origin_session -> agent:main:main -> external_broadcast\n"
        f"- disaster_external_channels: {ext_text}"
    )
    ok, note = send_agent_message(oc_bin, session_key, msg)
    if not ok:
        log_entry(log_path, "announce_route_failed", note, restart_id)


def resolve_origin_session_key(explicit, context_path, oc_bin):
    if explicit and explicit.strip():
        return explicit.strip(), "explicit"
    env_key = os.environ.get("OPENCLAW_SESSION_KEY", "").strip()
    if env_key:
        return env_key, "env"
    fm = read_context_frontmatter(context_path)
    val = str((fm or {}).get("origin_session_key", "")).strip()
    if val:
        return val, "context"
    inferred = infer_origin_session_key_from_sessions(oc_bin)
    if inferred:
        return inferred, "sessions"
    return "", "none"


def infer_origin_session_key_from_sessions(oc_bin):
    if not oc_bin:
        return ""
    payload = call_sessions_json(oc_bin)
    if not isinstance(payload, dict):
        return ""
    return select_origin_session_key_from_payload(payload)


def call_sessions_json(oc_bin):
    try:
        proc = subprocess.run(
            [oc_bin, "sessions", "--agent", "main", "--json"],
            capture_output=True,
            text=True,
            timeout=20,
        )
        if proc.returncode != 0:
            return {}
        return json.loads(proc.stdout or "{}")
    except Exception:
        return {}


def select_origin_session_key_from_payload(payload):
    candidates = []
    if not isinstance(payload, dict):
        return ""

    sessions_root = payload.get("sessions")
    # Shape A: `openclaw sessions --agent main --json`
    # { path, count, sessions: [ {key, updatedAt, ...}, ... ] }
    if isinstance(sessions_root, list):
        candidates.extend([x for x in sessions_root if isinstance(x, dict)])
    # Shape B: aggregate output with byAgent/recent containers.
    elif isinstance(sessions_root, dict):
        recent = sessions_root.get("recent", [])
        if isinstance(recent, list):
            candidates.extend(recent)
        by_agent = sessions_root.get("byAgent", [])
        if isinstance(by_agent, list):
            for item in by_agent:
                if not isinstance(item, dict):
                    continue
                if str(item.get("agentId", "")).strip() != "main":
                    continue
                rs = item.get("recent", [])
                if isinstance(rs, list):
                    candidates.extend(rs)

    ranked = []
    seen = set()
    for c in candidates:
        if not isinstance(c, dict):
            continue
        key = str(c.get("key", "")).strip()
        if not key or key in seen:
            continue
        seen.add(key)
        if not key.startswith("agent:main:"):
            continue
        if ":cron:" in key:
            continue
        flags = c.get("flags", []) if isinstance(c.get("flags", []), list) else []
        is_system = "system" in [str(x).strip().lower() for x in flags]
        updated = int(c.get("updatedAt", 0) or 0)
        priority = 1 if is_system else 0
        ranked.append((priority, -updated, key))

    if ranked:
        ranked.sort()
        return ranked[0][2]
    return ""


def upsert_context_metadata(context_path, updates):
    upsert_markdown_frontmatter(context_path, updates)


def write_restart_snapshot(
    context_path,
    restart_id,
    reason,
    origin_session_key,
    notify_mode,
    selection,
    effective_notify_plan,
):
    snapshot = {
        "restart_id": restart_id,
        "reason": reason,
        "context_path": context_path,
        "origin_session_key": origin_session_key,
        "notify_mode": notify_mode,
        "channel_selection": selection,
        "effective_notify_plan": effective_notify_plan,
        "created_at": iso_now(),
    }
    snap_path = os.path.join(os.path.dirname(context_path), f"restart-state-{restart_id}.json")
    atomic_write(snap_path, json.dumps(snapshot, ensure_ascii=False, indent=2))
    return snap_path


def make_restart_id():
    return f"rg-{int(time.time() * 1000)}-{uuid.uuid4().hex[:8]}"


def iso_now():
    return datetime.now(timezone.utc).astimezone().isoformat()


def expand(p):
    return os.path.expanduser(p) if p else p


def select_runtime_notification(base_notif, notify_mode, channel, target):
    notif = copy.deepcopy(base_notif if isinstance(base_notif, dict) else {})
    if notify_mode == "all":
        return notif
    if notify_mode == "selected":
        return apply_notification_override(notif, channel, target)
    # origin mode only uses out-of-band channels as guardian fallback.
    return notif


def apply_notification_override(base_notif, channel, target):
    notif = copy.deepcopy(base_notif if isinstance(base_notif, dict) else {})
    ch = (channel or "").strip().lower()
    tgt = (target or "").strip()
    if not ch:
        return notif
    if ch in {"none", "off", "disabled"}:
        notif["primary"] = "none"
        notif["channels"] = []
        return notif
    if ch == "webui":
        notif["primary"] = "none"
        notif["channels"] = []
        return notif

    oc = notif.get("openclaw", {})
    if not isinstance(oc, dict):
        oc = {}
    oc["channel"] = ch
    if tgt:
        oc["target"] = tgt
        oc["to"] = tgt
    notif["openclaw"] = oc
    notif["primary"] = "openclaw"
    notif["channels"] = []
    return notif


def is_local_host(host):
    h = (host or "").strip().lower()
    return h in {"127.0.0.1", "localhost", "::1"}


def trigger_restart(host, port, delay_ms, auth_token, oc_bin):
    notes = []

    http_code, timed_out, err = trigger_restart_http(host, port, delay_ms, auth_token)
    if timed_out:
        return True, "http-timeout", "gateway may already be restarting"
    if http_code == "200":
        return True, "http", f"http={http_code}"
    if http_code:
        notes.append(f"http={http_code}")
    if err:
        notes.append(f"http_err={err}")

    sig_ok, sig_note = trigger_restart_signal(host, port)
    if sig_ok:
        return True, "signal", sig_note
    if sig_note:
        notes.append(f"signal={sig_note}")

    cli_ok, cli_note = trigger_restart_cli(oc_bin)
    if cli_ok:
        return True, "cli", cli_note
    if cli_note:
        notes.append(f"cli={cli_note}")

    return False, "", "; ".join(notes) if notes else "unknown trigger failure"


def trigger_restart_http(host, port, delay_ms, auth_token):
    if not auth_token:
        return "", False, "missing-auth-token"
    try:
        host, port = validate_host_port(host, port)
    except ValueError as e:
        return "", False, f"invalid-host-port: {e}"


def validate_host_port(host, port):
    """Import from write_context for backwards compatibility."""
    sys.path.insert(0, SCRIPT_DIR)
    from write_context import validate_host_port as _validate
    return _validate(host, port)
    url = f"http://{host}:{port}/tools/invoke"
    payload = json.dumps(
        {
            "tool": "gateway",
            "action": "restart",
            "args": {"delayMs": int(delay_ms)},
            "sessionKey": "main",
        }
    )
    try:
        result = subprocess.run(
            [
                "curl",
                "-sS",
                "-o",
                "/dev/null",
                "-w",
                "%{http_code}",
                "-H",
                f"Authorization: Bearer {auth_token}",
                "-H",
                "Content-Type: application/json",
                "-d",
                payload,
                url,
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.stdout.strip(), False, ""
    except subprocess.TimeoutExpired:
        return "", True, "timeout"
    except Exception as e:
        return "", False, str(e)


def trigger_restart_signal(host, port):
    if not is_local_host(host):
        return False, "non-local-host"
    lsof_bin = find_lsof_bin()
    if not lsof_bin:
        return False, "lsof_missing"
    try:
        result = subprocess.run(
            [lsof_bin, "-nP", f"-iTCP:{port}", "-sTCP:LISTEN", "-t"],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except Exception as e:
        return False, f"lsof_error={e}"

    pids = [x.strip() for x in (result.stdout or "").splitlines() if x.strip().isdigit()]
    if not pids:
        return False, "no-listener-pid"

    for pid in pids:
        try:
            ps = subprocess.run(
                ["ps", "-p", pid, "-o", "command="],
                capture_output=True,
                text=True,
                timeout=5,
            )
            cmdline = (ps.stdout or "").strip().lower()
            if cmdline and ("openclaw" not in cmdline and "gateway" not in cmdline):
                continue
            kill = subprocess.run(
                ["kill", "-USR1", pid],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if kill.returncode == 0:
                return True, f"pid={pid}"
        except Exception:
            continue
    return False, "listener-not-openclaw-or-sigusr1-failed"


def trigger_restart_cli(oc_bin):
    if not oc_bin:
        return False, "missing-openclaw-bin"
    try:
        result = subprocess.run(
            [oc_bin, "gateway", "restart"],
            capture_output=True,
            text=True,
            timeout=90,
        )
        if result.returncode == 0:
            return True, "openclaw gateway restart"
        msg = (result.stderr or result.stdout or "").strip().splitlines()
        first = msg[0][:200] if msg else f"rc={result.returncode}"
        return False, f"rc={result.returncode}:{first}"
    except Exception as e:
        return False, str(e)


def report_trigger_failure_to_origin(oc_bin, origin_session_key, restart_id, detail):
    session_key = (origin_session_key or "").strip() or DEFAULT_MAIN_SESSION
    message = (
        "[restart_guard.result.v1]\n"
        "status: fail\n"
        "severity: critical\n"
        f"restart_id: {restart_id}\n"
        "failure_phase: TRIGGER\n"
        "error_code: TRIGGER_FAILED\n"
        "delivery_route: origin_session\n"
        f"note: restart trigger failed: {detail}\n"
        "action_required:\n"
        "1. Wait for guardian fallback result in this session.\n"
        "2. If no follow-up arrives, run postcheck and inspect restart.log/guardian.log.\n"
    )
    return send_agent_message(oc_bin, session_key, message)


def send_agent_message(oc_bin, session_key, message):
    if not oc_bin:
        return False, "missing openclaw binary"
    params = {
        "message": message,
        "sessionKey": session_key,
        "idempotencyKey": f"restart-guard-{uuid.uuid4().hex}",
    }
    try:
        proc = subprocess.run(
            [
                oc_bin,
                "gateway",
                "call",
                "agent",
                "--json",
                "--timeout",
                "15000",
                "--params",
                json.dumps(params, ensure_ascii=False),
            ],
            capture_output=True,
            text=True,
            timeout=20,
        )
        if proc.returncode == 0:
            return True, "accepted"
        err = (proc.stderr or proc.stdout or "").strip()[:300]
        return False, f"rc={proc.returncode} {err}"
    except Exception as e:
        return False, str(e)


def find_openclaw(configured):
    if configured:
        p = expand(configured)
        if os.path.isfile(p) and os.access(p, os.X_OK):
            return p
    p = shutil.which("openclaw")
    if p:
        return p
    import glob

    candidates = sorted(glob.glob(os.path.expanduser("~/.nvm/versions/node/*/bin/openclaw")))
    return candidates[-1] if candidates else None


def find_lsof_bin():
    p = shutil.which("lsof")
    if p and os.path.isfile(p) and os.access(p, os.X_OK):
        return p
    for candidate in ("/usr/sbin/lsof", "/usr/bin/lsof"):
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
    return ""


def dotenv_get(key):
    env_file = os.path.expanduser("~/.openclaw/.env")
    if not os.path.isfile(env_file):
        return ""
    with open(env_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith(f"{key}="):
                return line[len(key) + 1 :].strip().strip('"').strip("'")
    return ""


def log_entry(path, result, note, restart_id=""):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    ts = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S.%f %z")
    rid = restart_id or "-"
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"- {ts} result={result} restart_id={rid} note={note}\n")


def count_recent_failures(log_path, window):
    if not os.path.isfile(log_path):
        return 0
    count = 0
    with open(log_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    for line in reversed(lines):
        if "result=ok" in line or "result=triggered" in line:
            break
        if (
            "result=timeout" in line
            or "result=trigger_failed" in line
            or "result=trigger_error" in line
            or "result=failed" in line
        ):
            count += 1
    return min(count, window)


def cleanup_lock(lock_path):
    try:
        os.remove(lock_path)
    except OSError:
        pass


def stop_guardian_process(proc):
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except Exception:
        pass


def notify(notif_config, full_config, oc_bin, message):
    sys.path.insert(0, SCRIPT_DIR)
    from notify import notify as _notify

    _notify(notif_config, full_config, oc_bin, message)


def load_config(path):
    sys.path.insert(0, SCRIPT_DIR)
    from write_context import load_config as _load

    return _load(path)


def upsert_markdown_frontmatter(path, updates):
    sys.path.insert(0, SCRIPT_DIR)
    from write_context import upsert_markdown_frontmatter as _upsert

    _upsert(path, updates)


def read_context_frontmatter(path):
    sys.path.insert(0, SCRIPT_DIR)
    from write_context import parse_markdown_frontmatter as _parse

    data, _ = _parse(path)
    return data


def atomic_write(path, content):
    sys.path.insert(0, SCRIPT_DIR)
    from write_context import atomic_write as _atomic_write

    _atomic_write(path, content)


def die(msg):
    print(f"restart-guard: {msg}", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
