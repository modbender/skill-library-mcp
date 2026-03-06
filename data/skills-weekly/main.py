"""
main.py — SkillMetricScraper v3 CLI (ClawHub Real API Edition)

Usage:
    python main.py [--top N] [--days N] [--output FILE] [--week LABEL]
    python main.py --snapshot-only       # Record snapshot, skip script generation
    python main.py --list-db             # Show current DB state
    python main.py --mock                # Use synthetic data (offline dev)
    python main.py --max-pages 5         # Limit API pages (testing)
    python main.py --sort trending       # Sort: downloads, trending, installsCurrent, updated, stars

Environment (.env):
    CLAWHUB_BASE_URL    ClawHub registry URL (default: https://clawhub.ai)
    GITHUB_TOKEN        For fetching source READMEs from GitHub
    ANTHROPIC_API_KEY   For script generation
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

import discovery
import storage
import ranker
import harvester
import script_generator


def parse_args():
    parser = argparse.ArgumentParser(
        description="Discover, rank, and generate YouTube scripts for trending ClawHub skills."
    )
    parser.add_argument("--top", type=int, default=10, help="Top N skills to script (default: 10)")
    parser.add_argument("--days", type=int, default=7, help="Trailing days for velocity (default: 7)")
    parser.add_argument("--output", type=str, default=None, help="Output markdown file path")
    parser.add_argument("--week", type=str, default=None, help="Week label for report header")
    parser.add_argument("--model", type=str, default="claude-haiku-4-5-20251001", help="Anthropic model")
    parser.add_argument("--sort", type=str, default="downloads", help="ClawHub sort: downloads, trending, installsCurrent, updated, stars")
    parser.add_argument("--max-pages", type=int, default=0, help="Limit API pages (0 = unlimited)")
    parser.add_argument("--snapshot-only", action="store_true", help="Record snapshot only, skip LLM")
    parser.add_argument("--list-db", action="store_true", help="Print DB snapshot count and exit")
    parser.add_argument("--mock", action="store_true", help="Use synthetic data (offline dev)")
    parser.add_argument("--episode", type=int, default=1, help="Episode number for video script")
    return parser.parse_args()


def load_env() -> dict:
    load_dotenv()
    return {
        "github_token": os.getenv("GITHUB_TOKEN", ""),
        "anthropic_key": os.getenv("ANTHROPIC_API_KEY", ""),
        "clawhub_url": os.getenv("CLAWHUB_BASE_URL", ""),
    }


def main():
    args = parse_args()
    env = load_env()

    # --list-db
    if args.list_db:
        storage.init_db()
        count = storage.snapshot_count()
        latest = storage.get_latest_snapshot()
        dates = storage.distinct_snapshot_dates()
        print(f"DB: {storage.DB_PATH}")
        print(f"Total snapshot rows: {count}")
        print(f"Distinct snapshot dates: {len(dates)}")
        for d in dates[-5:]:
            print(f"  {d}")
        print(f"Skills with data: {len(latest)}")
        for row in latest[:15]:
            print(
                f"  {row['display_name']:35s} "
                f"installs={row['installs_current']:>6,}  "
                f"downloads={row['downloads']:>8,}  "
                f"stars={row['stars']:>4}"
            )
        return

    week_label = args.week or f"Week of {datetime.now().strftime('%b %d, %Y')}"
    output_path = args.output or f"openclaw_weekly_{datetime.now().strftime('%Y%m%d')}.md"

    print("=" * 60)
    print("  SkillMetricScraper v3 — ClawHub Real API Edition")
    print(f"  {week_label}")
    print("=" * 60)

    # Step 1: Initialise DB
    storage.init_db()

    # Step 2: Discover
    print(f"\n[1/5] Discovering ClawHub skills (sort={args.sort})...")
    skills = discovery.discover(
        clawhub_url=env["clawhub_url"],
        sort=args.sort,
        mock=args.mock,
        max_pages=args.max_pages,
    )
    if not skills:
        print("[ERROR] No skills discovered. Check network or use --mock for offline dev.")
        sys.exit(1)

    # Step 3: Upsert skills + record snapshot
    print(f"\n[2/5] Saving snapshot of {len(skills)} skills to DB...")
    storage.upsert_skills(skills)
    storage.record_snapshot(skills)

    if args.snapshot_only:
        dates = storage.distinct_snapshot_dates()
        print(f"\n[DONE] Snapshot recorded ({len(skills)} skills).")
        print(f"       Total snapshots in DB: {storage.snapshot_count()} rows across {len(dates)} date(s).")
        print(f"       Run without --snapshot-only to generate scripts.")
        print(f"       Tip: run daily with --snapshot-only to build velocity history.")
        return

    # Step 4: Rank by velocity (two-track)
    print(f"\n[3/5] Ranking by {args.days}-day velocity (movers + rockets)...")
    top_movers, top_rockets = ranker.rank(skills, db_days=args.days, top_n=args.top)

    all_top = top_movers + top_rockets

    # Step 5: Harvest content
    print(f"\n[4/5] Harvesting content for {len(all_top)} skills...")
    harvested = harvester.harvest(all_top, github_token=env["github_token"])

    movers_h = harvested[:len(top_movers)]
    rockets_h = harvested[len(top_movers):]

    # Step 6: Generate scripts
    if not env["anthropic_key"]:
        print("[WARN] No ANTHROPIC_API_KEY — skipping script generation")
        movers_s = [{**s, "script": "[No API key]"} for s in movers_h]
        rockets_s = [{**s, "script": "[No API key]"} for s in rockets_h]
    else:
        print(f"\n[5/5] Generating YouTube scripts via {args.model}...")
        all_scripted = script_generator.generate_scripts(harvested, env["anthropic_key"], model=args.model)
        movers_s = all_scripted[:len(top_movers)]
        rockets_s = all_scripted[len(top_movers):]

    # Render output: markdown report
    markdown = script_generator.render_markdown(movers_s, rockets_s, week_label=week_label)
    Path(output_path).write_text(markdown, encoding="utf-8")

    # Render output: voice-ready video script
    script_path = output_path.replace(".md", "_script.txt")
    video_script = script_generator.render_video_script(
        movers_s, rockets_s,
        episode_num=args.episode,
        week_label=week_label,
    )
    Path(script_path).write_text(video_script, encoding="utf-8")

    snap_count = storage.snapshot_count()
    dates = storage.distinct_snapshot_dates()
    total = len(movers_s) + len(rockets_s)
    print(f"\n[DONE] Report: {output_path}")
    print(f"       Script: {script_path}")
    print(f"       {len(movers_s)} movers + {len(rockets_s)} rockets | DB: {snap_count} rows across {len(dates)} date(s)")


if __name__ == "__main__":
    main()
