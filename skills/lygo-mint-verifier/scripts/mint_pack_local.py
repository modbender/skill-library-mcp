#!/usr/bin/env python3
"""Mint (canonicalize + hash) a local pack file and write ledger receipts.

This is a thin wrapper around the workspace LYGO-MINT tools.

Usage:
  python scripts/mint_pack_local.py --pack reference/CHAMPION_PACK_LYRA_V1.md --version 2026-02-07.v1 --champion LYRA --anchor SEAL_55_T

Outputs:
- prints hash + anchor snippet
- appends to state/lygo_mint_ledger.jsonl
- updates state/lygo_mint_ledger_canonical.json

No secrets are read or printed.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]  # workspace root
LEDGER = ROOT / "state" / "lygo_mint_ledger.jsonl"
CANON = ROOT / "state" / "lygo_mint_ledger_canonical.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def run_py(path: Path, args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(path), *args], cwd=str(ROOT), capture_output=True, text=True)


def main() -> None:
    # Force UTF-8 stdout on Windows so symbols like "Δ" don't crash.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    ap = argparse.ArgumentParser()
    ap.add_argument("--pack", required=True)
    ap.add_argument("--version", required=True)
    ap.add_argument("--champion", default="")
    ap.add_argument("--anchor", default="")
    ap.add_argument("--title", default="")
    args = ap.parse_args()

    # Resolve relative paths against workspace root
    # Resolve relative paths robustly:
    # - First relative to workspace root
    # - If that fails, try relative to current working directory
    if Path(args.pack).is_absolute():
        pack_path = Path(args.pack)
    else:
        cand1 = (ROOT / args.pack).resolve()
        cand2 = Path(args.pack).resolve()
        pack_path = cand1 if cand1.exists() else cand2

    if not pack_path.exists():
        raise SystemExit(f"Pack not found: {pack_path}")

    # Mint using existing tool
    mint_tool = ROOT / "tools" / "lygo_mint" / "mint_pack.py"
    if not mint_tool.exists():
        raise SystemExit(f"Missing mint tool: {mint_tool}")

    # Expect mint tool to output JSON or text; we treat stdout as the minted record if JSON.
    # Workspace mint tool expects positional pack_path
    proc = run_py(mint_tool, [str(pack_path), "--version", args.version, "--champion", args.champion or "", "--anchor", args.anchor or ""])
    if proc.returncode != 0:
        if proc.stdout:
            print(proc.stdout)
        if proc.stderr:
            print(proc.stderr, file=sys.stderr)
        raise SystemExit(proc.returncode)

    minted_raw = proc.stdout.strip()
    minted = None
    try:
        minted = json.loads(minted_raw)
    except Exception:
        # Fallback: store as text
        minted = {"raw": minted_raw}

    # Ensure required metadata
    minted.update({
        "pack_path": str(pack_path),
        "pack_version": args.version,
        "champion": args.champion,
        "anchor": args.anchor,
        "minted_at_utc": utc_now(),
        "kind": "mint",
    })

    # Append ledger
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open("a", encoding="utf-8") as f:
        f.write(json.dumps(minted, ensure_ascii=False) + "\n")

    # Canonicalize ledger
    canon_tool = ROOT / "tools" / "lygo_mint" / "canonicalize_ledger.py"
    if canon_tool.exists():
        _ = run_py(canon_tool, [])

    # Create anchor snippet
    h = minted.get("hash") or minted.get("LYGO_HASH_SHA256") or minted.get("lygo_hash_sha256") or ""
    title = args.title or pack_path.stem

    print("MINTED")
    print("pack:", pack_path)
    print("version:", args.version)
    if h:
        print("hash:", h)

    print("\nANCHOR_SNIPPET")
    print(f"LYGO-MINT v1 | {title} | {args.version}")
    if args.champion:
        print(f"CHAMPION: {args.champion}")
    if args.anchor:
        print(f"ANCHOR: {args.anchor}")
    if h:
        print(f"HASH_SHA256: {h}")
    print(f"MINTED_AT_UTC: {minted['minted_at_utc']}")
    print(f"LEDGER: state/lygo_mint_ledger.jsonl")
    print(f"CANON: state/lygo_mint_ledger_canonical.json")


if __name__ == "__main__":
    main()
