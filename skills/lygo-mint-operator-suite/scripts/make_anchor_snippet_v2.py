#!/usr/bin/env python3
"""Generate a platform-specific Anchor Snippet for LYGO-MINT v2.

Usage:
  python scripts/make_anchor_snippet_v2.py --pack-sha256 <hash> --title "..." --version 2026-02-09.v1 --platform moltx
"""

from __future__ import annotations

import argparse

PLATFORMS = {"moltx", "moltbook", "discord", "x", "4claw"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack-sha256", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--version", required=True)
    ap.add_argument("--author", default="DeepSeekOracle")
    ap.add_argument("--files", type=int, default=None)
    ap.add_argument("--canon", default="v2-text-lf-striptrail-1nl")
    ap.add_argument("--platform", default="moltx", choices=sorted(PLATFORMS))
    args = ap.parse_args()

    block = "\n".join(
        [
            "LYGO_MINT_V: 2",
            f"TITLE: {args.title}",
            f"VERSION: {args.version}",
            f"AUTHOR: {args.author}",
            f"PACK_SHA256: {args.pack_sha256}",
            (f"FILES: {args.files}" if args.files is not None else "FILES: ?"),
            f"CANON: {args.canon}",
        ]
    )

    if args.platform in {"discord"}:
        out = f"```\n{block}\n```"
    else:
        out = block

    print(out)


if __name__ == "__main__":
    main()
