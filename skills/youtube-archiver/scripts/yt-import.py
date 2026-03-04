#!/usr/bin/env python3
"""Import YouTube playlist videos into markdown notes."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yt_utils


def build_parser():
    parser = argparse.ArgumentParser(description="Import YouTube playlists into markdown notes")
    parser.add_argument("--output", default="./YouTube-Archive", help="Output directory for notes")
    parser.add_argument("--config", default="", help="Path to config JSON (default: <output>/.config.json)")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing files")
    parser.add_argument("--no-summary", action="store_true", help="Skip transcript + summary generation")
    parser.add_argument("--no-tags", action="store_true", help="Skip auto-tagging")
    parser.add_argument("--playlist", action="append", default=[], help="Import only this playlist ID (repeatable)")
    parser.add_argument("--init", action="store_true", help="Create default .config.json and README.md in output dir")
    parser.add_argument("--cookies", default="", help="Path to cookies.txt file")
    parser.add_argument("--browser", default="", help="Browser for cookie auth (chrome, firefox, edge, ...)")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    output_dir = Path(args.output).expanduser().resolve()
    config_path = Path(args.config).expanduser().resolve() if args.config else (output_dir / ".config.json")

    if args.init:
        result = yt_utils.initialize_output(
            output_dir=output_dir,
            config_path=config_path,
            import_script_path=Path(__file__).resolve(),
            enrich_script_path=(Path(__file__).resolve().parent / "yt-enrich.py"),
        )
        print("✅ Initialized youtube-archiver")
        print("   Config: {0}".format(result["config_path"]))
        print("   README: {0}".format(result["readme_path"]))
        return 0

    try:
        config, warnings = yt_utils.load_and_validate_config(
            config_path,
            strict=False,
            create_if_missing=False,
        )
    except yt_utils.ConfigError as exc:
        print("❌ Config error: {0}".format(exc), file=sys.stderr)
        print("   Tip: run with --init to create a default config.", file=sys.stderr)
        return 1

    for warning in warnings:
        print("⚠️  {0}".format(warning))

    lock_path = None
    if not args.dry_run:
        try:
            lock_path = yt_utils.acquire_lock(output_dir)
        except yt_utils.LockError as exc:
            print("❌ {0}".format(exc), file=sys.stderr)
            return 1

    try:
        stats = yt_utils.import_videos(
            output_dir=output_dir,
            config=config,
            dry_run=args.dry_run,
            no_summary=bool(args.no_summary),
            no_tags=bool(args.no_tags),
            playlist_ids=args.playlist or None,
            browser_override=args.browser or None,
            cookies_override=args.cookies or None,
        )

        if not args.dry_run:
            yt_utils.update_sync_state(output_dir, mode="import", stats=stats)

        print("🎬 Import finished")
        print("   Playlists:   {0}".format(stats.get("playlists", 0)))
        print("   Created:     {0}".format(stats.get("created", 0)))
        print("   Skipped:     {0}".format(stats.get("skipped", 0)))
        print("   Failed:      {0}".format(stats.get("failed", 0)))
        if args.dry_run:
            print("   Would create:{0}".format(stats.get("would_create", 0)))

        errors = stats.get("errors", [])
        if errors:
            print("\nErrors:")
            for err in errors[:20]:
                print(" - {0}".format(err))

        return 0 if stats.get("failed", 0) == 0 else 2
    finally:
        if lock_path is not None:
            yt_utils.release_lock(lock_path)


if __name__ == "__main__":
    sys.exit(main())
