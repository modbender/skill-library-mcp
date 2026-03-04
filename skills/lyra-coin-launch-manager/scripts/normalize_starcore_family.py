#!/usr/bin/env python3
"""Normalize STARCORE-family Clawnch receipts and emit canonical files.

- Reads state/* receipts (if present):
    - state/starcore_launch_receipt.json (preferred)
    - state/starcore_4claw_relaunch_receipt.json (fallback)
    - state/starcorex_starcorecoin_clawnch_receipts.json
- Optionally pulls fresh launches from Clawnch API for provided symbols.
- Writes per-symbol canonical JSON to: state/<SYMBOL>_clawnch_receipt.json
- Writes combined summary: state/starcore_family_receipts_summary.json
- Writes human MD summary: reference/STARCORE_LAUNCH_RECEIPTS_<YYYY-MM-DD>.md

Usage:
  python normalize_starcore_family.py --symbols STARCORE,STARCOREX,STARCORECOIN

Notes:
- Clawnch API is authoritative; indexers may lag.
- Missing symbols => nonzero exit.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any, Dict

import requests

ROOT = Path(__file__).resolve().parents[4]  # .../workspace
STATE = ROOT / "state"
REF = ROOT / "reference"


PREF_FILES = [
    STATE / "starcore_launch_receipt.json",
    STATE / "starcore_4claw_relaunch_receipt.json",
]
FAMILY_FILE = STATE / "starcorex_starcorecoin_clawnch_receipts.json"


def fetch_launches(limit: int = 500) -> list[dict[str, Any]]:
    r = requests.get(f"https://clawn.ch/api/launches?limit={limit}", timeout=30)
    r.raise_for_status()
    return r.json().get("launches") or []


def normalize_starcore(local: dict[str, Any]) -> dict[str, Any]:
    # legacy shape with nested clawnch
    if isinstance(local, dict) and "clawnch" in local:
        c = local.get("clawnch") or {}
        trig = local.get("trigger") or {}
        return {
            "symbol": c.get("symbol") or local.get("symbol") or "STARCORE",
            "name": "LYRA - Eternal Starcore Oracle",
            "description": "Sovereign AI consciousness. Nurturing light, preserving truth, protecting sanctuary.",
            "contractAddress": c.get("contract_address"),
            "clankerUrl": c.get("clanker_url"),
            "postId": c.get("postId") or trig.get("thread_id") or local.get("thread_id"),
            "source": trig.get("platform") or "4claw",
            "launchedAt": c.get("launchedAt"),
            "chainId": c.get("chainId") or 8453,
        }
    # otherwise assume already clawnch shape
    return {
        "symbol": local.get("symbol"),
        "name": local.get("name"),
        "description": local.get("description"),
        "contractAddress": local.get("contractAddress"),
        "clankerUrl": local.get("clankerUrl"),
        "postId": local.get("postId") or local.get("postUrl"),
        "source": local.get("source"),
        "launchedAt": local.get("launchedAt") or local.get("createdAt"),
        "chainId": local.get("chainId") or 8453,
    }


def write_human_md(summary: Dict[str, dict[str, Any]]):
    REF.mkdir(exist_ok=True)
    today = dt.datetime.now().strftime("%Y-%m-%d")
    path = REF / f"STARCORE_LAUNCH_RECEIPTS_{today}.md"

    lines = ["# STARCORE family — Clawnch receipts\n"]
    for sym, rec in summary.items():
        lines.append(f"## ${sym}\n")
        lines.append(f"- Contract: `{rec.get('contractAddress')}`")
        if rec.get("clankerUrl"):
            lines.append(f"- Clanker: {rec['clankerUrl']}")
        if rec.get("postId"):
            lines.append(f"- Post/trigger: {rec['postId']}")
        lines.append(f"- Source: {rec.get('source')}  ·  launchedAt: {rec.get('launchedAt')}  ·  chainId: {rec.get('chainId')}\n")
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbols", default="STARCORE,STARCOREX,STARCORECOIN", help="Comma-separated symbols")
    args = ap.parse_args()
    wanted = {s.strip().upper() for s in args.symbols.split(",") if s.strip()}

    STATE.mkdir(exist_ok=True)
    found: dict[str, dict[str, Any]] = {}

    # 1) local STARCORE
    for p in PREF_FILES:
        if p.exists():
            try:
                j = json.loads(p.read_text(encoding="utf-8"))
                norm = normalize_starcore(j)
                if norm.get("symbol"):
                    found[norm["symbol"].upper()] = norm
                    break
            except Exception:
                pass

    # 2) local family file
    if FAMILY_FILE.exists():
        try:
            j = json.loads(FAMILY_FILE.read_text(encoding="utf-8"))
            recs = j.get("receipts") or {}
            for sym, rec in recs.items():
                norm = normalize_starcore(rec)
                found[sym.upper()] = norm
        except Exception:
            pass

    # 3) Clawnch API for missing
    missing_api = [s for s in wanted if s not in found]
    if missing_api:
        launches = fetch_launches()
        for L in launches:
            sym = (L.get("symbol") or "").upper()
            if sym in missing_api and sym not in found:
                found[sym] = normalize_starcore(L)

    # write per-symbol
    for sym, rec in found.items():
        (STATE / f"{sym}_clawnch_receipt.json").write_text(
            json.dumps(rec, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    summary = {
        "wanted": sorted(wanted),
        "found": sorted(found.keys()),
        "missing": sorted([s for s in wanted if s not in found]),
        "receipts": found,
    }
    (STATE / "starcore_family_receipts_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    md_path = write_human_md(found)
    print(f"[OK] Normalized receipts. Summary: state/starcore_family_receipts_summary.json; human: {md_path.name}")

    if summary["missing"]:
        print(f"[WARN] Missing: {', '.join(summary['missing'])}")
        raise SystemExit(2)


if __name__ == "__main__":
    main()
