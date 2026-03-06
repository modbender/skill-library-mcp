#!/usr/bin/env python3
"""LYGO-MINT Operator Suite (v2) — verify a pack.

Usage:
  python scripts/verify_pack_v2.py --input <file|dir> --pack-sha256 <hash>

Exit codes:
  0 = PASS
  2 = FAIL
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from mint_pack_v2 import (  # type: ignore
    list_files,
    hash_file,
    canonical_manifest,
    sha256_text,
    CANON_RULESET,
)

try:
    import sys
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--pack-sha256", required=True)
    ap.add_argument("--title", default="")
    ap.add_argument("--version", default="")
    ap.add_argument("--author", default="")
    ap.add_argument("--tags", default="LYGO,Δ9Council")
    args = ap.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        raise SystemExit(f"Input not found: {input_path}")

    root, files = list_files(input_path)
    file_records = [hash_file(root, p) for p in files]

    # Build minimal manifest (meta removed from hash-critical part except title/version/author are unknown here)
    manifest = {
        "lygo_mint": {"v": 2, "canon": CANON_RULESET},
        "meta": {"title": args.title or None, "version": args.version or None, "author": args.author or None},
        "tags": [t.strip() for t in (args.tags or "").split(",") if t.strip()],
        "files": file_records,
    }

    canon = canonical_manifest(manifest)
    got = sha256_text(canon)

    ok = (got.lower() == args.pack_sha256.lower())
    out = {
        "ok": ok,
        "expected": args.pack_sha256,
        "got": got,
        "fileCount": len(file_records),
    }

    print(json.dumps(out, ensure_ascii=False, indent=2))
    raise SystemExit(0 if ok else 2)


if __name__ == "__main__":
    main()
