#!/usr/bin/env python3
"""
restart-guard: guardian.py
Detached watchdog process that guarantees restart state transitions.
"""

import argparse
import copy
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_MAIN_SESSION = "agent:main:main"
SHELL_METACHARS = ("|", ">", "<", ";", "&&", "||", "$(", "`")


def main():
    parser = argparse.ArgumentParser(description="Restart Guard: detached guardian")
    parser.add_argument("--config", required=True, help="Path to restart-guard.yaml")
    parser.add_argument("--restart-id", required=True, help="Restart id from restart.py")
    parser.add_argument("--context-path", default="", help="Restart context file")
    parser.add_argument("--context-snapshot", default="", help="Restart context snapshot JSON")
    parser.add_argument("--origin-session-key", default="", help="Origin session key")
    parser.add_argument("--notify-mode", default="origin", help="origin|selected|all")
    parser.add_argument("--channel", default="", help="Selected channel")
    parser.add_argument("--target", default="", help="Selected target")
    # Legacy compatibility
    parser.add_argument("--notify-channel", default="", help=argparse.SUPPRESS)
    parser.add_argument("--notify-target", default="", help=argparse.SUPPRESS)
    args = parser.parse_args()

    config = load_config(args.config)
    paths = config.get("paths", {}) or {}
    guardian_cfg = config.get("guardian", {}) or {}
    notif_base = config.get("notification", {}) or {}
    gateway_cfg = config.get("gateway", {}) or {}

    context_path = (
        expand(args.context_path)
        if args.context_path
        else expand(paths.get("context_file", "~/.openclaw/custom/work/restart-context.md"))
    )
    context_snapshot = expand(args.context_snapshot) if args.context_snapshot else ""
    lock_path = expand(paths.get("lock_file", "/tmp/restart-guard.lock"))
    log_path = expand(paths.get("restart_log", "~/.openclaw/custom/work/restart.log"))
    oc_bin = find_openclaw(paths.get("openclaw_bin", ""))
    restart_id = args.restart_id

    channel = (args.channel or args.notify_channel or "").strip()
    target = (args.target or args.notify_target or "").strip()
    notify_mode = normalize_notify_mode(args.notify_mode)
    runtime_notif = select_runtime_notification(notif_base, notify_mode, channel, target)
    origin_session_key = resolve_origin_session_key(args.origin_session_key, context_path)

    poll_interval = float(guardian_cfg.get("poll_interval", 2))
    wait_down_timeout_ms = int(
        guardian_cfg.get("wait_down_timeout_ms", int(guardian_cfg.get("timeout", 120)) * 1000)
    )
    wait_up_timeout_ms = int(
        guardian_cfg.get("wait_up_timeout_ms", int(guardian_cfg.get("timeout", 120)) * 1000)
    )
    health_success_streak = int(guardian_cfg.get("health_success_streak", 2))
    delivery_retry_budget_ms = int(guardian_cfg.get("delivery_retry_budget_ms", 90000))
    delivery_retry_interval_ms = int(guardian_cfg.get("delivery_retry_interval_ms", 2000))
    diagnostics_log_tail = int(guardian_cfg.get("diagnostics_log_tail", 80))
    diag_commands = normalize_list(
        guardian_cfg.get(
            "diagnostics",
            [
                "openclaw doctor --non-interactive",
                f"openclaw logs --tail {max(10, diagnostics_log_tail)}",
            ],
        )
    )
    if not diag_commands:
        diag_commands = [
            "openclaw doctor --non-interactive",
            f"openclaw logs --tail {max(10, diagnostics_log_tail)}",
        ]

    host = str(gateway_cfg.get("host", "127.0.0.1"))
    port = str(gateway_cfg.get("port", "18789"))

    guard_lock = f"{lock_path}.{restart_id}.guardian.lock"
    if not acquire_guard_lock(guard_lock):
        log_entry(log_path, "guardian_skip", f"duplicate_guardian restart_id={restart_id}", restart_id)
        return

    state_timestamps = {"guardian_started_at": iso_now()}
    start_monotonic = time.monotonic()
    health_trace = []
    record_state(log_path, restart_id, "WAIT_DOWN", "guardian started")
    merge_context_state(
        context_path,
        context_snapshot,
        {
            "restart_id": restart_id,
            "origin_session_key": origin_session_key,
            "notify_mode": notify_mode,
            "channel_selection": {"channel": channel, "target": target},
            "state_timestamps": state_timestamps,
        },
    )

    down_detected, down_note = wait_for_down(
        oc_bin=oc_bin,
        host=host,
        port=port,
        timeout_ms=wait_down_timeout_ms,
        poll_interval_s=poll_interval,
        on_probe=make_probe_callback(health_trace, "WAIT_DOWN"),
    )
    if not down_detected:
        state_timestamps["failed_at"] = iso_now()
        finish_failure(
            restart_id=restart_id,
            failure_phase="WAIT_DOWN",
            error_code="WAIT_DOWN_TIMEOUT",
            note=down_note,
            oc_bin=oc_bin,
            log_path=log_path,
            lock_path=lock_path,
            guard_lock=guard_lock,
            state_timestamps=state_timestamps,
            context_path=context_path,
            context_snapshot=context_snapshot,
            origin_session_key=origin_session_key,
            runtime_notif=runtime_notif,
            full_config=config,
            notify_mode=notify_mode,
            channel=channel,
            target=target,
            diag_commands=diag_commands,
            health_trace=health_trace,
            delivery_retry_budget_ms=delivery_retry_budget_ms,
            delivery_retry_interval_ms=delivery_retry_interval_ms,
            elapsed_ms=int((time.monotonic() - start_monotonic) * 1000),
        )
        return

    state_timestamps["down_detected_at"] = iso_now()
    record_state(log_path, restart_id, "START_GATEWAY", down_note)
    start_attempted = True
    start_ok, start_method, start_note = start_gateway(oc_bin)
    if not start_ok and not check_health(oc_bin, host, port):
        state_timestamps["failed_at"] = iso_now()
        finish_failure(
            restart_id=restart_id,
            failure_phase="START_GATEWAY",
            error_code="START_GATEWAY_FAILED",
            note=start_note,
            oc_bin=oc_bin,
            log_path=log_path,
            lock_path=lock_path,
            guard_lock=guard_lock,
            state_timestamps=state_timestamps,
            context_path=context_path,
            context_snapshot=context_snapshot,
            origin_session_key=origin_session_key,
            runtime_notif=runtime_notif,
            full_config=config,
            notify_mode=notify_mode,
            channel=channel,
            target=target,
            diag_commands=diag_commands,
            health_trace=health_trace,
            delivery_retry_budget_ms=delivery_retry_budget_ms,
            delivery_retry_interval_ms=delivery_retry_interval_ms,
            elapsed_ms=int((time.monotonic() - start_monotonic) * 1000),
        )
        return
    state_timestamps["start_gateway_at"] = iso_now()

    record_state(log_path, restart_id, "WAIT_UP_HEALTHY", start_method or "start_attempted")
    up_healthy, up_note = wait_for_up_healthy(
        oc_bin=oc_bin,
        host=host,
        port=port,
        timeout_ms=wait_up_timeout_ms,
        poll_interval_s=poll_interval,
        success_streak=max(1, health_success_streak),
        on_probe=make_probe_callback(health_trace, "WAIT_UP_HEALTHY"),
    )
    if not up_healthy:
        state_timestamps["failed_at"] = iso_now()
        finish_failure(
            restart_id=restart_id,
            failure_phase="WAIT_UP_HEALTHY",
            error_code="WAIT_UP_TIMEOUT",
            note=up_note,
            oc_bin=oc_bin,
            log_path=log_path,
            lock_path=lock_path,
            guard_lock=guard_lock,
            state_timestamps=state_timestamps,
            context_path=context_path,
            context_snapshot=context_snapshot,
            origin_session_key=origin_session_key,
            runtime_notif=runtime_notif,
            full_config=config,
            notify_mode=notify_mode,
            channel=channel,
            target=target,
            diag_commands=diag_commands,
            health_trace=health_trace,
            delivery_retry_budget_ms=delivery_retry_budget_ms,
            delivery_retry_interval_ms=delivery_retry_interval_ms,
            elapsed_ms=int((time.monotonic() - start_monotonic) * 1000),
        )
        return
    state_timestamps["up_healthy_at"] = iso_now()

    if not is_restart_successful(down_detected, start_attempted, up_healthy):
        state_timestamps["failed_at"] = iso_now()
        finish_failure(
            restart_id=restart_id,
            failure_phase="INVARIANT",
            error_code="STATE_INVARIANT_FAILED",
            note="required: down_detected && start_attempted && up_healthy",
            oc_bin=oc_bin,
            log_path=log_path,
            lock_path=lock_path,
            guard_lock=guard_lock,
            state_timestamps=state_timestamps,
            context_path=context_path,
            context_snapshot=context_snapshot,
            origin_session_key=origin_session_key,
            runtime_notif=runtime_notif,
            full_config=config,
            notify_mode=notify_mode,
            channel=channel,
            target=target,
            diag_commands=diag_commands,
            health_trace=health_trace,
            delivery_retry_budget_ms=delivery_retry_budget_ms,
            delivery_retry_interval_ms=delivery_retry_interval_ms,
            elapsed_ms=int((time.monotonic() - start_monotonic) * 1000),
        )
        return

    elapsed_ms = int((time.monotonic() - start_monotonic) * 1000)
    event = build_event_payload(
        status="ok",
        restart_id=restart_id,
        context_path=context_path,
        context_snapshot=context_snapshot,
        notify_mode=notify_mode,
        channel=channel,
        target=target,
        elapsed_ms=elapsed_ms,
        state_timestamps=state_timestamps,
        note=up_note if up_note else start_note,
        severity="info",
        failure_phase="",
        error_code="",
        diagnostics_summary="",
        diagnostics_file="",
    )
    record_state(log_path, restart_id, "ACK_ORIGIN_SESSION", "sending success event")
    ack = deliver_result_with_budget(
        oc_bin=oc_bin,
        origin_session_key=origin_session_key,
        event=event,
        runtime_notif=runtime_notif,
        full_config=config,
        retry_budget_ms=delivery_retry_budget_ms,
        retry_interval_ms=delivery_retry_interval_ms,
    )
    if ack.get("ok", False):
        state_timestamps["ack_sent_at"] = iso_now()
    else:
        state_timestamps["delivery_exhausted_at"] = iso_now()

    final_status = "ok" if ack.get("ok", False) else "ack_failed"
    note = (
        f"start={start_method or 'attempted'}; up={up_note}; "
        f"ack_via={ack.get('via', 'none')}; ack_note={ack.get('note', '')}; "
        f"delivery_attempts={ack.get('attempts', 0)}"
    )
    if ack.get("delivery_exhausted"):
        log_entry(
            log_path,
            "delivery_exhausted",
            f"status=ok; note={ack.get('note', '')}",
            restart_id,
        )
    log_entry(log_path, final_status, note, restart_id)
    merge_context_state(
        context_path,
        context_snapshot,
        {
            "last_result": "ok",
            "last_note": note,
            "delivery_status": "delivered" if ack.get("ok", False) else "delivery_exhausted",
            "state_timestamps": state_timestamps,
        },
    )
    cleanup_lock(lock_path)
    cleanup_lock(guard_lock)
    if ack.get("ok", False):
        return
    sys.exit(1)


def is_restart_successful(down_detected, start_attempted, up_healthy):
    return bool(down_detected and start_attempted and up_healthy)


def wait_for_down(
    oc_bin,
    host,
    port,
    timeout_ms,
    poll_interval_s,
    now_fn=None,
    sleep_fn=None,
    on_probe=None,
):
    now_fn = now_fn or time.monotonic
    sleep_fn = sleep_fn or time.sleep
    deadline = now_fn() + max(0, timeout_ms) / 1000.0
    while now_fn() <= deadline:
        healthy = check_health(oc_bin, host, port)
        if on_probe:
            on_probe(healthy)
        if not healthy:
            return True, "gateway unreachable/down observed"
        sleep_fn(max(0.2, poll_interval_s))
    return False, f"timeout={timeout_ms}ms (no down transition observed)"


def wait_for_up_healthy(
    oc_bin,
    host,
    port,
    timeout_ms,
    poll_interval_s,
    success_streak,
    now_fn=None,
    sleep_fn=None,
    on_probe=None,
):
    now_fn = now_fn or time.monotonic
    sleep_fn = sleep_fn or time.sleep
    deadline = now_fn() + max(0, timeout_ms) / 1000.0
    streak = 0
    while now_fn() <= deadline:
        healthy = check_health(oc_bin, host, port)
        if on_probe:
            on_probe(healthy, streak)
        if healthy:
            streak += 1
            if streak >= success_streak:
                return True, f"healthy streak={streak}"
        else:
            streak = 0
        sleep_fn(max(0.2, poll_interval_s))
    return False, f"timeout={timeout_ms}ms (healthy streak < {success_streak})"


def start_gateway(oc_bin):
    if not oc_bin:
        return False, "", "missing openclaw binary"
    attempts = [
        [oc_bin, "gateway", "start"],
        [oc_bin, "gateway", "restart"],
    ]
    notes = []
    for cmd in attempts:
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
            if proc.returncode == 0:
                return True, " ".join(cmd[1:]), "ok"
            msg = (proc.stderr or proc.stdout or "").strip().splitlines()
            notes.append(f"{' '.join(cmd[1:])}: rc={proc.returncode} {msg[0][:180] if msg else ''}")
        except Exception as e:
            notes.append(f"{' '.join(cmd[1:])}: {e}")
    return False, "", "; ".join(notes)


def check_health(oc_bin, host, port):
    if oc_bin:
        for cmd in (
            [oc_bin, "gateway", "health", "--json", "--timeout", "5000"],
            [oc_bin, "health", "--json", "--timeout", "5000"],
        ):
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                if result.returncode != 0:
                    continue
                data = json.loads(result.stdout or "{}")
                if data.get("ok") is True or str(data.get("status", "")).lower() == "ok":
                    return True
            except Exception:
                continue
    return check_health_curl(host, port)


def check_health_curl(host, port):
    try:
        try:
            from write_context import validate_host_port
            host, port = validate_host_port(host, port)
        except ValueError:
            return False
        result = subprocess.run(
            ["curl", "-sS", "--max-time", "5", f"http://{host}:{port}/health"],
            capture_output=True,
            text=True,
            timeout=8,
        )
        if result.returncode != 0:
            return False
        body = (result.stdout or "").lower()
        return "ok" in body or '"status":"ok"' in body
    except Exception:
        return False


def finish_failure(
    restart_id,
    failure_phase,
    error_code,
    note,
    oc_bin,
    log_path,
    lock_path,
    guard_lock,
    state_timestamps,
    context_path,
    context_snapshot,
    origin_session_key,
    runtime_notif,
    full_config,
    notify_mode,
    channel,
    target,
    diag_commands,
    health_trace,
    delivery_retry_budget_ms,
    delivery_retry_interval_ms,
    elapsed_ms,
):
    diag_bundle = build_diagnostics_bundle(
        oc_bin=oc_bin,
        diag_commands=diag_commands,
        failure_phase=failure_phase,
        error_code=error_code,
        note=note,
        health_trace=health_trace,
    )
    diagnostics_path = write_diagnostics_bundle(context_path, restart_id, diag_bundle)
    summary = summarize_diagnostics_bundle(diag_bundle, diagnostics_path)
    event = build_event_payload(
        status="fail",
        restart_id=restart_id,
        context_path=context_path,
        context_snapshot=context_snapshot,
        notify_mode=notify_mode,
        channel=channel,
        target=target,
        elapsed_ms=elapsed_ms,
        state_timestamps=state_timestamps,
        note=f"{error_code}: {note}",
        severity="critical",
        failure_phase=failure_phase,
        error_code=error_code,
        diagnostics_summary=summary,
        diagnostics_file=diagnostics_path,
    )
    ack = deliver_result_with_budget(
        oc_bin=oc_bin,
        origin_session_key=origin_session_key,
        event=event,
        runtime_notif=runtime_notif,
        full_config=full_config,
        retry_budget_ms=delivery_retry_budget_ms,
        retry_interval_ms=delivery_retry_interval_ms,
    )
    log_entry(
        log_path,
        "failed",
        (
            f"error_code={error_code}; note={note}; "
            f"ack_via={ack.get('via', 'none')}; ack_note={ack.get('note', '')}; "
            f"delivery_attempts={ack.get('attempts', 0)}"
        ),
        restart_id,
    )
    if ack.get("ok", False):
        state_timestamps["ack_sent_at"] = iso_now()
    else:
        state_timestamps["delivery_exhausted_at"] = iso_now()
    if ack.get("delivery_exhausted"):
        log_entry(
            log_path,
            "delivery_exhausted",
            f"status=fail; error_code={error_code}; note={ack.get('note', '')}",
            restart_id,
        )
    merge_context_state(
        context_path,
        context_snapshot,
        {
            "last_result": "failed",
            "last_note": f"{error_code}: {note}",
            "diagnostics_file": diagnostics_path,
            "delivery_status": "delivered" if ack.get("ok", False) else "delivery_exhausted",
            "state_timestamps": state_timestamps,
        },
    )
    cleanup_lock(lock_path)
    cleanup_lock(guard_lock)
    sys.exit(1)


def build_event_payload(
    status,
    restart_id,
    context_path,
    context_snapshot,
    notify_mode,
    channel,
    target,
    elapsed_ms,
    state_timestamps,
    note,
    severity,
    failure_phase,
    error_code,
    diagnostics_summary,
    diagnostics_file,
):
    return {
        "event_type": "restart_guard.result.v1",
        "status": status,
        "severity": severity,
        "restart_id": restart_id,
        "context_file": context_path,
        "context_snapshot": context_snapshot,
        "notify_mode": notify_mode,
        "channel_selection": {"channel": channel, "target": target},
        "elapsed_ms": elapsed_ms,
        "state_timestamps": state_timestamps,
        "note": note,
        "failure_phase": failure_phase,
        "error_code": error_code,
        "diagnostics_summary": diagnostics_summary,
        "diagnostics_file": diagnostics_file,
        "delivery_attempts": 0,
        "delivery_route": "",
        "delivery_exhausted": False,
        "event_time": iso_now(),
    }


def deliver_result_with_budget(
    oc_bin,
    origin_session_key,
    event,
    runtime_notif,
    full_config,
    retry_budget_ms=90000,
    retry_interval_ms=2000,
    now_fn=None,
    sleep_fn=None,
):
    now_fn = now_fn or time.monotonic
    sleep_fn = sleep_fn or time.sleep
    session_key = (origin_session_key or "").strip()
    origin_route = session_key or DEFAULT_MAIN_SESSION
    emergency_notif = build_emergency_notification(runtime_notif, full_config)
    deadline = now_fn() + max(1000, int(retry_budget_ms)) / 1000.0
    attempts = 0
    notes = []

    while True:
        attempts += 1
        event_attempt = dict(event)
        event_attempt["delivery_attempts"] = attempts
        event_attempt["delivery_exhausted"] = False

        msg = format_agent_event_message(event_attempt)
        ok, note = send_agent_message(oc_bin, origin_route, msg)
        if ok:
            return {
                "ok": True,
                "via": "agent",
                "session_key": origin_route,
                "note": note,
                "attempts": attempts,
                "delivery_exhausted": False,
            }
        notes.append(f"origin:{note}")

        if origin_route != DEFAULT_MAIN_SESSION:
            event_main = dict(event_attempt)
            event_main["delivery_route"] = "main_session"
            msg_main = format_agent_event_message(event_main)
            ok2, note2 = send_agent_message(oc_bin, DEFAULT_MAIN_SESSION, msg_main)
            if ok2:
                return {
                    "ok": True,
                    "via": "agent_main_fallback",
                    "session_key": DEFAULT_MAIN_SESSION,
                    "note": f"origin_failed={note}; main={note2}",
                    "attempts": attempts,
                    "delivery_exhausted": False,
                }
            notes.append(f"main:{note2}")

        event_ext = dict(event_attempt)
        event_ext["delivery_route"] = "external_broadcast"
        notif_text = format_external_notification(event_ext)
        notify_result = notify_with_result(emergency_notif, full_config, oc_bin, notif_text)
        if notify_result.get("ok"):
            sent = ",".join(notify_result.get("succeeded", []))
            return {
                "ok": True,
                "via": "external_fallback",
                "session_key": "",
                "note": f"sent={sent or '-'}",
                "attempts": attempts,
                "delivery_exhausted": False,
            }
        attempted = ",".join(notify_result.get("attempted", [])) or "-"
        notes.append(f"external:attempted={attempted}")

        if now_fn() >= deadline:
            break
        sleep_fn(max(0.2, int(retry_interval_ms) / 1000.0))
        if now_fn() >= deadline:
            break

    return {
        "ok": False,
        "via": "none",
        "session_key": "",
        "note": "; ".join(notes[-4:])[:500],
        "attempts": attempts,
        "delivery_exhausted": True,
    }


def format_agent_event_message(event):
    lines = [
        "[restart_guard.result.v1]",
        f"status: {event.get('status', '')}",
        f"severity: {event.get('severity', '')}",
        f"restart_id: {event.get('restart_id', '')}",
        f"context_file: {event.get('context_file', '')}",
        f"context_snapshot: {event.get('context_snapshot', '')}",
        f"elapsed_ms: {event.get('elapsed_ms', 0)}",
        f"failure_phase: {event.get('failure_phase', '')}",
        f"error_code: {event.get('error_code', '')}",
        f"diagnostics_file: {event.get('diagnostics_file', '')}",
        f"delivery_attempts: {event.get('delivery_attempts', 0)}",
        f"delivery_route: {event.get('delivery_route', 'origin_session')}",
        f"note: {event.get('note', '')}",
    ]
    diag = str(event.get("diagnostics_summary", "") or "").strip()
    if diag:
        lines.append("diagnostics_summary:")
        lines.append(diag[:1200])
    lines.append("action_required:")
    lines.append("1. Read the restart context and saved state.")
    lines.append("2. Reply to the user in this same session with the restart result.")
    return "\n".join(lines)


def format_external_notification(event):
    lines = [
        "[restart-guard]",
        f"event: {event.get('event_type', '')}",
        f"status: {event.get('status', '')}",
        f"severity: {event.get('severity', '')}",
        f"restart_id: {event.get('restart_id', '')}",
        f"error_code: {event.get('error_code', '')}",
        f"failure_phase: {event.get('failure_phase', '')}",
        f"diagnostics_file: {event.get('diagnostics_file', '')}",
        f"delivery_attempts: {event.get('delivery_attempts', 0)}",
        f"elapsed_ms: {event.get('elapsed_ms', 0)}",
        f"note: {event.get('note', '')}",
    ]
    diag = str(event.get("diagnostics_summary", "") or "").strip()
    if diag:
        lines.append("diagnostics:")
        lines.append(diag[:1200])
    return "\n".join(lines)


def send_agent_message(oc_bin, session_key, message):
    if not oc_bin:
        return False, "missing openclaw binary"
    idem = f"restart-guard-{uuid.uuid4().hex}"
    params = {
        "message": message,
        "sessionKey": session_key,
        "idempotencyKey": idem,
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


def build_diagnostics_bundle(oc_bin, diag_commands, failure_phase, error_code, note, health_trace):
    commands = run_diagnostics_commands(oc_bin, diag_commands)
    return {
        "generated_at": iso_now(),
        "failure_phase": failure_phase,
        "error_code": error_code,
        "note": note,
        "health_summary": summarize_health_trace(health_trace),
        "commands": commands,
    }


def run_diagnostics_commands(oc_bin, commands):
    outputs = []
    for cmd in commands:
        record = {
            "command": cmd,
            "returncode": -1,
            "summary": "",
            "output": "",
        }
        try:
            actual = cmd
            if oc_bin and cmd.startswith("openclaw "):
                actual = oc_bin + cmd[8:]
            if contains_shell_metachar(actual):
                raise ValueError("shell metacharacters are not allowed in diagnostics commands")
            exec_args = shlex.split(actual)
            if not exec_args:
                raise ValueError("empty command after parsing")
            result = subprocess.run(
                exec_args,
                shell=False,
                capture_output=True,
                text=True,
                timeout=30,
            )
            output = (result.stdout or "").strip()
            if not output:
                output = (result.stderr or "").strip()
            output = output[:8000]
            first = output.splitlines()[0][:240] if output else ""
            record["returncode"] = int(result.returncode)
            record["summary"] = first or f"rc={result.returncode}"
            record["output"] = output
        except Exception as e:
            record["summary"] = f"error: {e}"
            record["output"] = str(e)
        outputs.append(record)
    return outputs


def summarize_health_trace(trace):
    items = trace if isinstance(trace, list) else []
    if not items:
        return "no health probes recorded"
    downs = 0
    ups = 0
    last = []
    for row in items:
        healthy = bool((row or {}).get("healthy", False))
        if healthy:
            ups += 1
        else:
            downs += 1
        phase = str((row or {}).get("phase", ""))
        at = str((row or {}).get("at", ""))
        streak = int((row or {}).get("streak", 0))
        last.append(f"{at} {phase} healthy={str(healthy).lower()} streak={streak}")
    tail = last[-8:]
    return f"probes={len(items)} up={ups} down={downs}\n" + "\n".join(tail)


def summarize_diagnostics_bundle(bundle, diagnostics_file):
    commands = bundle.get("commands", []) if isinstance(bundle, dict) else []
    doctor = first_command_summary(commands, "doctor")
    logs = first_command_summary(commands, "logs")
    summary = (
        f"error_code={bundle.get('error_code', '')}; "
        f"failure_phase={bundle.get('failure_phase', '')}; "
        f"doctor={doctor}; logs={logs}; "
        f"diagnostics_file={diagnostics_file}"
    )
    return redact_sensitive(summary)[:1400]


def first_command_summary(commands, keyword):
    for item in commands:
        cmd = str((item or {}).get("command", "")).lower()
        if keyword in cmd:
            return str((item or {}).get("summary", "")).strip()[:200] or "n/a"
    return "n/a"


def write_diagnostics_bundle(context_path, restart_id, bundle):
    directory = os.path.dirname(context_path) if context_path else os.getcwd()
    if not directory:
        directory = os.getcwd()
    os.makedirs(directory, exist_ok=True)
    json_path = os.path.join(directory, f"restart-diagnostics-{restart_id}.json")
    md_path = os.path.join(directory, f"restart-diagnostics-{restart_id}.md")
    payload = json.dumps(bundle, ensure_ascii=False, indent=2)
    atomic_write(json_path, payload)
    lines = [
        "# Restart Diagnostics",
        "",
        f"- restart_id: {restart_id}",
        f"- generated_at: {bundle.get('generated_at', '')}",
        f"- failure_phase: {bundle.get('failure_phase', '')}",
        f"- error_code: {bundle.get('error_code', '')}",
        f"- note: {bundle.get('note', '')}",
        "",
        "## Health Summary",
        "",
        str(bundle.get("health_summary", "")).strip(),
        "",
        "## Command Outputs",
        "",
    ]
    for cmd in bundle.get("commands", []):
        command = str((cmd or {}).get("command", "")).strip()
        rc = (cmd or {}).get("returncode", "")
        output = str((cmd or {}).get("output", "")).strip()
        lines.append(f"### `{command}` (rc={rc})")
        lines.append("")
        lines.append("```text")
        lines.append(redact_sensitive(output)[:8000])
        lines.append("```")
        lines.append("")
    atomic_write(md_path, "\n".join(lines).strip() + "\n")
    return md_path


def redact_sensitive(text):
    val = str(text or "")
    val = re.sub(
        r"(?i)(token|api[_-]?key|secret|password)\s*[:=]\s*([A-Za-z0-9_\-\.]{6,})",
        r"\1=[REDACTED]",
        val,
    )
    val = re.sub(r"(?i)bearer\s+[A-Za-z0-9\-\._~\+\/]+=*", "bearer [REDACTED]", val)
    return val


def contains_shell_metachar(cmd):
    text = str(cmd or "")
    return any(token in text for token in SHELL_METACHARS)


def make_probe_callback(trace, phase):
    def _record(healthy, streak=0):
        trace.append(
            {
                "phase": phase,
                "healthy": bool(healthy),
                "streak": int(streak),
                "at": iso_now(),
            }
        )

    return _record


def normalize_channels_value(value):
    if isinstance(value, list):
        return [str(x) for x in value if str(x).strip()]
    if isinstance(value, str):
        v = value.strip()
        if not v:
            return []
        if v.startswith("[") and v.endswith("]"):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return [str(x) for x in parsed if str(x).strip()]
            except Exception:
                pass
        return [x.strip() for x in v.split(",") if x.strip()]
    return []


def normalize_list(value):
    if isinstance(value, list):
        return [str(x) for x in value]
    if isinstance(value, str):
        v = value.strip()
        if not v:
            return []
        if v.startswith("[") and v.endswith("]"):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return [str(x) for x in parsed]
            except Exception:
                pass
        return [v]
    return []


def normalize_notify_mode(raw):
    mode = (raw or "").strip().lower()
    if mode not in {"origin", "selected", "all"}:
        return "origin"
    return mode


def select_runtime_notification(base_notif, notify_mode, channel, target):
    notif = copy.deepcopy(base_notif if isinstance(base_notif, dict) else {})
    if notify_mode == "all":
        return notif
    if notify_mode == "selected":
        return apply_notification_override(notif, channel, target)
    return notif


def build_emergency_notification(runtime_notif, full_config):
    notif = copy.deepcopy(runtime_notif if isinstance(runtime_notif, dict) else {})
    emergency_policy = str((notif.get("emergency_policy", "") or "origin_then_all")).strip().lower()
    if emergency_policy not in {"origin_then_all", "origin-main-all"}:
        emergency_policy = "origin_then_all"
    channels = resolve_external_channels(notif, full_config)
    notif["channels"] = channels
    notif["primary"] = "none"
    notif["emergency_policy"] = emergency_policy
    return notif


def resolve_external_channels(runtime_notif, full_config):
    result = []
    seen = set()

    def add(ch):
        name = str(ch or "").strip().lower()
        if not name or name in {"none", "off", "disabled", "webui"}:
            return
        if name in seen:
            return
        seen.add(name)
        result.append(name)

    notif = full_config.get("notification", {}) if isinstance(full_config, dict) else {}
    for ch in normalize_channels_value(notif.get("channels", [])):
        add(ch)
    add(notif.get("fallback", ""))

    for ch in normalize_channels_value((runtime_notif or {}).get("channels", [])):
        add(ch)

    try:
        sys.path.insert(0, SCRIPT_DIR)
        from discover_channels import discover_channels as _discover

        payload = _discover(full_config)
        for item in payload.get("choices", []):
            if not isinstance(item, dict):
                continue
            if item.get("enabled") is not True:
                continue
            add(item.get("id", ""))
    except Exception:
        pass

    return result


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


def resolve_origin_session_key(explicit, context_path):
    raw = (explicit or "").strip()
    if raw:
        return raw
    frontmatter, _ = parse_markdown_frontmatter(context_path)
    return str((frontmatter or {}).get("origin_session_key", "")).strip()


def merge_context_state(context_path, context_snapshot, updates):
    if context_path:
        update_context_frontmatter(context_path, updates)
    if context_snapshot and os.path.exists(context_snapshot):
        try:
            with open(context_snapshot, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                merge_dict(data, updates or {})
                atomic_write(context_snapshot, json.dumps(data, ensure_ascii=False, indent=2))
        except Exception:
            pass


def merge_dict(dst, src):
    for key, val in (src or {}).items():
        if isinstance(val, dict) and isinstance(dst.get(key), dict):
            merge_dict(dst[key], val)
        else:
            dst[key] = val


def update_context_frontmatter(path, updates):
    current, body = parse_markdown_frontmatter(path)
    state = current.get("state_timestamps", {})
    if not isinstance(state, dict):
        state = {}
    incoming_state = (updates or {}).get("state_timestamps", {})
    if isinstance(incoming_state, dict):
        state.update(incoming_state)
    merged = dict(current)
    merged.update(updates or {})
    merged["state_timestamps"] = state
    write_markdown_frontmatter(path, merged, body)


def acquire_guard_lock(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(f"{os.getpid()} {iso_now()}\n")
        return True
    except FileExistsError:
        return False
    except OSError:
        return False


def expand(p):
    return os.path.expanduser(p) if p else p


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


def iso_now():
    return datetime.now(timezone.utc).astimezone().isoformat()


def log_entry(path, result, note, restart_id=""):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    ts = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S.%f %z")
    rid = restart_id or "-"
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"- {ts} result={result} restart_id={rid} note={note}\n")


def record_state(log_path, restart_id, state, note):
    log_entry(log_path, f"state_{state}", note, restart_id)
    log(f"state={state} restart_id={restart_id} note={note}")


def cleanup_lock(lock_path):
    try:
        os.remove(lock_path)
    except OSError:
        pass


def notify(notif_config, full_config, oc_bin, message):
    sys.path.insert(0, SCRIPT_DIR)
    from notify import notify as _notify

    return _notify(notif_config, full_config, oc_bin, message)


def notify_with_result(notif_config, full_config, oc_bin, message):
    sys.path.insert(0, SCRIPT_DIR)
    from notify import notify_with_result as _notify_with_result

    return _notify_with_result(notif_config, full_config, oc_bin, message)


def load_config(path):
    sys.path.insert(0, SCRIPT_DIR)
    from write_context import load_config as _load

    return _load(path)


def parse_markdown_frontmatter(path):
    sys.path.insert(0, SCRIPT_DIR)
    from write_context import parse_markdown_frontmatter as _parse

    return _parse(path)


def write_markdown_frontmatter(path, frontmatter, body):
    sys.path.insert(0, SCRIPT_DIR)
    from write_context import write_markdown_frontmatter as _write

    _write(path, frontmatter, body)


def atomic_write(path, content):
    sys.path.insert(0, SCRIPT_DIR)
    from write_context import atomic_write as _atomic

    _atomic(path, content)


def log(msg):
    ts = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S.%f %z")
    print(f"[guardian {ts}] {msg}", flush=True)


if __name__ == "__main__":
    main()
