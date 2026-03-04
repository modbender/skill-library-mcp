#!/usr/bin/env python3
"""codeflow-guard.py

Session-scoped guard state for Codeflow runs.

Implements:
- activate: mark guard active for current context
- deactivate: disable guard
- status: print current guard state
- check: validate current run against active guard

State is stored in JSON and audit records are appended as JSONL.
"""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import re
import sys
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
from py_compat import require_python310

require_python310(prog="codeflow-guard")

from redaction import redact_text


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def norm(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()

_COMMAND_HINT_LIMIT = 200


def command_hint(command: Any) -> str:
    text = norm(command)
    if not text:
        return ""
    text = redact_text(text, strict=True)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= _COMMAND_HINT_LIMIT:
        return text
    return text[: max(0, _COMMAND_HINT_LIMIT - 1)] + "…"


def load_json(path: Path) -> Dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return {}

@contextmanager
def file_lock(path: Path):
    """Process-level lock for a path (uses a sibling .lock file)."""
    lock_path = Path(str(path) + ".lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(lock_path), os.O_CREAT | os.O_RDWR, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        try:
            os.close(fd)
        except Exception:
            pass


def write_json_atomic(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f"{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
            f.flush()
            try:
                os.fsync(f.fileno())
            except Exception:
                pass
        os.replace(tmp, path)
        try:
            os.chmod(path, 0o600)
        except Exception:
            pass
        try:
            dfd = os.open(str(path.parent), os.O_DIRECTORY)
            try:
                os.fsync(dfd)
            finally:
                os.close(dfd)
        except Exception:
            pass
    finally:
        try:
            if os.path.exists(tmp):
                os.unlink(tmp)
        except Exception:
            pass


def append_audit(path: Path, event: str, result: str, payload: Dict[str, Any]) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        rec = {"ts": now_iso(), "event": event, "result": result}
        rec.update(payload)
        with file_lock(path):
            with path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception:
        # Audit must never break the main flow.
        pass


def current_context(args: argparse.Namespace) -> Dict[str, str]:
    return {
        "sessionKey": norm(args.session_key),
        "platform": norm(args.platform),
        "chatId": norm(args.chat_id),
        "threadId": norm(args.thread_id),
        "workdir": norm(args.workdir),
        "agent": norm(args.agent),
        "commandHint": command_hint(args.command),
    }

def binding_key(platform: str, chat_id: str, thread_id: str, session_key: str) -> str:
    """Build a stable binding key for the current context.

    Priority:
    1) chat/thread (Telegram topics/forums)
    2) session key (Discord / non-chat contexts)
    3) global fallback
    """
    p = norm(platform).lower() or "unknown"
    chat = norm(chat_id)
    thread = norm(thread_id)
    sess = norm(session_key)

    if chat:
        # Normalize "no topic" as a stable sentinel to support chat-only bindings.
        t = thread if thread else "none"
        return f"{p}:chat:{chat}:thread:{t}"
    if sess:
        return f"{p}:session:{sess}"
    return f"{p}:global"


def _load_bindings(state: Dict[str, Any]) -> Dict[str, Any]:
    bindings = state.get("bindings")
    if isinstance(bindings, dict):
        return bindings

    # Fallback for state files that store a single binding at state["guard"].
    guard = state.get("guard")
    if isinstance(guard, dict) and guard:
        key = binding_key(
            platform=norm(guard.get("platform")),
            chat_id=norm(guard.get("chatId")),
            thread_id=norm(guard.get("threadId")),
            session_key=norm(guard.get("sessionKey")),
        )
        return {key: guard}

    return {}


def cmd_activate(args: argparse.Namespace) -> int:
    state_path = Path(args.state).expanduser()
    audit_path = Path(args.audit).expanduser()

    ctx = current_context(args)
    key = binding_key(ctx["platform"], ctx["chatId"], ctx["threadId"], ctx["sessionKey"])

    guard = {
        "active": True,
        "activatedAt": now_iso(),
        "sessionKey": ctx["sessionKey"],
        "platform": ctx["platform"],
        "chatId": ctx["chatId"],
        "threadId": ctx["threadId"],
        "workdir": ctx["workdir"],
        "agent": ctx["agent"],
        "commandHint": ctx["commandHint"],
    }

    with file_lock(state_path):
        state = load_json(state_path)
        bindings = _load_bindings(state)
        bindings[key] = guard
        state["bindings"] = bindings
        # Convenience field: last activated binding.
        state["guard"] = guard
        state["updatedAt"] = now_iso()
        write_json_atomic(state_path, state)

    append_audit(
        audit_path,
        "activate",
        "ok",
        {
            "bindingKey": key,
            "sessionKey": ctx["sessionKey"],
            "platform": ctx["platform"],
            "chatId": ctx["chatId"],
            "threadId": ctx["threadId"],
            "workdir": ctx["workdir"],
            "agent": ctx["agent"],
        },
    )

    print("GUARD_ACTIVE")
    return 0


def cmd_deactivate(args: argparse.Namespace) -> int:
    state_path = Path(args.state).expanduser()
    audit_path = Path(args.audit).expanduser()

    ctx = current_context(args)
    key = binding_key(ctx["platform"], ctx["chatId"], ctx["threadId"], ctx["sessionKey"])
    with file_lock(state_path):
        state = load_json(state_path)
        bindings = _load_bindings(state)

        guard = bindings.get(key) if isinstance(bindings.get(key), dict) else {}
        guard = dict(guard)  # don't mutate shared refs from _load_bindings()
        guard["active"] = False
        guard["deactivatedAt"] = now_iso()
        guard["commandHint"] = ctx["commandHint"]
        guard.pop("lastCommand", None)
        guard.pop("command", None)
        # Preserve binding fields when possible; ensure platform/chat/thread/session are set.
        guard.setdefault("sessionKey", ctx["sessionKey"])
        guard.setdefault("platform", ctx["platform"])
        guard.setdefault("chatId", ctx["chatId"])
        guard.setdefault("threadId", ctx["threadId"])
        bindings[key] = guard
        state["bindings"] = bindings
        state["guard"] = guard  # convenience alias
        state["updatedAt"] = now_iso()
        write_json_atomic(state_path, state)

    append_audit(
        audit_path,
        "deactivate",
        "ok",
        {
            "bindingKey": key,
            "sessionKey": ctx["sessionKey"],
            "platform": ctx["platform"],
            "chatId": ctx["chatId"],
            "threadId": ctx["threadId"],
        },
    )

    print("GUARD_INACTIVE")
    return 0


def _check_binding(guard: Dict[str, Any], ctx: Dict[str, str]) -> str:
    expected_session = norm(guard.get("sessionKey"))
    expected_chat = norm(guard.get("chatId"))
    expected_thread = norm(guard.get("threadId"))

    # Strict session binding when both are present.
    if expected_session and ctx["sessionKey"] and expected_session != ctx["sessionKey"]:
        return f"session_mismatch expected={expected_session} got={ctx['sessionKey']}"

    # Chat/thread binding for Telegram/forum contexts.
    if expected_chat:
        if not ctx["chatId"]:
            return "missing_chat_context"
        if expected_chat != ctx["chatId"]:
            return f"chat_mismatch expected={expected_chat} got={ctx['chatId']}"

    if expected_thread:
        if not ctx["threadId"]:
            return "missing_thread_context"
        if expected_thread != ctx["threadId"]:
            return f"thread_mismatch expected={expected_thread} got={ctx['threadId']}"

    return ""


def cmd_check(args: argparse.Namespace) -> int:
    state_path = Path(args.state).expanduser()
    audit_path = Path(args.audit).expanduser()

    state = load_json(state_path)
    ctx = current_context(args)
    key = binding_key(ctx["platform"], ctx["chatId"], ctx["threadId"], ctx["sessionKey"])
    bindings = _load_bindings(state)
    guard = bindings.get(key) if isinstance(bindings.get(key), dict) else {}

    if not guard:
        reason = "no_binding"
        append_audit(
            audit_path,
            "check",
            "deny",
            {
                "reason": reason,
                "bindingKey": key,
                "sessionKey": ctx["sessionKey"],
                "platform": ctx["platform"],
                "chatId": ctx["chatId"],
                "threadId": ctx["threadId"],
                "workdir": ctx["workdir"],
                "agent": ctx["agent"],
                "commandHint": ctx["commandHint"],
                "knownBindings": sorted(bindings.keys())[:50],
            },
        )
        print("GUARD_BLOCKED: no binding for this chat/topic. Re-run /codeflow here to activate.", file=sys.stderr)
        return 2

    if not bool(guard.get("active")):
        reason = "binding_inactive"
        append_audit(
            audit_path,
            "check",
            "deny",
            {
                "reason": reason,
                "bindingKey": key,
                "sessionKey": ctx["sessionKey"],
                "platform": ctx["platform"],
                "chatId": ctx["chatId"],
                "threadId": ctx["threadId"],
                "workdir": ctx["workdir"],
                "agent": ctx["agent"],
                "commandHint": ctx["commandHint"],
            },
        )
        print("GUARD_BLOCKED: binding inactive. Re-run /codeflow in this chat/topic to activate.", file=sys.stderr)
        return 2

    binding_err = _check_binding(guard, ctx)
    if binding_err:
        append_audit(
            audit_path,
            "check",
            "deny",
            {
                "reason": binding_err,
                "bindingKey": key,
                "sessionKey": ctx["sessionKey"],
                "platform": ctx["platform"],
                "chatId": ctx["chatId"],
                "threadId": ctx["threadId"],
                "workdir": ctx["workdir"],
                "agent": ctx["agent"],
                "commandHint": ctx["commandHint"],
                "guardSessionKey": norm(guard.get("sessionKey")),
                "guardChatId": norm(guard.get("chatId")),
                "guardThreadId": norm(guard.get("threadId")),
            },
        )
        print(f"GUARD_BLOCKED: {binding_err}. Re-run /codeflow in this chat/topic.", file=sys.stderr)
        return 2

    warnings = []
    expected_workdir = norm(guard.get("workdir"))
    if expected_workdir and ctx["workdir"] and expected_workdir != ctx["workdir"]:
        warnings.append(f"workdir_changed:{expected_workdir}->{ctx['workdir']}")

    append_audit(
        audit_path,
        "check",
        "allow",
        {
            "bindingKey": key,
            "sessionKey": ctx["sessionKey"],
            "platform": ctx["platform"],
            "chatId": ctx["chatId"],
            "threadId": ctx["threadId"],
            "workdir": ctx["workdir"],
            "agent": ctx["agent"],
            "commandHint": ctx["commandHint"],
            "warnings": warnings,
        },
    )

    print("GUARD_OK")
    if warnings:
        print("GUARD_WARN: " + ",".join(warnings), file=sys.stderr)
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    state_path = Path(args.state).expanduser()
    state = load_json(state_path)
    bindings = _load_bindings(state)
    guard = state.get("guard") if isinstance(state.get("guard"), dict) else {}

    summaries = []
    for k in sorted(bindings.keys()):
        b = bindings.get(k) if isinstance(bindings.get(k), dict) else {}
        summaries.append(
            {
                "key": k,
                "active": bool(b.get("active")),
                "platform": norm(b.get("platform")),
                "chatId": norm(b.get("chatId")),
                "threadId": norm(b.get("threadId")),
                "sessionKey": norm(b.get("sessionKey")),
                "workdir": norm(b.get("workdir")),
                "activatedAt": norm(b.get("activatedAt")),
                "deactivatedAt": norm(b.get("deactivatedAt")),
            }
        )

    any_active = any(bool((bindings.get(k) or {}).get("active")) for k in bindings.keys() if isinstance(bindings.get(k), dict))
    out = {
        "stateFile": str(state_path),
        "active": any_active,
        "guard": guard,
        "bindings": summaries,
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


def add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--state", required=True, help="Guard state JSON file")
    parser.add_argument("--audit", required=True, help="Audit log JSONL file")
    parser.add_argument("--session-key", default="", help="Current OpenClaw session key")
    parser.add_argument("--platform", default="", help="Current platform")
    parser.add_argument("--chat-id", default="", help="Current chat id")
    parser.add_argument("--thread-id", default="", help="Current thread/topic id")
    parser.add_argument("--workdir", default="", help="Current workdir")
    parser.add_argument("--agent", default="", help="Agent display name")
    parser.add_argument("--command", default="", help="Command string")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Codeflow guard state manager")
    sub = parser.add_subparsers(dest="action", required=True)

    p_activate = sub.add_parser("activate", help="Activate guard")
    add_common_args(p_activate)

    p_deactivate = sub.add_parser("deactivate", help="Deactivate guard")
    add_common_args(p_deactivate)

    p_check = sub.add_parser("check", help="Check guard for current run")
    add_common_args(p_check)

    p_status = sub.add_parser("status", help="Show guard status")
    add_common_args(p_status)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.action == "activate":
        return cmd_activate(args)
    if args.action == "deactivate":
        return cmd_deactivate(args)
    if args.action == "check":
        return cmd_check(args)
    if args.action == "status":
        return cmd_status(args)

    parser.error(f"unknown action: {args.action}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
