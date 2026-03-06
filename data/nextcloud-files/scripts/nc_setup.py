#!/usr/bin/env python3
"""
nc_setup.py - Initialize a folder structure in Nextcloud.
Part of the Nextcloud skill for OpenClaw.

Usage:
  python3 nc_setup.py --root Jarvis
  python3 nc_setup.py --root Jarvis --folders Articles,LinkedIn,Recherche,Veille
  python3 nc_setup.py --list    (list existing top-level folders)
"""

import argparse
import json
import sys
from pathlib import Path

# Allow running from any working directory
sys.path.insert(0, str(Path(__file__).resolve().parent))
from nextcloud import NextcloudClient, NextcloudError


def main():
    p = argparse.ArgumentParser(
        description="Initialize a Nextcloud folder structure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 nc_setup.py --root Jarvis
  python3 nc_setup.py --root Jarvis --folders Articles,LinkedIn,Recherche,Veille
  python3 nc_setup.py --list
"""
    )
    p.add_argument("--root",    default="",  help="Root folder to create under / (e.g. Jarvis)")
    p.add_argument("--folders", default="",  help="Comma-separated sub-folders to create inside --root")
    p.add_argument("--list",    action="store_true", help="List top-level folders and exit")
    args = p.parse_args()

    try:
        nc = NextcloudClient()
    except NextcloudError as e:
        print(f"✗ {e}", file=sys.stderr)
        sys.exit(1)

    # ── List mode ──────────────────────────────────────────────────────────────
    if args.list:
        items = nc.list_dir("/")
        dirs  = [i for i in items if i["is_dir"]]
        if not dirs:
            print("(no folders at root)")
        for d in dirs:
            print(f"📁  {d['name']}")
        return

    # ── Setup mode ─────────────────────────────────────────────────────────────
    root    = args.root.strip("/") if args.root else None
    folders = [f.strip() for f in args.folders.split(",") if f.strip()] if args.folders else []

    if not root and not folders:
        p.print_help()
        sys.exit(0)

    print(f"🔌 Connected: {nc.base_url} (user: {nc.user})")

    paths_to_create = []
    if root:
        paths_to_create.append(root)
        for sub in folders:
            paths_to_create.append(f"{root}/{sub}")
    else:
        paths_to_create.extend(folders)

    print(f"\n📁 Creating {len(paths_to_create)} folder(s)...")
    for path in paths_to_create:
        try:
            nc.mkdir(path)
            print(f"   ✓ /{path}")
        except Exception as e:
            print(f"   ~ /{path}  ({e})")

    print("\n✅ Done.")


if __name__ == "__main__":
    main()
