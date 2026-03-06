#!/usr/bin/env python3
"""Analyze OpenClaw cron jobs JSON and emit a concise ops report.

Input schema (expected): output of OpenClaw cron(list):
{
  "jobs": [
    {
      "id": "...",
      "name": "...",
      "enabled": true,
      "schedule": {"kind":"cron","expr":"...","tz":"..."} | {"kind":"every","everyMs":...} | {"kind":"at","at":"..."},
      "delivery": {"mode":"none"|"announce"},
      "sessionTarget": "isolated"|"main",
      "state": {"lastStatus":"ok"|"error", "consecutiveErrors": 0, "lastError": "..."}
    }
  ]
}

This tool is public-safe: it only reports.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def schedule_str(s: dict) -> str:
    if not s:
        return "?"
    k = s.get("kind")
    if k == "cron":
        tz = s.get("tz") or ""
        return f"cron:{s.get('expr')} {tz}".strip()
    if k == "every":
        ms = s.get("everyMs")
        return f"every:{ms}ms"
    if k == "at":
        return f"at:{s.get('at')}"
    return str(s)


def is_frequent(schedule: dict) -> bool:
    # heuristic: hourly or more frequent
    if not schedule:
        return False
    if schedule.get("kind") == "every":
        ms = schedule.get("everyMs") or 0
        return ms and ms <= 60 * 60 * 1000
    if schedule.get("kind") == "cron":
        expr = schedule.get("expr") or ""
        # crude: contains */1 or * in hour field
        return "*/" in expr or expr.strip().startswith("*")
    return False


def delivery_mode(job: dict) -> str:
    d = job.get("delivery") or {}
    return d.get("mode") or "none"


def norm_name(name: str) -> str:
    name = (name or "").lower()
    name = re.sub(r"\s+", " ", name).strip()
    # strip time/cadence tokens
    name = re.sub(r"\b(daily|hourly|weekly|am/pm|\d{1,2}:\d{2})\b", "", name)
    return re.sub(r"\s+", " ", name).strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True, help="Path to cron list JSON")
    args = ap.parse_args()

    data = load_json(Path(args.inp))
    jobs = data.get("jobs") or []

    enabled = [j for j in jobs if j.get("enabled")]
    disabled = [j for j in jobs if not j.get("enabled")]

    announce = [j for j in enabled if delivery_mode(j) == "announce"]
    errors = [j for j in enabled if (j.get("state") or {}).get("lastStatus") == "error" or (j.get("state") or {}).get("consecutiveErrors", 0) > 0]
    frequent = [j for j in enabled if is_frequent(j.get("schedule") or {})]

    # duplicate-ish detection by normalized name
    buckets: Dict[str, List[dict]] = {}
    for j in enabled:
        buckets.setdefault(norm_name(j.get("name") or ""), []).append(j)
    dups = [(k, v) for k, v in buckets.items() if k and len(v) >= 2]
    dups.sort(key=lambda kv: len(kv[1]), reverse=True)

    lines: List[str] = []
    lines.append("AOI Cron Ops (Lite) — Audit Report")
    lines.append(f"- Jobs: enabled {len(enabled)} / disabled {len(disabled)} (total {len(jobs)})")
    lines.append(f"- Announce(notify): {len(announce)} | Frequent-ish: {len(frequent)} | Error-ish: {len(errors)}")

    risks: List[str] = []
    if len(announce) >= 5:
        risks.append(f"notification spam risk: {len(announce)} announce jobs")
    if errors:
        top = errors[0]
        risks.append(f"errors present: e.g. '{top.get('name')}'")
    if dups:
        k, v = dups[0]
        risks.append(f"possible duplicate purpose: '{k}' x{len(v)}")
    if frequent and len(frequent) >= 3:
        risks.append(f"high cadence load: {len(frequent)} jobs hourly+ (heuristic)")

    if risks:
        lines.append("Top risks:")
        for r in risks[:5]:
            lines.append(f"- {r}")

    lines.append("Recommendations (report-only):")
    if dups:
        lines.append("- consolidate duplicates: keep 1 canonical job, disable others")
    if len(announce) >= 3:
        lines.append("- switch non-critical jobs delivery.mode -> none, add 1 digest job")
    if errors:
        lines.append("- for flaky external deps (502/401): add retry/backoff or downgrade to none")
    if frequent:
        lines.append("- slow heavy jobs (community patrol/research) to 4–12h cadence")

    # show minimal apply plan (not executed)
    lines.append("Apply plan (DO NOT auto-apply; require approval):")
    for j in announce[:5]:
        lines.append(f"- patch {j.get('id')}: delivery.mode=none  # {j.get('name')}")

    if errors:
        e = errors[0]
        st = e.get("state") or {}
        le = (st.get("lastError") or "").strip()
        if le:
            le = le[:160]
        lines.append(f"- investigate: {e.get('name')} lastError='{le}'")

    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
