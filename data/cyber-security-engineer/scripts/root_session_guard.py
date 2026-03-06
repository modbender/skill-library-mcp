#!/usr/bin/env python3
"""Root session guard with idle-timeout and allowlisted argv scoping.
Review before use. No network calls are made from this script.
"""
import argparse
import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional


DEFAULT_TIMEOUT_MINUTES = 30
STATE_PATH = Path.home() / ".openclaw" / "security" / "root-session-state.json"


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def to_iso(ts: datetime) -> str:
    return ts.isoformat().replace("+00:00", "Z")


def from_iso(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    return datetime.fromisoformat(value)


@dataclass
class AllowedCommand:
    argv: List[str]
    added_at_utc: str


@dataclass
class SessionState:
    privilege_mode: str
    last_elevated_activity_utc: Optional[str]
    last_normal_activity_utc: Optional[str]
    last_transition_utc: str
    last_action: str
    # When in elevated mode, restrict which privileged commands are allowed to run.
    allowed_commands: List[AllowedCommand] = field(default_factory=list)
    approved_reason: Optional[str] = None
    approved_session_id: Optional[str] = None

    def as_dict(self) -> Dict[str, Optional[str]]:
        return {
            "privilege_mode": self.privilege_mode,
            "last_elevated_activity_utc": self.last_elevated_activity_utc,
            "last_normal_activity_utc": self.last_normal_activity_utc,
            "last_transition_utc": self.last_transition_utc,
            "last_action": self.last_action,
            "approved_reason": self.approved_reason,
            "approved_session_id": self.approved_session_id,
            "allowed_commands": [
                {"argv": e.argv, "added_at_utc": e.added_at_utc}
                for e in self.allowed_commands
            ],
        }


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def default_state() -> SessionState:
    ts = to_iso(now_utc())
    return SessionState(
        privilege_mode="normal",
        last_elevated_activity_utc=None,
        last_normal_activity_utc=ts,
        last_transition_utc=ts,
        last_action="init-normal",
        allowed_commands=[],
        approved_reason=None,
        approved_session_id=None,
    )


def load_state(path: Path) -> SessionState:
    if not path.exists():
        state = default_state()
        save_state(path, state)
        return state
    with path.open("r", encoding="utf-8") as f:
        raw = json.load(f)
    allowed_raw = raw.get("allowed_commands") or []
    allowed: List[AllowedCommand] = []
    if isinstance(allowed_raw, list):
        for entry in allowed_raw:
            if not isinstance(entry, dict):
                continue
            argv = entry.get("argv")
            added_at_utc = entry.get("added_at_utc")
            if isinstance(argv, list) and all(isinstance(x, str) for x in argv) and isinstance(
                added_at_utc, str
            ):
                allowed.append(AllowedCommand(argv=argv, added_at_utc=added_at_utc))
    return SessionState(
        privilege_mode=raw.get("privilege_mode", "normal"),
        last_elevated_activity_utc=raw.get("last_elevated_activity_utc"),
        last_normal_activity_utc=raw.get("last_normal_activity_utc"),
        last_transition_utc=raw.get("last_transition_utc", to_iso(now_utc())),
        last_action=raw.get("last_action", "unknown"),
        allowed_commands=allowed,
        approved_reason=raw.get("approved_reason"),
        approved_session_id=raw.get("approved_session_id"),
    )


def save_state(path: Path, state: SessionState) -> None:
    ensure_parent(path)
    with path.open("w", encoding="utf-8") as f:
        json.dump(state.as_dict(), f, indent=2)
        f.write("\n")


def minutes_since(ts_iso: Optional[str]) -> Optional[float]:
    ts = from_iso(ts_iso)
    if ts is None:
        return None
    delta = now_utc() - ts
    return round(delta.total_seconds() / 60.0, 2)


def preflight(state: SessionState, timeout_minutes: int) -> int:
    idle_mins = minutes_since(state.last_elevated_activity_utc)
    timed_out = (
        state.privilege_mode == "elevated"
        and idle_mins is not None
        and idle_mins >= timeout_minutes
    )

    action = "continue-normal"
    approval_required = True
    if state.privilege_mode == "elevated" and not timed_out:
        action = "elevated-active"
        # Approval is still required per-command unless the command is already allowlisted.
        approval_required = False
    elif timed_out:
        action = "drop-elevation"
        state.privilege_mode = "normal"
        state.allowed_commands = []
        state.approved_reason = None
        state.approved_session_id = None
        state.last_transition_utc = to_iso(now_utc())
        state.last_action = "timeout-drop"

    result = {
        "status": "REQUIRES_APPROVAL" if approval_required else "ELEVATED_AVAILABLE",
        "privilege_mode": state.privilege_mode,
        "idle_minutes_since_elevated": idle_mins,
        "timeout_minutes": timeout_minutes,
        "action": action,
        "allowed_commands_count": len(state.allowed_commands),
    }
    print(json.dumps(result, indent=2))
    return 2 if approval_required else 0


def is_allowed(state: SessionState, argv: List[str]) -> bool:
    if not argv:
        return False
    for entry in state.allowed_commands:
        if entry.argv == argv:
            return True
    return False


def authorize(state: SessionState, timeout_minutes: int, argv: List[str], session_id: Optional[str]) -> int:
    idle_mins = minutes_since(state.last_elevated_activity_utc)
    timed_out = (
        state.privilege_mode == "elevated"
        and idle_mins is not None
        and idle_mins >= timeout_minutes
    )
    if timed_out:
        state.privilege_mode = "normal"
        state.allowed_commands = []
        state.approved_reason = None
        state.approved_session_id = None
        state.last_transition_utc = to_iso(now_utc())
        state.last_action = "timeout-drop"

    session_ok = session_id is None or state.approved_session_id in (None, session_id)
    allowed = state.privilege_mode == "elevated" and is_allowed(state, argv) and session_ok
    approval_required = not allowed

    result = {
        "status": "REQUIRES_APPROVAL" if approval_required else "AUTHORIZED",
        "privilege_mode": state.privilege_mode,
        "idle_minutes_since_elevated": idle_mins,
        "timeout_minutes": timeout_minutes,
        "allowed": allowed,
        "allowed_commands_count": len(state.allowed_commands),
        "session_id": session_id,
        "session_ok": session_ok,
    }
    print(json.dumps(result, indent=2))
    return 2 if approval_required else 0


def approve_command(state: SessionState, reason: str, argv: List[str], session_id: Optional[str]) -> None:
    ts = to_iso(now_utc())
    state.privilege_mode = "elevated"
    state.last_elevated_activity_utc = ts
    state.last_transition_utc = ts
    state.last_action = "approved-command"
    state.approved_reason = reason
    state.approved_session_id = session_id
    if argv and not is_allowed(state, argv):
        state.allowed_commands.append(AllowedCommand(argv=argv, added_at_utc=ts))


def mark_elevated_used(state: SessionState) -> None:
    ts = to_iso(now_utc())
    state.privilege_mode = "elevated"
    state.last_elevated_activity_utc = ts
    state.last_transition_utc = ts
    state.last_action = "elevated-used"


def mark_normal_used(state: SessionState) -> None:
    ts = to_iso(now_utc())
    state.privilege_mode = "normal"
    state.last_normal_activity_utc = ts
    state.last_transition_utc = ts
    state.last_action = "normal-used"


def drop(state: SessionState, reason: str) -> None:
    ts = to_iso(now_utc())
    state.privilege_mode = "normal"
    state.allowed_commands = []
    state.approved_reason = None
    state.approved_session_id = None
    state.last_transition_utc = ts
    state.last_action = reason


def status(state: SessionState, timeout_minutes: int) -> None:
    idle_mins = minutes_since(state.last_elevated_activity_utc)
    timed_out = (
        state.privilege_mode == "elevated"
        and idle_mins is not None
        and idle_mins >= timeout_minutes
    )
    result = state.as_dict()
    result["idle_minutes_since_elevated"] = idle_mins
    result["timeout_minutes"] = timeout_minutes
    result["timed_out"] = timed_out
    result["approval_required"] = state.privilege_mode != "elevated" or timed_out
    print(json.dumps(result, indent=2))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="OpenClaw root/elevated session guard")
    parser.add_argument(
        "--state-file",
        default=str(STATE_PATH),
        help="Path to session state JSON file",
    )
    parser.add_argument(
        "--timeout-minutes",
        type=int,
        default=DEFAULT_TIMEOUT_MINUTES,
        help="Idle timeout for elevated mode",
    )

    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("preflight", help="Check timeout and approval requirement")
    authz = sub.add_parser(
        "authorize",
        help="Authorize a specific argv against the current elevated allowlist",
    )
    authz.add_argument(
        "--argv-json",
        required=True,
        help='Command argv as JSON array, e.g. ["launchctl","print","..."]',
    )
    authz.add_argument("--session-id", help="Task session id to scope approvals")
    approve = sub.add_parser(
        "approve",
        help="Approve a specific argv for elevated execution (adds to allowlist)",
    )
    approve.add_argument("--reason", required=True, help="Approval reason")
    approve.add_argument(
        "--argv-json",
        required=True,
        help='Command argv as JSON array, e.g. ["launchctl","print","..."]',
    )
    approve.add_argument("--session-id", help="Task session id to scope approvals")
    sub.add_parser("elevated-used", help="Mark elevated mode as used now")
    sub.add_parser("normal-used", help="Mark normal mode activity now")
    sub.add_parser("drop", help="Drop to normal mode")
    sub.add_parser("status", help="Print current state and timeout info")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    state_file = Path(os.path.expanduser(args.state_file))
    state = load_state(state_file)

    if args.command == "preflight":
        code = preflight(state, args.timeout_minutes)
        save_state(state_file, state)
        return code
    if args.command == "authorize":
        argv = json.loads(args.argv_json)
        if not isinstance(argv, list) or not all(isinstance(x, str) for x in argv):
            print('{"status":"ERROR","error":"argv-json must be a JSON array of strings"}')
            return 2
        code = authorize(state, args.timeout_minutes, argv, args.session_id)
        save_state(state_file, state)
        return code
    if args.command == "approve":
        argv = json.loads(args.argv_json)
        if not isinstance(argv, list) or not all(isinstance(x, str) for x in argv):
            print('{"status":"ERROR","error":"argv-json must be a JSON array of strings"}')
            return 2
        approve_command(state, args.reason, argv, args.session_id)
        save_state(state_file, state)
        print('{"status":"OK","action":"approved-command"}')
        return 0
    if args.command == "elevated-used":
        mark_elevated_used(state)
        save_state(state_file, state)
        print('{"status":"OK","action":"elevated-used"}')
        return 0
    if args.command == "normal-used":
        mark_normal_used(state)
        save_state(state_file, state)
        print('{"status":"OK","action":"normal-used"}')
        return 0
    if args.command == "drop":
        drop(state, "manual-drop")
        save_state(state_file, state)
        print('{"status":"OK","action":"drop-elevation"}')
        return 0
    if args.command == "status":
        status(state, args.timeout_minutes)
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
