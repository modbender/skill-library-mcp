#!/usr/bin/env python3
"""ETH24 - Daily Ethereum digest pipeline.

crawl -> rank -> publish
"""

import argparse
import json
import os
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))


def run():
    parser = argparse.ArgumentParser(description="ETH24 daily digest")
    parser.add_argument(
        "--mode",
        choices=["tweet", "cli"],
        default="cli",
        help="Output mode: tweet (Typefully) or cli (stdout)",
    )
    args = parser.parse_args()

    today = datetime.now().strftime("%Y-%m-%d")
    out_dir = SCRIPT_DIR / "output" / today
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"ETH24 - {today}")
    print("=" * 40)

    # 1 - Crawl
    print("\n[1/3] Crawling sources...")
    from crawl import crawl_x, crawl_rss

    crawl_data = {
        "crawled_at": datetime.now(timezone.utc).isoformat(),
        "tweets": crawl_x(),
        "rss": crawl_rss(),
    }
    (out_dir / "crawled.json").write_text(json.dumps(crawl_data, indent=2))
    n_tweets = len(crawl_data["tweets"])
    n_rss = len(crawl_data["rss"])
    print(f"  {n_tweets} tweets, {n_rss} RSS articles")

    if n_tweets == 0:
        print(
            "ERROR: No tweets found. Check X_BEARER_TOKEN and/or XAI_API_KEY.",
            file=sys.stderr,
        )
        sys.exit(1)

    # 2 - Rank
    print("\n[2/3] Ranking and generating commentary...")
    from rank import rank

    ranked = rank(crawl_data)
    (out_dir / "ranked.json").write_text(
        json.dumps(ranked, indent=2, ensure_ascii=False)
    )
    stories = ranked.get("stories", [])
    print(f"  {len(stories)} stories ranked")

    if len(stories) == 0:
        print("\nNo stories met the quality bar today.")
        return

    # 3 - Output
    from publish import format_tweet, format_cli, create_draft

    if args.mode == "tweet":
        print("\n[3/3] Publishing tweet...")
        text = format_tweet(ranked)
        (out_dir / "thread.txt").write_text(text)

        social_set_id = os.environ.get("TYPEFULLY_SOCIAL_SET_ID")
        typefully_key = os.environ.get("TYPEFULLY_API_KEY")

        if social_set_id and typefully_key:
            posts = [{"text": text}]
            create_draft(social_set_id, posts)
            print("  Draft created on Typefully")
        else:
            print("  Typefully keys not set - saved tweet preview only", file=sys.stderr)

        print(f"  Tweet preview: {out_dir / 'thread.txt'}")
    else:
        print("\n[3/3] Output...")
        text = format_cli(ranked)
        (out_dir / "cli.txt").write_text(text)
        print()
        print(text)

    print("\n" + "=" * 40)
    print(f"Done. Output: {out_dir}/")


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception:
        traceback.print_exc()
        sys.exit(1)
