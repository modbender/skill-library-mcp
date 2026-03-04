---
name: x-twitter
description: >
  Personal X (Twitter) analytics — timeline engagement, mentions, follower tracking,
  read any tweet/thread, bookmarks, and combined briefings via X API v2.
  Cost-optimized with persistent local store and daily budget guards.
metadata: {"openclaw":{"emoji":"𝕏","requires":{"bins":["uv"]}}}
---

# X (Twitter) Personal Analytics

Monitor your X account — posts, engagement, mentions, followers. Read any tweet. Built for daily briefings and accountability.

## Triggers

Use this skill when the user asks about:
- Their X / Twitter posts, timeline, or engagement
- Mentions, replies, or who's talking about them on X
- Follower count, profile stats, follower growth
- "What's happening on my X?" / "How are my posts doing?"
- "Check my Twitter mentions" / "Any new replies?"
- Morning briefing / daily social media summary
- "Am I on X too much?" / accountability check
- Reading a specific tweet or thread (user sends a tweet URL)
- "What did @someone say?" / reading other people's tweets
- Bookmarking or saving tweets for later
- X/Twitter analytics or performance

## Prerequisites

Run setup first (imports credentials from `~/.openclaw/.env` or prompts interactively):
```bash
uv run scripts/x_setup.py
```

## Commands

### Briefing — combined morning summary

```bash
# Full briefing: your posts + mentions + profile (last 24h, ~$0.02)
uv run scripts/x_briefing.py

# Custom lookback period
uv run scripts/x_briefing.py --hours 48

# Preview cost
uv run scripts/x_briefing.py --dry-run
```

### Timeline — your posts + engagement

```bash
# Recent posts with engagement metrics
uv run scripts/x_timeline.py recent

# Last 5 posts
uv run scripts/x_timeline.py recent --max 5

# Posts from last 24 hours
uv run scripts/x_timeline.py recent --hours 24

# Top posts by engagement (from local store, no API call)
uv run scripts/x_timeline.py top --days 7

# Refresh metrics for a specific tweet
uv run scripts/x_timeline.py refresh TWEET_ID

# Accountability check — are they on X right now?
uv run scripts/x_timeline.py activity
```

### Mentions — who's talking to/about you

```bash
# Recent mentions
uv run scripts/x_mentions.py recent

# Mentions from last 24 hours
uv run scripts/x_mentions.py recent --hours 24

# Mentions with context (shows what they replied to — costs extra)
uv run scripts/x_mentions.py recent --context
```

### Read — fetch any tweet or thread

```bash
# Read a tweet by URL
uv run scripts/x_read.py https://x.com/user/status/123456

# Read by bare ID
uv run scripts/x_read.py 123456

# Fetch full thread
uv run scripts/x_read.py 123456 --thread

# Preview cost
uv run scripts/x_read.py --dry-run https://x.com/user/status/123456
```

### Bookmarks — save and manage

```bash
# List your bookmarks
uv run scripts/x_bookmarks.py list

# Bookmark a post
uv run scripts/x_bookmarks.py add TWEET_ID

# Remove a bookmark
uv run scripts/x_bookmarks.py remove TWEET_ID
```

### User Profile — stats + follower tracking

```bash
# Your profile stats
uv run scripts/x_user.py me

# Track follower changes over time
uv run scripts/x_user.py me --track

# Look up another user
uv run scripts/x_user.py lookup someuser
```

### Setup & Spend

```bash
# Validate credentials
uv run scripts/x_setup.py --check

# Show config (secrets redacted)
uv run scripts/x_setup.py --show

# Weekly spend summary
uv run scripts/x_setup.py --spend-report

# 30-day spend report
uv run scripts/x_setup.py --spend-report --days 30

# Set budget mode
uv run scripts/x_setup.py --budget-mode relaxed

# Print version
uv run scripts/x_setup.py --version
```

### Cost Control Flags (all scripts)

```bash
# Preview cost without making the API call
uv run scripts/x_timeline.py --dry-run recent

# Override budget guard
uv run scripts/x_timeline.py --force recent

# Skip all budget checks and warnings
uv run scripts/x_timeline.py --no-budget recent
```

## Workflows

### Morning Brief
```bash
uv run scripts/x_briefing.py
```
Single command replaces running timeline + mentions + user separately. Costs ~$0.02.

### Accountability Check
```bash
uv run scripts/x_timeline.py activity
```
Use this when the user should be working — it shows when they last posted and how active they've been. Nudge them if they're spending too much time on X.

### Weekly Review
```bash
uv run scripts/x_timeline.py top --days 7
uv run scripts/x_user.py me --track
```

## Agent Guidelines — READ THIS BEFORE CALLING ANY COMMAND

**Every command costs real money.** The X API charges per request. Follow these rules to minimize spend:

### Rules

1. **Never call the same command twice in one conversation** unless the user explicitly asks for fresh data. The scripts cache locally — if you already ran `recent` this session, just reference those results.
2. **Prefer `top` over `recent` for repeat questions.** `top` reads from the local store for free ($0). `recent` hits the API ($0.005).
3. **Don't use `--context` on mentions by default.** It costs an extra $0.005 per reply thread it fetches. Only add it if the user specifically asks "what were they replying to?"
4. **Use `--max 5` for quick checks.** Default is 10-20. If the user just wants a summary, pull fewer.
5. **Use `--hours 24` for briefings.** Don't pull the full timeline when they just want "what happened today."
6. **Never run all scripts unprompted.** If the user asks "what's happening on my X?", use `x_briefing.py` instead of running 3 separate commands.
7. **For accountability checks, use `activity` only.** It's a single API call. Don't also pull mentions and profile — that triples the cost.
8. **`top` and `refresh` are your friends.** `top` is free (local data). `refresh TWEET_ID` updates just one tweet ($0.005) — use it when they ask "how's my last post doing?" instead of re-pulling the whole timeline.
9. **Watch the daily spend total.** Every command output shows "Today's spend: $X.XXX". If it's approaching the budget limit, tell the user before making more calls.
10. **Never loop or retry on your own.** If a command fails (402, rate limit, etc.), report the error. Don't retry automatically.
11. **x_read.py caches tweets** — if the user asks about the same tweet again, it's already in the local store. No need to re-fetch.
12. **Use x_briefing.py for morning briefings** instead of running timeline + mentions + user separately. It's cheaper ($0.02 vs $0.02 for 3 separate commands) and cleaner output.

### Cost Reference

| Action | Cost | When to use |
|--------|------|-------------|
| `x_briefing.py` | $0.02 | Morning briefing — one command does it all |
| `recent` | $0.005 | Once per briefing, or when user asks for new posts |
| `top` | **$0** | Anytime — serves from local store |
| `activity` | $0.005 | Accountability check, once per session max |
| `refresh ID` | $0.005 | User asks about a specific post's performance |
| `mentions recent` | $0.005 | Once per briefing, or user asks about replies |
| `mentions --context` | $0.005-0.03 | Only when user explicitly wants reply context |
| `x_read.py URL` | $0.005 | User sends a tweet URL or asks to read a post |
| `x_read.py --thread` | $0.005-0.01 | User asks for full thread |
| `x_bookmarks.py list` | $0.005 | User wants to see saved bookmarks |
| `x_bookmarks.py add/remove` | **$0** | Write actions are free |
| `user me` | $0.01 | Profile check, once per day is plenty |
| `user me --track` | $0.01 | Morning brief only — saves follower delta |
| `user lookup` | $0.01 | Only when user asks about another account |
| `--spend-report` | **$0** | Check spending anytime |
| `--dry-run` | **$0** | Preview cost before any command |

### Budget Modes

The user can set a budget enforcement mode via `x_setup.py --budget-mode`:
- **guarded** (default): Warn at 50/80/100%, block at limit
- **relaxed**: Warn at 50/80/100%, never block
- **unlimited**: No warnings, no blocks

### Budget Tiers

The user set a daily budget during setup. The scripts will warn and block when the limit is hit:
- **lite**: $0.03/day (~1 briefing)
- **standard**: $0.10/day (~3-5 checks)
- **intense**: $0.25/day (~10+ checks)

If blocked, tell the user: "Daily X API budget reached. Use --force to override, or wait until tomorrow."

### What NOT to do

- Don't run commands "just to have fresh data" — only fetch when the user needs it
- Don't use `--no-cache` unless debugging
- Don't call `user lookup` on multiple accounts in a loop
- Don't refresh every tweet's metrics — only refresh specific ones the user asks about
- Don't combine `recent` + `mentions` + `user` in one response — use `x_briefing.py` instead
