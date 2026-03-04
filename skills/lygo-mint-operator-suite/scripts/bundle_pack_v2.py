#!/usr/bin/env python3
"""Create a deterministic-ish bundle zip for a pack folder.

Notes:
- Zip format itself can embed timestamps; we set them to a constant.
- File order is sorted by relative path.

Usage:
  python scripts/bundle_pack_v2.py --input <dir> --out tmp/pack.bundle.zip
"""

from __future__ import annotations

import argparse
import os
import zipfile
from pathlib import Path

from mint_pack_v2 import relpath_posix

FIXED_DT = (2020, 1, 1, 0, 0, 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    src = Path(args.input).expanduser().resolve()
    if not src.is_dir():
        raise SystemExit("--input must be a directory")

    outp = Path(args.out).expanduser().resolve()
    outp.parent.mkdir(parents=True, exist_ok=True)

    files = []
    for dirpath, _, filenames in os.walk(src):
        for fn in filenames:
            fp = Path(dirpath) / fn
            if fn in {".DS_Store"}:
                continue
            if "__pycache__" in fp.parts:
                continue
            files.append(fp)
    files.sort(key=lambda x: relpath_posix(src, x))

    with zipfile.ZipFile(outp, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for fp in files:
            arc = relpath_posix(src, fp)
            zi = zipfile.ZipInfo(arc, date_time=FIXED_DT)
            zi.compress_type = zipfile.ZIP_DEFLATED
            data = fp.read_bytes()
            z.writestr(zi, data)

    print(str(outp))


if __name__ == "__main__":
    main()
