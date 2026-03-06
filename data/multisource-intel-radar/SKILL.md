---
name: multisource-intel-radar
description: Build and run a high-signal information radar for C-end founders and operators across YouTube, X/Twitter, Reddit, WeChat Official Accounts, and Xiaohongshu. Use when the user wants OPML/RSS ingestion, keyword-whitelist filtering (创业/AI/增长/金融), daily digests, noise reduction, and action-oriented summaries.
---

# Multi-Source Intel Radar

Create a founder-grade signal system: less junk, more decisions.

## Inputs
- OPML file (default: `/Users/rogeryang/Downloads/follow.opml`)
- Keyword whitelist (default: 创业, AI, 增长, 金融)
- Optional source lists for non-RSS channels (X list links, subreddit list, WeChat/XHS accounts)

## Output Contract
Always output:
1. **Top 3 must-read signals** (one-line why + one action + clickable source link)
2. **Top 5 watchlist items** (with source link)
3. **Dropped noise summary** (what got filtered and why)
4. **Filter transparency** (counts + rates: scanned -> matched -> shortlisted -> top3)
5. **Next experiment** (one concrete growth/ops move)

## Workflow

### Step 1) Ingest feed sources
- Parse OPML with `scripts/parse_opml.py`
- Generate normalized feed list: `assets/feeds.txt`

### Step 2) Fetch + filter
- Run `scripts/build_digest.py` with keyword whitelist
- Time window default: last 48h
- Keep only items that match whitelist in title/summary
- For Xiaohongshu: do browser search (not watchlist-dependent), using keyword combos like:
  - 创业 AI 增长
  - AI 产品 复盘
  - 增长运营 案例
  Then append top findings with profile/note links.

### Step 3) Score items
Use this weighted scoring:
- Relevance to whitelist (40%)
- Actionability in 7 days (30%)
- Novelty / non-obviousness (20%)
- Evidence density (10%)

### Step 4) Summarize for execution
For each selected item, provide:
- Core insight (1 sentence)
- Why it matters for current product
- Suggested action today (1 step)

## Source Coverage Notes
- YouTube/X/Reddit often available via RSSHub or platform feeds in OPML
- WeChat OA and Xiaohongshu are often not natively RSS; add via:
  - RSS bridge links (if available)
  - Manual watchlist files (`assets/wechat_watchlist.txt`, `assets/xhs_watchlist.txt`)
- If a source has no feed, include it in watchlist and mark as **manual scan required**

## Anti-Noise Rules
- Do not output generic motivational posts
- Drop repeated观点 without new evidence
- Prefer first-hand data / concrete case over opinion
- Keep digest under 10 items total

## Daily Cadence (recommended)
- 09:30: morning digest (strategic)
- 18:30: evening digest (tactical)

## Keyword Defaults
创业, AI, 增长, 金融

If user provides new keywords, merge and deduplicate.

## Files
- Parser: `scripts/parse_opml.py`
- Digest builder: `scripts/build_digest.py`
- Notes: `references/scoring-and-ops.md`