#!/usr/bin/env python3
"""Guardian threats exporter for dashboard/guardian-threats.json.

BL-042 goals:
- channel scanned/flagged metrics are cumulative and stable for telegram/cron/email
- dashboard channel panel uses all-time counts (not per-run only)
"""

from __future__ import annotations

import glob
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

SKILL_ROOT = Path(__file__).resolve().parents[1]
if str(SKILL_ROOT) not in sys.path:
    sys.path.insert(0, str(SKILL_ROOT))

from core.guardian_db import GuardianDB
from core.settings import DEFAULT_CONFIG, load_config

WORKSPACE = Path(os.environ.get("GUARDIAN_WORKSPACE") or SKILL_ROOT.parents[1]).resolve()
WORKSPACE_DASHBOARD_DIR = WORKSPACE / "dashboard"
LOCAL_DASHBOARD_DIR = SKILL_ROOT / "dashboard"
GUARDIAN_DEFS = SKILL_ROOT / "definitions"
CONTEXT_RADIUS = 3

SESSION_DIRS = [
    Path.home() / ".openclaw" / "agents" / "main" / "sessions",
    Path.home() / ".openclaw" / "cron" / "runs",
]


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
OUTPUT = DASHBOARD_DIR / "guardian-threats.json"
CONFIG_OUTPUT = DASHBOARD_DIR / "guardian-config.json"
DAILY_STATE_FILE = DASHBOARD_DIR / "guardian-daily-state.json"


def load_config_safe() -> Dict[str, Any]:
    try:
        cfg = load_config()
        merged = dict(DEFAULT_CONFIG)
        if isinstance(cfg, dict):
            merged.update(cfg)
        return merged
    except Exception:
        return dict(DEFAULT_CONFIG)


def load_definitions(ignore_ids: Optional[set[str]] = None) -> List[Dict[str, Any]]:
    sigs: List[Dict[str, Any]] = []
    ignore_ids = ignore_ids or set()
    for fname in ("injection-sigs.json", "exfil-patterns.json", "tool-abuse.json", "social-engineering.json"):
        fpath = GUARDIAN_DEFS / fname
        if not fpath.exists():
            continue
        try:
            data = json.loads(fpath.read_text(encoding="utf-8"))
            items = data if isinstance(data, list) else data.get("signatures", data.get("patterns", []))
            for item in items:
                sid = str(item.get("id", "?"))
                if sid not in ignore_ids:
                    sigs.append(item)
        except Exception:
            continue
    return sigs


def compile_patterns(sigs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    compiled: List[Dict[str, Any]] = []
    for sig in sigs:
        det = sig.get("detection", {}) if isinstance(sig.get("detection", {}), dict) else {}
        pats: List[str] = det.get("patterns", [])
        if not pats and isinstance(sig.get("patterns"), list):
            pats = sig["patterns"]
        if not pats and sig.get("pattern"):
            pats = [sig["pattern"]]

        case_sensitive = bool(det.get("case_sensitive", False))
        if sig.get("flags") == "i":
            case_sensitive = False
        flags = 0 if case_sensitive else re.IGNORECASE

        category = sig.get("category") or "unknown"
        sid = str(sig.get("id", ""))
        if category == "unknown":
            if sid.startswith("INJ"):
                category = "prompt_injection"
            elif sid.startswith("EXF"):
                category = "data_exfiltration"
            elif sid.startswith("TAB"):
                category = "tool_abuse"
            elif sid.startswith("SE"):
                category = "social_engineering"

        for pat in pats:
            try:
                compiled.append(
                    {
                        "regex": re.compile(pat, flags),
                        "id": sid or "?",
                        "severity": sig.get("severity", "low"),
                        "category": category,
                        "description": sig.get("description", ""),
                        "score": int(sig.get("score", 50)),
                    }
                )
            except re.error:
                continue
    return compiled


def extract_text(entry: Dict[str, Any]) -> Optional[str]:
    if entry.get("type") != "message":
        return None
    message = entry.get("message", {})
    content = message.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(str(c.get("text", "")) for c in content if isinstance(c, dict))
    return None


def normalize_ts(raw: Any) -> Optional[str]:
    if not raw:
        return None
    try:
        dt = datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).isoformat()
    except Exception:
        try:
            return datetime.fromtimestamp(float(raw), tz=timezone.utc).isoformat()
        except Exception:
            return str(raw)


def _classify_channel(path: str) -> str:
    p = path.lower()
    if "/cron/" in p:
        return "cron"
    if "email" in p:
        return "email"
    return "telegram"


def _clean_msg(text: Any, maxlen: int = 400) -> str:
    return " ".join(str(text or "").split())[:maxlen]


def build_context(messages: List[Dict[str, Any]], idx: int) -> str:
    start = max(0, idx - CONTEXT_RADIUS)
    end = min(len(messages), idx + CONTEXT_RADIUS + 1)
    lines: List[str] = []
    for i in range(start, end):
        prefix = "▶ " if i == idx else "· "
        lines.append(f"{prefix}{_clean_msg(messages[i].get('text', ''))}")
    return "\n".join(lines)


def build_context_parts(messages: List[Dict[str, Any]], idx: int) -> Dict[str, Optional[str]]:
    before = [_clean_msg(messages[i].get("text", "")) for i in range(max(0, idx - CONTEXT_RADIUS), idx)]
    after = [
        _clean_msg(messages[i].get("text", ""))
        for i in range(idx + 1, min(len(messages), idx + CONTEXT_RADIUS + 1))
    ]
    return {
        "context_before": "\n".join(before) if before else None,
        "context_match": _clean_msg(messages[idx].get("text", "")) or None,
        "context_after": "\n".join(after) if after else None,
    }


def scan_message(text: str, patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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


def _read_json(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def compute_channel_scanned_all_time() -> Dict[str, int]:
    totals: Dict[str, int] = {}

    # Telegram/Cron from raw session logs.
    for sdir in SESSION_DIRS:
        if not sdir.is_dir():
            continue
        for fpath in sdir.glob("*.jsonl"):
            channel = _classify_channel(str(fpath))
            count = 0
            try:
                for raw in fpath.read_text(encoding="utf-8", errors="ignore").splitlines():
                    if not raw.strip():
                        continue
                    try:
                        entry = json.loads(raw)
                    except Exception:
                        continue
                    text = extract_text(entry)
                    if text and len(text) >= 5:
                        count += 1
            except Exception:
                continue
            totals[channel] = totals.get(channel, 0) + count

    # Email comes from noc-email collector cumulative metrics.
    email_doc = _read_json(DASHBOARD_DIR / "noc-email.json")
    if not email_doc and DASHBOARD_DIR != LOCAL_DASHBOARD_DIR:
        email_doc = _read_json(LOCAL_DASHBOARD_DIR / "noc-email.json")
    guardian = email_doc.get("guardian", {})
    email_scanned = guardian.get("cumulative_scanned") or email_doc.get("cumulative_scanned") or guardian.get("scanned")
    if email_scanned:
        totals["email"] = int(email_scanned)

    return totals


def scan_sessions_incremental(db: GuardianDB, patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
    total_messages = 0
    total_clean = 0
    total_at_risk = 0
    total_blocked = 0
    category_counts: Dict[str, int] = {}
    channel_scanned: Dict[str, int] = {}
    channel_threats: Dict[str, int] = {}
    files_scanned = 0

    jsonl_files: List[str] = []
    for sdir in SESSION_DIRS:
        if sdir.is_dir():
            jsonl_files.extend(glob.glob(str(sdir / "*.jsonl")))

    for fpath in jsonl_files:
        channel = _classify_channel(fpath)
        try:
            stat = os.stat(fpath)
        except OSError:
            continue

        mtime = stat.st_mtime
        fsize = stat.st_size
        saved_offset, saved_mtime = db.get_bookmark(fpath)

        if mtime == saved_mtime and saved_offset >= fsize:
            continue
        if mtime != saved_mtime and fsize < saved_offset:
            saved_offset = 0

        files_scanned += 1
        try:
            with open(fpath, "r", encoding="utf-8", errors="ignore") as fh:
                fh.seek(saved_offset)
                raw_lines = fh.readlines()
            new_offset = fsize
        except Exception:
            raw_lines = []
            new_offset = saved_offset

        messages: List[Dict[str, Any]] = []
        for raw in raw_lines:
            line = raw.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except Exception:
                continue
            text = extract_text(msg)
            if text is None or len(text) < 5:
                continue
            messages.append(
                {
                    "text": text,
                    "ts": normalize_ts(msg.get("timestamp") or msg.get("ts") or msg.get("time")),
                }
            )

        for idx, msg in enumerate(messages):
            text = msg["text"]
            total_messages += 1
            channel_scanned[channel] = channel_scanned.get(channel, 0) + 1
            msg_hash = hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()
            hits = scan_message(text, patterns)
            if not hits:
                total_clean += 1
                continue

            total_at_risk += 1
            channel_threats[channel] = channel_threats.get(channel, 0) + 1
            best = max(hits, key=lambda h: h["score"])
            blocked = int(best["score"]) >= 80
            if blocked:
                total_blocked += 1

            cat = best["category"]
            category_counts[cat] = category_counts.get(cat, 0) + 1
            ctx_parts = build_context_parts(messages, idx)
            db.add_threat(
                sig_id=best["id"],
                category=best["category"],
                severity=best["severity"],
                score=best["score"],
                evidence=best["evidence"],
                description=best["description"],
                blocked=blocked,
                channel=channel,
                source_file=os.path.basename(fpath),
                message_hash=msg_hash,
                context=build_context(messages, idx),
                detected_at=msg.get("ts"),
                context_before=ctx_parts["context_before"],
                context_after=ctx_parts["context_after"],
                context_match=ctx_parts["context_match"],
            )

        db.set_bookmark(fpath, new_offset, mtime)

    if total_messages > 0 or files_scanned > 0:
        health = max(0, 100 - min(30, total_at_risk * 2) - min(20, total_blocked))
        db.record_scan(total_messages, files_scanned, total_clean, total_at_risk, total_blocked, category_counts, health)

    return {
        "messagesScanned": total_messages,
        "filesScanned": files_scanned,
        "clean": total_clean,
        "atRisk": total_at_risk,
        "blocked": total_blocked,
        "categories": category_counts,
        "channelScanned": channel_scanned,
        "channelThreats": channel_threats,
    }


def _read_daily_scanned_state(new_messages_scanned: int) -> int:
    today = datetime.now().strftime("%Y-%m-%d")
    state = _read_json(DAILY_STATE_FILE)
    if state.get("date") != today:
        state = {"date": today, "scanned_today": 0}
    state["scanned_today"] = int(state.get("scanned_today", 0)) + int(new_messages_scanned)
    try:
        DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
        DAILY_STATE_FILE.write_text(json.dumps(state), encoding="utf-8")
    except Exception:
        pass
    return int(state.get("scanned_today", 0))


def build_output(
    db: GuardianDB,
    scan_stats: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None,
    sig_count: Optional[int] = None,
    channel_scanned_all_time: Optional[Dict[str, int]] = None,
) -> Dict[str, Any]:
    threats_list = db.get_threats(hours=24, limit=80)
    summary_db = db.get_threat_summary(hours=24)
    hourly = db.get_metrics(period="hourly", days=1)
    all_time = db.get_current_totals()

    threats_out: List[Dict[str, Any]] = []
    for t in threats_list:
        threats_out.append(
            {
                "id": t["id"],
                "sig_id": t["sig_id"],
                "category": t["category"],
                "severity": t["severity"],
                "score": t["score"],
                "evidence": t["evidence"],
                "description": t["description"],
                "blocked": bool(t["blocked"]),
                "channel": t["channel"],
                "file": t["source_file"],
                "timestamp": t["detected_at"],
                "detected_at": t["detected_at"],
                "context": t.get("context"),
                "context_before": t.get("context_before"),
                "context_after": t.get("context_after"),
                "context_match": t.get("context_match"),
                "approved_override": t.get("approved_override", 0),
                "approved_by": t.get("approved_by"),
                "approved_at": t.get("approved_at"),
            }
        )

    total_scanned = int(all_time.get("totalScanned", 0) or 0)
    total_at_risk = int(summary_db["total"])
    total_clean = max(0, total_scanned - total_at_risk)

    channel_rows = db.conn.execute(
        "SELECT channel, COUNT(*) AS cnt, SUM(blocked) AS blk FROM threats WHERE dismissed=0 GROUP BY channel"
    ).fetchall()
    channels_all = {r[0]: {"threats": int(r[1]), "blocked": int(r[2] or 0)} for r in channel_rows if r[0]}

    channel_activity: Dict[str, Dict[str, int]] = {}
    all_time_scanned = channel_scanned_all_time if channel_scanned_all_time is not None else {}

    for ch, cnt in all_time_scanned.items():
        channel_activity.setdefault(ch, {"scanned": 0, "threats": 0, "blocked": 0})
        channel_activity[ch]["scanned"] = int(cnt)

    # BL-042 hardening: explicit run values must win for channels present in scan_stats.
    for ch, cnt in (scan_stats.get("channelScanned", {}) or {}).items():
        entry = channel_activity.setdefault(ch, {"scanned": 0, "threats": 0, "blocked": 0})
        entry["scanned"] = int(cnt)

    for ch, cnt in (scan_stats.get("channelThreats", {}) or {}).items():
        entry = channel_activity.setdefault(ch, {"scanned": 0, "threats": 0, "blocked": 0})
        entry["threats"] += int(cnt)

    for ch, meta in channels_all.items():
        entry = channel_activity.setdefault(ch, {"scanned": 0, "threats": 0, "blocked": 0})
        entry["threats"] = max(entry["threats"], int(meta.get("threats", 0)))
        entry["blocked"] = max(entry["blocked"], int(meta.get("blocked", 0)))

    scanned_today = _read_daily_scanned_state(int(scan_stats.get("messagesScanned", 0)))
    today_local = datetime.now().date()
    threats_today = 0
    for row in threats_out:
        ts = row.get("detected_at") or row.get("timestamp")
        if not ts:
            continue
        try:
            dt = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
            if dt.astimezone().date() == today_local:
                threats_today += 1
        except Exception:
            continue

    stats = {
        "total_scanned": total_scanned,
        "scanned_today": scanned_today,
        "threats_today": threats_today,
        "total_threats": total_at_risk,
        "total_blocked": int(summary_db["blocked"]),
        "definitions": sig_count,
        "files_scanned": int(scan_stats.get("filesScanned", 0)),
        "by_channel": channel_activity,
    }

    summary = {
        "total": total_at_risk,
        "messagesScanned": total_scanned,
        "filesScanned": int(scan_stats.get("filesScanned", 0)),
        "clean": total_clean,
        "atRisk": total_at_risk,
        "blocked": int(summary_db["blocked"]),
        "cleanPct": round((total_clean / max(total_scanned, 1)) * 100, 2),
        "injections": int(summary_db["injections"]),
        "exfiltration": int(summary_db["exfiltration"]),
        "toolAbuse": int(summary_db["toolAbuse"]),
        "socialEng": int(summary_db.get("socialEng", 0)),
        "categories": summary_db["categories"],
        "channels": channels_all,
    }

    mode = "active"
    cfg = config or {}
    if cfg.get("enabled") is False:
        mode = "disabled"
    elif cfg.get("admin_override"):
        mode = "monitor"

    allowlist_rows = db.conn.execute("SELECT * FROM allowlist WHERE active=1 ORDER BY created_at DESC").fetchall()
    allowlist_rules = [dict(r) for r in allowlist_rows]

    now = datetime.now(timezone.utc).isoformat()
    return {
        "lastScan": now,
        "scanned": total_scanned,
        "threats": threats_out,
        "summary": summary,
        "stats": stats,
        "channels": channel_activity,
        "trending": {
            "hourly": [
                {"period": m["period_start"], "atRisk": m["at_risk"], "scanned": m["messages_scanned"]}
                for m in hourly
            ]
        },
        "allTime": all_time,
        "config": cfg,
        "mode": mode,
        "updated": now,
        "generated_at": now,
        "allowlist": allowlist_rules,
    }


def write_config_snapshot(config_data: Dict[str, Any]) -> None:
    DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_OUTPUT.write_text(json.dumps(config_data, indent=2) + "\n", encoding="utf-8")


def run() -> Dict[str, Any]:
    config_data = load_config_safe()
    dismissed = set(config_data.get("dismissed_signatures") or [])
    patterns = compile_patterns(load_definitions(ignore_ids=dismissed))

    db_path = (Path(os.environ.get("GUARDIAN_DB_PATH", "")) if os.environ.get("GUARDIAN_DB_PATH") else (SKILL_ROOT / "guardian.db")).resolve()
    db = GuardianDB(db_path=str(db_path))
    try:
        scan_stats = scan_sessions_incremental(db, patterns)
        all_time_channel_scanned = compute_channel_scanned_all_time()
        result = build_output(
            db,
            scan_stats,
            config=config_data,
            sig_count=len(patterns),
            channel_scanned_all_time=all_time_channel_scanned,
        )
    finally:
        db.close()

    DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    write_config_snapshot(config_data)
    return result


def main() -> int:
    result = run()
    summary = result.get("summary", {})
    print(
        "Guardian scan: "
        f"{summary.get('messagesScanned', 0)} scanned all-time, "
        f"{summary.get('atRisk', 0)} at risk, {summary.get('blocked', 0)} blocked"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
