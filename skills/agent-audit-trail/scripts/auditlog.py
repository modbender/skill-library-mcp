#!/usr/bin/env python3
"""Append/verify tamper-evident audit log entries.

A hash-chained, append-only audit log for AI agents.

Features:
- NDJSON format (one JSON object per line)
- SHA-256 hash chaining for tamper detection
- Monotonic ordering tokens for sequencing
- File locking for safe concurrent access
- Zero external dependencies (Python 3.9+ stdlib only)

Hash model:
- prev = previous entry's chain.hash (or '0'*64 for first entry)
- line_c14n = JSON.stringify(entry without chain, separators=(',',':'))
- chain.hash = sha256(prev + "\\n" + line_c14n)

Usage:
  ./auditlog.py append --kind <type> --summary <description> [options]
  ./auditlog.py verify [--log <path>]

See SKILL.md for full documentation.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import fcntl
import hashlib
import json
import os
import sys
from typing import Any, Dict, Tuple

try:
    from zoneinfo import ZoneInfo
except ImportError:
    ZoneInfo = None  # type: ignore

# Defaults — override with --log or environment
DEFAULT_LOG = os.environ.get("AUDIT_LOG_PATH", os.path.join("audit", "agent-actions.ndjson"))
DEFAULT_TZ = os.environ.get("AUDIT_LOG_TZ", "UTC")
DEFAULT_ACTOR = os.environ.get("AUDIT_LOG_ACTOR", "agent")
CHAIN_ALGO = "sha256(prev\\nline_c14n)"


def _now_iso(tz_name: str = DEFAULT_TZ) -> str:
    """Return current time as ISO-8601 with timezone offset."""
    if ZoneInfo is None:
        # Fallback for Python < 3.9: UTC only
        return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")
    return _dt.datetime.now(tz=ZoneInfo(tz_name)).isoformat(timespec="seconds")


def _sha256_hex(data: bytes) -> str:
    """Return hex-encoded SHA-256 hash."""
    return hashlib.sha256(data).hexdigest()


def _c14n(obj: Dict[str, Any]) -> str:
    """Canonicalize dict to JSON (deterministic, compact)."""
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=False, sort_keys=True)


def _get_prev_hash_and_last_ord(raw_lines: list[bytes]) -> Tuple[str, int]:
    """Extract previous hash and last ord from existing log lines."""
    if not raw_lines:
        return ("0" * 64, 0)

    prev_hash = None
    last_ord = 0

    for raw in reversed(raw_lines):
        try:
            obj = json.loads(raw.decode("utf-8"))
        except Exception:
            continue
        if not isinstance(obj, dict):
            continue

        # Get prev_hash from last chained entry
        if prev_hash is None:
            ch = obj.get("chain")
            if isinstance(ch, dict) and isinstance(ch.get("hash"), str):
                prev_hash = ch["hash"]

        # Get last ord
        if last_ord == 0 and isinstance(obj.get("ord"), int):
            last_ord = obj["ord"]

        if prev_hash is not None and last_ord != 0:
            break

    # Bootstrap: if no chain found, hash the last line raw
    if prev_hash is None and raw_lines:
        prev_hash = _sha256_hex(raw_lines[-1])

    return (prev_hash or "0" * 64, last_ord)


def append_entry(
    path: str,
    entry: Dict[str, Any],
    *,
    actor: str = DEFAULT_ACTOR,
    tz: str = DEFAULT_TZ,
) -> Dict[str, Any]:
    """Append a new chained entry to the audit log.
    
    Takes an exclusive lock to ensure safe concurrent access.
    Returns the written entry (with chain data).
    """
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

    with open(path, "a+", encoding="utf-8") as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            # Read existing entries under lock
            f.seek(0)
            raw_lines = f.read().encode("utf-8").splitlines()
            prev_hash, last_ord = _get_prev_hash_and_last_ord(raw_lines)

            # Build entry
            obj = dict(entry)
            obj.setdefault("ts", _now_iso(tz))
            obj.setdefault("actor", actor)
            obj.setdefault("plane", "action")
            obj["ord"] = last_ord + 1

            # Compute hash (over entry without chain field)
            obj_for_hash = {k: v for k, v in obj.items() if k != "chain"}
            line_c14n = _c14n(obj_for_hash)
            new_hash = _sha256_hex((prev_hash + "\n" + line_c14n).encode("utf-8"))

            obj["chain"] = {"prev": prev_hash, "hash": new_hash, "algo": CHAIN_ALGO}

            # Append
            f.seek(0, os.SEEK_END)
            f.write(_c14n(obj) + "\n")
            f.flush()
            os.fsync(f.fileno())
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)

    return obj


def verify(path: str, verbose: bool = False) -> Tuple[bool, str]:
    """Verify the hash chain integrity.
    
    Returns (success, message).
    """
    if not os.path.exists(path):
        return (False, f"File not found: {path}")

    with open(path, "rb") as f:
        raw_lines = f.read().splitlines()

    if not raw_lines:
        return (True, "Empty log (nothing to verify)")

    # Find first chained entry
    start_idx = None
    for i, raw in enumerate(raw_lines):
        try:
            obj = json.loads(raw.decode("utf-8"))
            ch = obj.get("chain") if isinstance(obj, dict) else None
            if isinstance(ch, dict) and "prev" in ch and "hash" in ch:
                start_idx = i
                break
        except Exception:
            continue

    if start_idx is None:
        return (True, "No chained entries found (legacy log)")

    prev = None
    last_ord = None
    verified = 0

    for i in range(start_idx, len(raw_lines)):
        raw = raw_lines[i]
        line_num = i + 1

        try:
            obj = json.loads(raw.decode("utf-8"))
        except Exception as e:
            return (False, f"Line {line_num}: Invalid JSON - {e}")

        if not isinstance(obj, dict):
            return (False, f"Line {line_num}: Not a JSON object")

        ch = obj.get("chain")
        if not isinstance(ch, dict):
            return (False, f"Line {line_num}: Missing or invalid chain")

        # Initialize prev from first entry's declared prev
        if prev is None:
            prev = ch.get("prev")

        # Check monotonic ord
        ordv = obj.get("ord")
        if isinstance(ordv, int):
            if last_ord is not None and ordv != last_ord + 1:
                return (False, f"Line {line_num}: ord not monotonic (got {ordv}, expected {last_ord + 1})")
            last_ord = ordv

        # Verify hash
        obj_for_hash = {k: v for k, v in obj.items() if k != "chain"}
        line_c14n = _c14n(obj_for_hash)
        expected = _sha256_hex((prev + "\n" + line_c14n).encode("utf-8"))

        if expected != ch.get("hash"):
            return (False, f"Line {line_num}: Hash mismatch\n  Expected: {expected}\n  Got:      {ch.get('hash')}")

        prev = ch.get("hash")
        verified += 1

    return (True, f"OK ({verified} entries verified)")


def _parse_json_arg(s: str | None) -> Any:
    """Parse a JSON string argument, or return None."""
    if s is None:
        return None
    try:
        return json.loads(s)
    except json.JSONDecodeError as e:
        raise SystemExit(f"Invalid JSON argument: {e}\nInput: {s}")


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="auditlog",
        description="Tamper-evident audit logging for AI agents",
    )
    parser.add_argument(
        "--log",
        default=DEFAULT_LOG,
        help=f"Audit log path (default: {DEFAULT_LOG}, or AUDIT_LOG_PATH env)",
    )
    parser.add_argument(
        "--actor",
        default=DEFAULT_ACTOR,
        help=f"Actor name (default: {DEFAULT_ACTOR}, or AUDIT_LOG_ACTOR env)",
    )
    parser.add_argument(
        "--tz",
        default=DEFAULT_TZ,
        help=f"Timezone for timestamps (default: {DEFAULT_TZ}, or AUDIT_LOG_TZ env)",
    )

    sub = parser.add_subparsers(dest="cmd", required=True)

    # append subcommand
    ap = sub.add_parser("append", help="Append a new audit log entry")
    ap.add_argument("--kind", required=True, help="Event type (e.g., file-write, exec, api-call)")
    ap.add_argument("--summary", required=True, help="Human-readable description")
    ap.add_argument("--domain", default="unknown", help="Logical domain")
    ap.add_argument("--target", help="What was acted upon (file, URL, command)")
    ap.add_argument("--gate", help="Gate reference for approved actions")
    ap.add_argument("--provenance", help="JSON object with source attribution")
    ap.add_argument("--details", help="JSON object with additional data")

    # verify subcommand
    vp = sub.add_parser("verify", help="Verify audit log integrity")
    vp.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.cmd == "append":
        entry: Dict[str, Any] = {
            "kind": args.kind,
            "summary": args.summary,
            "domain": args.domain,
        }
        if args.target:
            entry["target"] = args.target
        if args.gate:
            entry["gate"] = args.gate
        if args.provenance:
            entry["provenance"] = _parse_json_arg(args.provenance)
        if args.details:
            entry["details"] = _parse_json_arg(args.details)

        result = append_entry(args.log, entry, actor=args.actor, tz=args.tz)
        print(_c14n(result))
        return 0

    if args.cmd == "verify":
        success, message = verify(args.log, verbose=args.verbose)
        print(message)
        return 0 if success else 1

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
