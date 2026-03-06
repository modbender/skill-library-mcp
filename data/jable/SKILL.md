---
name: jable
description: Fetch and rank Jable latest-update videos by likes within a recent time window (default 48h). Use when asked to pull Jable recent updates, sort by likes/popularity, and return top N links in a formatted list.
user-invocable: true
---

# Jable

Use this skill to produce "recent + top liked" lists from Jable quickly and repeatably.

## Install

From ClawHub:

```bash
clawhub install jable
```

(If you keep it in GitHub instead, clone/copy this folder into your OpenClaw workspace as `skills/jable/`.)

## Quick Start

Run:

```bash
python3 skills/jable/scripts/top_liked_recent.py --hours 48 --top 3 --pages 10
```

Parameters:
- `--hours`: recent window in hours (default `48`)
- `--top`: number of items to output (default `3`)
- `--pages`: number of `latest-updates` pages to scan for like counts (default `10`)

## Workflow

1. Read publish times from `https://jable.tv/rss/`.
2. Read like counts from `https://jable.tv/latest-updates/` pages.
3. Keep only videos inside the requested recent window.
4. Sort by likes descending.
5. Return top N with title, likes, and URL.

## Usage (in chat)

Ask for a list like:
- “Pull Jable latest updates and show top 5 by likes from last 24h”

## Output Format

Use this style when replying to users:

```text
1️⃣ <title>
❤️ <likes>
🔗 <url>

2️⃣ <title>
❤️ <likes>
🔗 <url>
```

## Notes

- If a recent RSS item does not appear in scanned latest pages, it may miss like data and be skipped.
- Increase `--pages` when needed.
