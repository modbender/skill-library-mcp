#!/usr/bin/env python3
"""
XQueue Setup — interactive setup for the file-based X post scheduler.
Creates folder structure, config, and explains the system.
"""

import json
import os
import sys

DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
DEFAULT_TIMES = ["9am", "12pm", "5pm"]
OPTIMAL_TIMES = {
    1: ["10am"],
    2: ["9am", "5pm"],
    3: ["9am", "12pm", "5pm"],
    4: ["8am", "11am", "2pm", "6pm"],
    5: ["8am", "10am", "12pm", "3pm", "6pm"],
}


def ask(prompt, default=None):
    suffix = f" [{default}]" if default else ""
    val = input(f"{prompt}{suffix}: ").strip()
    return val if val else default


def ask_yn(prompt, default="y"):
    val = ask(prompt, default).lower()
    return val in ("y", "yes")


def main():
    print("=" * 50)
    print("  XQueue Setup")
    print("  File-based X/Twitter post scheduler")
    print("=" * 50)
    print()
    print("How it works:")
    print("  - You get a folder for each day of the week")
    print("  - Inside each day, subfolders for each posting time")
    print("  - Drop a .md file in a time folder = scheduled tweet")
    print("  - A cron job posts the content and removes the file")
    print("  - The schedule cycles weekly (every Monday 9am, etc.)")
    print()

    # Base directory
    base = ask("Where should the xqueue folder live?", os.getcwd())
    queue_dir = os.path.join(base, "xqueue")

    # Timezone
    tz = ask("Your timezone?", "America/Chicago")

    # Posting frequency
    print()
    print("How many times per day do you want to post?")
    print("  (We'll create that many time slots per day)")
    count = int(ask("Posts per day", "3"))
    count = max(1, min(count, 5))

    # Times
    print()
    suggested = OPTIMAL_TIMES.get(count, DEFAULT_TIMES[:count])
    print(f"Suggested times for {count}x/day: {', '.join(suggested)}")
    custom = ask("Use these times? Or enter your own (comma-separated)", "y")
    if custom.lower() in ("y", "yes"):
        times = suggested
    else:
        times = [t.strip() for t in custom.split(",")]

    # Thread separator
    print()
    separator = ask("Thread separator (put this between tweets in a thread file)", "---")

    # Delete after post
    print()
    print("After posting, should the file be deleted?")
    print("  YES (recommended): each tweet posts once, folder stays clean")
    print("  NO: files stay, but will post AGAIN next week on the same day/time")
    delete_after = ask_yn("Delete after posting?", "y")

    # Communities
    print()
    print("X communities to post to (optional).")
    print("  When you start a tweet with 'Post to Build in Public:' it posts there.")
    print()
    communities = {}
    import re
    while True:
        print("  Add a community (enter to skip/finish):")
        print("    Paste the community URL or ID (e.g. x.com/i/communities/123456 or just 123456)")
        entry = ask("Community", "")
        if not entry:
            break
        entry = entry.strip()
        # Extract numeric ID from URL or raw number
        url_match = re.search(r'communities/(\d+)', entry)
        if url_match:
            cid = url_match.group(1)
        elif entry.isdigit():
            cid = entry
        else:
            print(f"  ✗ Couldn't find a community ID in '{entry}'.")
            print(f"    Go to your community on X and copy the URL — it looks like:")
            print(f"    x.com/i/communities/1234567890")
            continue
        name = ask("  Display name for this community (used in tweets like 'Post to NAME:')", f"community-{cid}")
        communities[name] = cid
        print(f"  ✓ Added '{name}' (ID: {cid})")

    # Dry run
    print()
    dry_run = ask_yn("Start in dry-run mode? (logs what WOULD post, doesn't actually post)", "n")

    # Build config
    config = {
        "timezone": tz,
        "separator": separator,
        "deleteAfterPost": delete_after,
        "communities": communities,
        "logFile": "xqueue/posted.log",
        "dryRun": dry_run,
    }

    # Create folders
    print()
    print(f"Creating xqueue at: {queue_dir}")
    os.makedirs(queue_dir, exist_ok=True)
    for day in DAYS:
        for t in times:
            path = os.path.join(queue_dir, day, t)
            os.makedirs(path, exist_ok=True)

    # Write config
    config_path = os.path.join(queue_dir, "config.json")
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    # Write a sample tweet
    sample_path = os.path.join(queue_dir, DAYS[1], times[0], "sample-tweet.md")
    with open(sample_path, "w") as f:
        f.write("This is a sample tweet. Delete this file or edit it!\n")

    print()
    print("✅ XQueue is set up!")
    print()
    print("Your folder structure:")
    for day in DAYS:
        slots = "  ".join(times)
        print(f"  {day}/  →  {slots}")
    print()
    print(f"Config: {config_path}")
    print(f"Sample tweet: {sample_path}")
    print()
    print("Next steps:")
    print("  1. Add X community IDs to config.json (if using communities)")
    print("  2. Set up the cron job (xqueue-post.py runs every 15 min)")
    print("  3. Drop .md files into time folders to schedule tweets!")
    print()
    if delete_after:
        print("📌 deleteAfterPost is ON — files are removed after posting.")
    else:
        print("⚠️  deleteAfterPost is OFF — files will post again next week!")


if __name__ == "__main__":
    main()
