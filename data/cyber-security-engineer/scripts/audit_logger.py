#!/usr/bin/env python3
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


AUDIT_LOG = Path.home() / ".openclaw" / "security" / "privileged-audit.jsonl"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def append_audit(event: Dict[str, Any]) -> None:
    """
    Append an audit event to an on-disk JSONL timeline.

    Best-effort only: audit logging must never block privileged operations.
    """
    try:
        AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
        payload = {"ts_utc": _utc_now_iso(), **event}
        with AUDIT_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, separators=(",", ":")) + "\n")
    except Exception:
        return

