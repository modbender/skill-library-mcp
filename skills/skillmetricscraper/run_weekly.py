"""
run_weekly.py — One-command weekly report generation (v5)

Runs the full pipeline in order:
  0. bridge: Copy container DB (has daily snapshot history) to host
  1. x_capture: Scan X/Twitter for OpenClaw signals (append to existing)
  2. discovery: Fetch all skills from ClawHub API
  3. storage: Record snapshot to SQLite time-series DB
  4. ranker: Two-track ranking (Movers + Rockets)
  5. harvester: Fetch docs for top skills
  6. script_generator: Generate YouTube pitches via LLM

Usage:
    python run_weekly.py                     # Full run, top 10, all pages
    python run_weekly.py --top 5             # Top 5 only
    python run_weekly.py --skip-x            # Skip X/Twitter capture
    python run_weekly.py --snapshot-only     # Just snapshot, no scripts
    python run_weekly.py --max-pages 3       # Limit API pages (testing)
    python run_weekly.py --no-bridge         # Skip container DB copy

For daily cron (snapshot accumulation only):
    python run_weekly.py --snapshot-only --skip-x
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

CONTAINER_NAME = "openclaw-gateway-secure"
CONTAINER_DB = "/home/node/.openclaw/workspace/data/skills-weekly/metrics.db"


def _bridge_container_db():
    """Copy container's metrics.db (with daily snapshot history) to host."""
    host_db = Path(__file__).parent / "data" / "metrics.db"
    host_db.parent.mkdir(parents=True, exist_ok=True)

    # Check container health
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", f"name={CONTAINER_NAME}",
             "--format", "{{.Status}}"],
            capture_output=True, text=True, timeout=10,
        )
        if "(healthy)" not in result.stdout:
            print(f"  [WARN] Container {CONTAINER_NAME} not healthy, skipping DB bridge")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("  [WARN] Docker not available, skipping DB bridge")
        return False

    # Backup existing host DB
    if host_db.exists():
        backup = host_db.with_suffix(".db.bak")
        shutil.copy2(host_db, backup)
        print(f"  Host DB backed up to {backup.name}")

    # Copy container DB to host
    try:
        result = subprocess.run(
            ["docker", "cp", f"{CONTAINER_NAME}:{CONTAINER_DB}", str(host_db)],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            print(f"  [WARN] docker cp failed: {result.stderr.strip()}")
            # Restore backup
            backup = host_db.with_suffix(".db.bak")
            if backup.exists():
                shutil.copy2(backup, host_db)
                print("  Restored backup")
            return False
        print(f"  Container DB copied to host ({host_db.stat().st_size // 1024}KB)")
        return True
    except subprocess.TimeoutExpired:
        print("  [WARN] docker cp timed out")
        return False


def main():
    parser = argparse.ArgumentParser(description="Full weekly pipeline runner")
    parser.add_argument("--top", type=int, default=10)
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--output", type=str, default=None)
    parser.add_argument("--week", type=str, default=None)
    parser.add_argument("--model", type=str, default="claude-haiku-4-5-20251001")
    parser.add_argument("--sort", type=str, default="downloads")
    parser.add_argument("--max-pages", type=int, default=0)
    parser.add_argument("--snapshot-only", action="store_true")
    parser.add_argument("--skip-x", action="store_true", help="Skip X/Twitter capture")
    parser.add_argument("--mock", action="store_true")
    parser.add_argument("--no-bridge", action="store_true", help="Skip container DB copy")
    parser.add_argument("--episode", type=int, default=1, help="Episode number for video script")
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    week_label = args.week or f"Week of {now.strftime('%b %d, %Y')}"

    print("=" * 60)
    print("  OpenClaw Skills Weekly — Full Pipeline (v4)")
    print(f"  {week_label}")
    print("=" * 60)

    # Step 1: Multi-source signal capture (X + Reddit + HN)
    if not args.skip_x and not args.snapshot_only:
        print("\n" + "=" * 40)
        print("  PHASE 1: Multi-Source Signal Capture")
        print("=" * 40)

        # X/Twitter
        try:
            import x_capture
            date_from = (now - timedelta(days=args.days)).strftime("%Y-%m-%d")
            date_to = now.strftime("%Y-%m-%d")
            x_capture.capture(date_from=date_from, date_to=date_to, append=True)
        except Exception as e:
            print(f"[WARN] X capture failed (non-fatal): {e}")

        # Reddit + Hacker News
        try:
            import reddit_capture
            reddit_capture.capture(days=args.days)
        except Exception as e:
            print(f"[WARN] Reddit/HN capture failed (non-fatal): {e}")

    # Step 0: Bridge container DB (get real daily snapshot history)
    if not args.no_bridge:
        print("\n" + "=" * 40)
        print("  PHASE 0: Container DB Bridge")
        print("=" * 40)
        _bridge_container_db()

    # Rollup old hourly data (keep last 30 days granular, compact the rest)
    try:
        import storage as _storage_rollup
        _storage_rollup.init_db()
        rolled = _storage_rollup.rollup_hourly()
        if rolled > 0:
            print(f"  [ROLLUP] Compacted {rolled} old hourly rows")
    except Exception as e:
        print(f"  [WARN] Rollup failed (non-fatal): {e}")

    # OpenClaw project metadata snapshot (GitHub repo tracking)
    if not args.snapshot_only:
        try:
            import project_tracker
            print("\n  [PROJECT] Capturing OpenClaw ecosystem metadata...")
            project_tracker.capture()
        except Exception as e:
            print(f"  [WARN] Project tracker failed (non-fatal): {e}")

    # Step 2-6: ClawHub pipeline
    print("\n" + "=" * 40)
    print("  PHASE 2: ClawHub Data Pipeline")
    print("=" * 40)

    import discovery
    import storage
    import ranker
    import harvester
    import script_generator

    env = {
        "github_token": os.getenv("GITHUB_TOKEN", ""),
        "anthropic_key": os.getenv("ANTHROPIC_API_KEY", ""),
        "clawhub_url": os.getenv("CLAWHUB_BASE_URL", ""),
    }

    storage.init_db()

    print(f"\n[1/5] Discovering ClawHub skills (sort={args.sort})...")
    skills = discovery.discover(
        clawhub_url=env["clawhub_url"],
        sort=args.sort,
        mock=args.mock,
        max_pages=args.max_pages,
    )
    if not skills:
        print("[ERROR] No skills discovered.")
        sys.exit(1)

    print(f"\n[2/5] Saving snapshot of {len(skills)} skills to DB...")
    storage.upsert_skills(skills)
    storage.record_snapshot(skills)

    if args.snapshot_only:
        dates = storage.distinct_snapshot_dates()
        print(f"\n[DONE] Snapshot recorded ({len(skills)} skills).")
        print(f"       DB: {storage.snapshot_count()} rows across {len(dates)} date(s).")
        return

    print(f"\n[3/5] Ranking by {args.days}-day velocity (two-track: movers + rockets)...")
    top_movers, top_rockets = ranker.rank(skills, db_days=args.days, top_n=args.top)

    # Combine for harvesting and script gen
    all_top = top_movers + top_rockets

    print(f"\n[4/5] Harvesting content for {len(all_top)} skills...")
    harvested = harvester.harvest(all_top, github_token=env["github_token"])

    # Split back into movers and rockets after harvest
    movers_h = harvested[:len(top_movers)]
    rockets_h = harvested[len(top_movers):]

    if not env["anthropic_key"]:
        print("[WARN] No ANTHROPIC_API_KEY — skipping script generation")
        movers_s = [{**s, "script": "[No API key]"} for s in movers_h]
        rockets_s = [{**s, "script": "[No API key]"} for s in rockets_h]
    else:
        print(f"\n[5/5] Generating YouTube scripts via {args.model}...")
        all_scripted = script_generator.generate_scripts(harvested, env["anthropic_key"], model=args.model)
        movers_s = all_scripted[:len(top_movers)]
        rockets_s = all_scripted[len(top_movers):]

    # Time-series enrichment for report + JSON
    print("\n[6/6] Building time-series data...")

    # Per-skill history (sparkline data for each top skill)
    for skill in movers_s + rockets_s:
        slug = skill.get("slug", "")
        if slug:
            skill["history"] = storage.get_skill_history(slug, days=args.days)

    # Catalog-level aggregates (total skills, downloads, installs over time)
    catalog_history = storage.get_catalog_history(days=args.days)

    # OpenClaw project metadata (stars, PRs, releases)
    project_history = storage.get_project_history(days=args.days)

    # Output 1: Markdown report (data-rich, for reference)
    output_path = args.output or f"openclaw_weekly_{now.strftime('%Y%m%d')}.md"
    markdown = script_generator.render_markdown(
        movers_s, rockets_s, week_label=week_label,
        catalog_history=catalog_history, project_history=project_history,
    )
    Path(output_path).write_text(markdown, encoding="utf-8")

    # Output 2: Voice-ready video script (GitHubAwesome style)
    script_path = output_path.replace(".md", "_script.txt")
    video_script = script_generator.render_video_script(
        movers_s, rockets_s,
        episode_num=args.episode,
        week_label=week_label,
    )
    Path(script_path).write_text(video_script, encoding="utf-8")

    # Output 3: Structured JSON for Remotion video pipeline
    json_path = output_path.replace(".md", ".json")
    json_data = {
        "episode": args.episode,
        "week_label": week_label,
        "generated_at": now.isoformat(),
        "movers": movers_s,
        "rockets": rockets_s,
        "catalog": catalog_history,
        "openclaw_project": project_history,
    }
    Path(json_path).write_text(json.dumps(json_data, indent=2, default=str), encoding="utf-8")

    dates = storage.distinct_snapshot_dates()
    total = len(movers_s) + len(rockets_s)
    print(f"\n{'=' * 60}")
    print(f"  DONE:")
    print(f"    Report: {output_path}")
    print(f"    Script: {script_path}")
    print(f"    JSON:   {json_path}")
    print(f"  {len(movers_s)} movers + {len(rockets_s)} rockets | DB: {storage.snapshot_count()} rows across {len(dates)} date(s)")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
