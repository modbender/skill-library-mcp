#!/usr/bin/env python3
"""Enrich imported YouTube notes with transcripts, summaries, and tags."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yt_utils


def build_parser():
    parser = argparse.ArgumentParser(description="Enrich YouTube notes")
    parser.add_argument("--output", default="./YouTube-Archive", help="Output directory containing notes")
    parser.add_argument("--config", default="", help="Path to config JSON (default: <output>/.config.json)")
    parser.add_argument("--dry-run", action="store_true", help="Preview enrichment without writing files")
    parser.add_argument("--limit", type=int, default=None, help="Maximum number of notes to enrich")
    parser.add_argument("--strict-config", action="store_true", help="Fail on unknown config keys")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    output_dir = Path(args.output).expanduser().resolve()
    config_path = Path(args.config).expanduser().resolve() if args.config else (output_dir / ".config.json")

    try:
        config, warnings = yt_utils.load_and_validate_config(
            config_path,
            strict=bool(args.strict_config),
            create_if_missing=False,
        )
    except yt_utils.ConfigError as exc:
        print("❌ Config error: {0}".format(exc), file=sys.stderr)
        print("   Tip: run yt-import.py --init first.", file=sys.stderr)
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
        stats = yt_utils.enrich_notes(
            output_dir=output_dir,
            config=config,
            dry_run=bool(args.dry_run),
            limit=args.limit,
        )

        if not args.dry_run:
            yt_utils.update_sync_state(output_dir, mode="enrich", stats=stats)

        print("🔄 Enrichment finished")
        print("   Processed: {0}".format(stats.get("processed", 0)))
        print("   Enriched:  {0}".format(stats.get("enriched", 0)))
        print("   Skipped:   {0}".format(stats.get("skipped", 0)))
        print("   Failed:    {0}".format(stats.get("failed", 0)))

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
