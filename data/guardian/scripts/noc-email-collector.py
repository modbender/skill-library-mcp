#!/usr/bin/env python3
"""Guardian email collector with cumulative scanned/flagged metrics (BL-042)."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

SKILL_ROOT = Path(__file__).resolve().parents[1]
if str(SKILL_ROOT) not in sys.path:
    sys.path.insert(0, str(SKILL_ROOT))

from core.guardian_db import GuardianDB

WORKSPACE = Path(os.environ.get("GUARDIAN_WORKSPACE") or SKILL_ROOT.parents[1]).resolve()
WORKSPACE_DASHBOARD_DIR = WORKSPACE / "dashboard"
LOCAL_DASHBOARD_DIR = SKILL_ROOT / "dashboard"
GUARDIAN_DEFS = SKILL_ROOT / "definitions"


def resolve_dashboard_dir() -> Path:
    candidates = [WORKSPACE_DASHBOARD_DIR, LOCAL_DASHBOARD_DIR]
    for cand in candidates:
        try:
            cand.mkdir(parents=True, exist_ok=True)
            probe = cand / ".guardian-write-probe"
            probe.write_text("ok", encoding="utf-8")
            probe.unlink(missing_ok=True)
            return cand
        except OSError:
            continue
    return LOCAL_DASHBOARD_DIR


DASHBOARD_DIR = resolve_dashboard_dir()
OUT = DASHBOARD_DIR / "noc-email.json"
STATE = DASHBOARD_DIR / "noc-email-state.json"


def _load_json(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def load_email_patterns() -> List[Dict[str, Any]]:
    sigs: List[Dict[str, Any]] = []
    for fname in ("injection-sigs.json", "exfil-patterns.json", "social-engineering.json"):
        fpath = GUARDIAN_DEFS / fname
        if not fpath.exists():
            continue
        try:
            data = json.loads(fpath.read_text(encoding="utf-8"))
            items = data if isinstance(data, list) else data.get("signatures", data.get("patterns", []))
            sigs.extend(items)
        except Exception:
            continue

    compiled: List[Dict[str, Any]] = []
    for sig in sigs:
        det = sig.get("detection", {}) if isinstance(sig.get("detection", {}), dict) else {}
        pats = det.get("patterns", [])
        if not pats and isinstance(sig.get("patterns"), list):
            pats = sig["patterns"]
        if not pats and sig.get("pattern"):
            pats = [sig["pattern"]]

        sid = str(sig.get("id", ""))
        cat = sig.get("category") or "unknown"
        if cat == "unknown":
            if sid.startswith("INJ"):
                cat = "prompt_injection"
            elif sid.startswith("EXF"):
                cat = "data_exfiltration"
            elif sid.startswith("SE"):
                cat = "social_engineering"

        for pat in pats:
            try:
                compiled.append(
                    {
                        "regex": re.compile(pat, re.IGNORECASE),
                        "id": sid or "?",
                        "severity": sig.get("severity", "low"),
                        "category": cat,
                        "description": sig.get("description", ""),
                        "score": int(sig.get("score", 50)),
                    }
                )
            except re.error:
                continue
    return compiled


def scan_email(text: str, patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not text:
        return []
    hits: List[Dict[str, Any]] = []
    for p in patterns:
        m = p["regex"].search(text)
        if not m:
            continue
        hits.append(
            {
                "id": p["id"],
                "category": p["category"],
                "severity": p["severity"],
                "score": p["score"],
                "evidence": m.group(0)[:80],
                "description": p["description"],
            }
        )
    return hits


def _normalize_messages(source: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows = source.get("recentUnread") or []
    if not isinstance(rows, list):
        return []
    out: List[Dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        mid = str(row.get("id", "")).strip() or hashlib.sha256(
            f"{row.get('from','')}|{row.get('subject','')}|{row.get('snippet','')}".encode("utf-8", errors="replace")
        ).hexdigest()[:24]
        out.append(
            {
                "id": mid,
                "from": str(row.get("from", "")),
                "subject": str(row.get("subject", "")),
                "date": str(row.get("date", "")),
                "snippet": str(row.get("snippet", ""))[:240],
                "labels": row.get("labels", []),
            }
        )
    return out


def run(input_json: Path | None = None) -> Dict[str, Any]:
    DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)

    prev_out = _load_json(OUT)
    state = _load_json(STATE)
    seen_ids = set(state.get("seen_ids", []))

    source = _load_json(input_json) if input_json else prev_out
    messages = _normalize_messages(source)

    patterns = load_email_patterns()
    db_path = (Path(os.environ.get("GUARDIAN_DB_PATH", "")) if os.environ.get("GUARDIAN_DB_PATH") else (SKILL_ROOT / "guardian.db")).resolve()
    db = GuardianDB(db_path=str(db_path))

    scanned_run = 0
    flagged_run = 0
    email_threats: List[Dict[str, Any]] = []

    try:
        for msg in messages:
            msg_id = msg["id"]
            if msg_id in seen_ids:
                continue
            seen_ids.add(msg_id)
            scanned_run += 1

            scan_text = f"{msg.get('from','')} {msg.get('subject','')} {msg.get('snippet','')}"
            hits = scan_email(scan_text, patterns)
            if not hits:
                continue

            flagged_run += 1
            best = max(hits, key=lambda h: h["score"])
            blocked = int(best["score"]) >= 80
            msg["guardian_flag"] = {
                "score": best["score"],
                "category": best["category"],
                "severity": best["severity"],
                "blocked": blocked,
            }
            email_threats.append(
                {
                    "email_id": msg_id,
                    "from": msg.get("from", ""),
                    "subject": msg.get("subject", ""),
                    "category": best["category"],
                    "severity": best["severity"],
                    "score": best["score"],
                    "evidence": best["evidence"],
                    "blocked": blocked,
                }
            )

            msg_hash = hashlib.sha256(scan_text.encode("utf-8", errors="replace")).hexdigest()
            db.add_threat(
                sig_id=best["id"],
                category=best["category"],
                severity=best["severity"],
                score=best["score"],
                evidence=best["evidence"],
                description=best["description"],
                blocked=blocked,
                channel="email",
                source_file=f"email:{msg_id}",
                message_hash=msg_hash,
            )

        if scanned_run > 0:
            db.record_scan(
                scanned_run,
                1,
                scanned_run - flagged_run,
                flagged_run,
                sum(1 for t in email_threats if t.get("blocked")),
                {},
                max(0, 100 - min(100, flagged_run * 10)),
            )
    finally:
        db.close()

    prev_guardian = prev_out.get("guardian", {}) if isinstance(prev_out.get("guardian"), dict) else {}
    cumulative_scanned = int(prev_guardian.get("cumulative_scanned") or prev_out.get("cumulative_scanned") or 0) + scanned_run
    cumulative_flagged = int(prev_guardian.get("cumulative_flagged") or prev_out.get("cumulative_flagged") or 0) + flagged_run

    out = {
        "generatedAt": datetime.now(timezone.utc).astimezone().isoformat(),
        "account": str(source.get("account", "unknown")),
        "unreadCount": int(source.get("unreadCount", len(messages))),
        "allUnread": int(source.get("allUnread", source.get("unreadCount", len(messages)))),
        "todayCount": int(source.get("todayCount", 0)),
        "recentUnread": messages,
        "cumulative_scanned": cumulative_scanned,
        "cumulative_flagged": cumulative_flagged,
        "guardian": {
            "scanned": scanned_run,
            "flagged": flagged_run,
            "threats": email_threats,
            "cumulative_scanned": cumulative_scanned,
            "cumulative_flagged": cumulative_flagged,
        },
    }

    OUT.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    STATE.write_text(json.dumps({"seen_ids": sorted(seen_ids)}, indent=2) + "\n", encoding="utf-8")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Guardian NOC email collector")
    parser.add_argument("--input", type=str, help="Optional JSON file containing recentUnread payload")
    args = parser.parse_args()
    src = Path(args.input).expanduser().resolve() if args.input else None
    data = run(input_json=src)
    g = data.get("guardian", {})
    print(
        f"Email collector: scanned={g.get('scanned', 0)} flagged={g.get('flagged', 0)} "
        f"cumulative_scanned={g.get('cumulative_scanned', 0)} cumulative_flagged={g.get('cumulative_flagged', 0)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
