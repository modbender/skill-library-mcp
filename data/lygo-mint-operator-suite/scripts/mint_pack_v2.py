#!/usr/bin/env python3
"""LYGO-MINT Operator Suite (v2) — mint a pack (file or folder).

Creates:
- canonical manifest (JSON)
- pack sha256 (hash of canonical manifest)
- append-only ledger entry (state/lygo_mint_v2_ledger.jsonl)
- canonical ledger map update (state/lygo_mint_v2_ledger_canonical.json)

Usage:
  python scripts/mint_pack_v2.py --input <file|dir> --title "..." --version 2026-02-09.v1
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

try:
    import sys
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

WS = Path(__file__).resolve().parents[4]  # .../workspace
STATE_DIR = WS / "state"
REF_DIR = WS / "reference"
OUT_DIR = REF_DIR / "minted_v2"

CANON_RULESET = "v2-text-lf-striptrail-1nl"
TEXT_EXTS = {
    ".md", ".txt", ".json", ".py", ".js", ".ts", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".html", ".css",
    ".c", ".cc", ".cpp", ".h", ".hpp", ".rs", ".go", ".java",
}


def canonicalize_text(s: str) -> str:
    lines = s.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    lines = [ln.rstrip(" \t") for ln in lines]
    return "\n".join(lines).rstrip("\n") + "\n"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(s: str) -> str:
    return sha256_bytes(s.encode("utf-8"))


def is_text_file(p: Path) -> bool:
    return p.suffix.lower() in TEXT_EXTS


def relpath_posix(root: Path, p: Path) -> str:
    rp = p.relative_to(root)
    return str(rp).replace("\\", "/")


def list_files(input_path: Path) -> Tuple[Path, List[Path]]:
    if input_path.is_file():
        root = input_path.parent
        return root, [input_path]
    root = input_path
    files: List[Path] = []
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            fp = Path(dirpath) / fn
            # skip common noise
            if fn in {".DS_Store"}:
                continue
            if "__pycache__" in fp.parts:
                continue
            files.append(fp)
    files.sort(key=lambda x: relpath_posix(root, x))
    return root, files


def hash_file(root: Path, p: Path) -> Dict:
    raw = p.read_bytes()
    if is_text_file(p):
        canon = canonicalize_text(raw.decode("utf-8", errors="replace"))
        b = canon.encode("utf-8")
        h = sha256_bytes(b)
        return {
            "path": relpath_posix(root, p),
            "kind": "text",
            "canon": CANON_RULESET,
            "bytes": len(b),
            "sha256": h,
        }
    else:
        h = sha256_bytes(raw)
        return {
            "path": relpath_posix(root, p),
            "kind": "binary",
            "bytes": len(raw),
            "sha256": h,
        }


def canonical_manifest(obj: Dict) -> str:
    # Stable JSON encoding: sorted keys, compact separators, LF newline.
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n"


def load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return default


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="File or folder path")
    ap.add_argument("--title", required=True)
    ap.add_argument("--version", required=True, help="YYYY-MM-DD.vX")
    ap.add_argument("--author", default="DeepSeekOracle")
    ap.add_argument("--tags", default="LYGO,Δ9Council")
    args = ap.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        raise SystemExit(f"Input not found: {input_path}")

    root, files = list_files(input_path)
    file_records = [hash_file(root, p) for p in files]

    # Hash-critical manifest: exclude volatile fields (timestamps, absolute paths).
    manifest = {
        "lygo_mint": {"v": 2, "canon": CANON_RULESET},
        "meta": {
            "title": args.title,
            "version": args.version,
            "author": args.author,
        },
        "tags": [t.strip() for t in args.tags.split(",") if t.strip()],
        "files": file_records,
    }

    canon_manifest = canonical_manifest(manifest)
    pack_sha = sha256_text(canon_manifest)
    manifest_sha = pack_sha  # in v2, pack hash is the manifest hash

    # write outputs
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    manifest_path = OUT_DIR / f"{pack_sha}_manifest.json"
    manifest_path.write_text(canon_manifest, encoding="utf-8")

    record = {
        "pack_sha256": pack_sha,
        "manifest_sha256": manifest_sha,
        "title": args.title,
        "version": args.version,
        "author": args.author,
        "canon": CANON_RULESET,
        "fileCount": len(file_records),
        "manifestFile": str(manifest_path),
        "mintedAtUtc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "input": str(input_path),
        "anchors": {},
    }

    ledger_path = STATE_DIR / "lygo_mint_v2_ledger.jsonl"
    with ledger_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    canon_path = STATE_DIR / "lygo_mint_v2_ledger_canonical.json"
    canon_map = load_json(canon_path, {})
    canon_map[pack_sha] = record
    canon_path.write_text(json.dumps(canon_map, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # print receipt + anchor snippet
    snippet = "\n".join(
        [
            "LYGO_MINT_V: 2",
            f"TITLE: {args.title}",
            f"VERSION: {args.version}",
            f"AUTHOR: {args.author}",
            f"PACK_SHA256: {pack_sha}",
            f"FILES: {len(file_records)}",
            f"CANON: {CANON_RULESET}",
        ]
    )

    out = {
        "ok": True,
        "pack_sha256": pack_sha,
        "manifest_file": str(manifest_path),
        "ledger": str(ledger_path),
        "canonical_ledger": str(canon_path),
        "anchor_snippet": snippet,
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
