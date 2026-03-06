#!/usr/bin/env python3
"""Verify STARCORE-family contracts via Blockscout + Dexscreener.

Outputs: state/starcore_family_verify.json

Classification per symbol:
- launched_confirmed: Clawnch receipt present (contractAddress populated)
- indexed_ok: Blockscout reports is_contract=True (best effort; may lag)
- pair_found: Dexscreener returns at least one pair

Usage:
  python verify_starcore_family.py --symbols STARCORE,STARCOREX,STARCORECOIN
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import requests

ROOT = Path(__file__).resolve().parents[4]  # .../workspace
STATE = ROOT / "state"


def load_receipts(symbols: list[str]) -> dict[str, dict[str, Any]]:
    data: dict[str, dict[str, Any]] = {}
    for sym in symbols:
        p = STATE / f"{sym}_clawnch_receipt.json"
        if p.exists():
            try:
                data[sym] = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                pass
    return data


def check_blockscout(addr: str) -> dict[str, Any]:
    url = f"https://base.blockscout.com/api/v2/addresses/{addr}"
    try:
        r = requests.get(url, timeout=15)
        if r.status_code != 200:
            return {"status": "error", "code": r.status_code}
        j = r.json()
        return {
            "status": "ok",
            "is_contract": bool(j.get("is_contract")),
            "has_logs": j.get("has_logs"),
            "token": j.get("token"),
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


def check_dexscreener(addr: str) -> dict[str, Any]:
    url = f"https://api.dexscreener.com/latest/dex/search/?q={addr}"
    try:
        r = requests.get(url, timeout=15)
        if r.status_code != 200:
            return {"status": "error", "code": r.status_code}
        j = r.json()
        pairs = j.get("pairs") or []
        return {"status": "ok", "pairs_found": len(pairs), "pairs": pairs[:3]}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbols", default="STARCORE,STARCOREX,STARCORECOIN", help="Comma-separated symbols")
    args = ap.parse_args()
    symbols = [s.strip().upper() for s in args.symbols.split(",") if s.strip()]

    STATE.mkdir(exist_ok=True)
    receipts = load_receipts(symbols)

    report = {}
    for sym in symbols:
        rec = receipts.get(sym) or {}
        contract = rec.get("contractAddress") or ""
        entry = {
            "contractAddress": contract,
            "launched_confirmed": bool(contract),
            "indexed_ok": False,
            "pair_found": False,
            "blockscout": {},
            "dexscreener": {},
        }
        if contract:
            bs = check_blockscout(contract)
            entry["blockscout"] = bs
            if bs.get("status") == "ok" and bs.get("is_contract"):
                entry["indexed_ok"] = True

            ds = check_dexscreener(contract)
            entry["dexscreener"] = ds
            if ds.get("status") == "ok" and ds.get("pairs_found", 0) > 0:
                entry["pair_found"] = True

        report[sym] = entry

    out_path = STATE / "starcore_family_verify.json"
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[OK] Verification report: {out_path}")

    missing = [s for s in symbols if not receipts.get(s)]
    if missing:
        print(f"[WARN] Missing receipts for: {', '.join(missing)}")
        raise SystemExit(2)


if __name__ == "__main__":
    main()
