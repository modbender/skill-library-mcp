# AGENTS.md — X (Twitter) Skill (Machine-Readable Reference)

This file is for AI agents (Claude Code, OpenClaw, Cursor, Copilot, etc.). For human docs, see [README.md](README.md). For setup instructions, see [SETUP.md](SETUP.md).

## Setup

Credentials directory: `~/.openclaw/skills-config/x-twitter/`
Required files: `config.json` (created by setup)

```bash
uv run scripts/x_setup.py  # Interactive setup — imports keys, validates, picks budget tier
```

## Commands

All scripts use `uv run` (auto-installs dependencies). Run from the skill directory. All commands support `--dry-run` to preview cost and `--no-budget` to skip budget checks.

### x_briefing.py — Combined Morning Briefing

```bash
# Full briefing: posts + mentions + profile (~$0.020)
uv run scripts/x_briefing.py

# Custom lookback period
uv run scripts/x_briefing.py --hours 48

# Preview cost
uv run scripts/x_briefing.py --dry-run
```

### x_timeline.py — Your Posts + Engagement

```bash
# Recent posts with engagement metrics (~$0.005)
uv run scripts/x_timeline.py recent
uv run scripts/x_timeline.py recent --max 5
uv run scripts/x_timeline.py recent --hours 24

# Top posts by engagement — FREE, reads from local store
uv run scripts/x_timeline.py top --days 7 --max 10

# Refresh one tweet's metrics (~$0.005)
uv run scripts/x_timeline.py refresh <TWEET_ID>

# Accountability check — how active on X? (~$0.005)
uv run scripts/x_timeline.py activity

# Preview cost without calling API
uv run scripts/x_timeline.py --dry-run recent
```

### x_mentions.py — Mentions & Replies

```bash
# Recent mentions (~$0.005)
uv run scripts/x_mentions.py recent
uv run scripts/x_mentions.py recent --max 10 --hours 24

# Mentions with parent tweet context (~$0.005-0.030) [EXPENSIVE]
uv run scripts/x_mentions.py recent --context
```

### x_read.py — Read Any Tweet or Thread

```bash
# Read a tweet by URL or ID (~$0.005)
uv run scripts/x_read.py https://x.com/user/status/123456
uv run scripts/x_read.py 123456

# Fetch full thread (~$0.005-0.010)
uv run scripts/x_read.py 123456 --thread

# Preview cost
uv run scripts/x_read.py --dry-run https://x.com/user/status/123456
```

### x_bookmarks.py — Bookmarks

```bash
# List bookmarks (~$0.005)
uv run scripts/x_bookmarks.py list
uv run scripts/x_bookmarks.py list --max 10

# Bookmark a post ($0 — free write action)
uv run scripts/x_bookmarks.py add TWEET_ID

# Remove a bookmark ($0 — free write action)
uv run scripts/x_bookmarks.py remove TWEET_ID
```

### x_user.py — Profile & Follower Tracking

```bash
# Your profile stats (~$0.010)
uv run scripts/x_user.py me

# Profile + save follower delta for tracking (~$0.010)
uv run scripts/x_user.py me --track

# Look up another user (~$0.010)
uv run scripts/x_user.py lookup <USERNAME>
```

### x_setup.py — Config & Spend

```bash
# Validate credentials
uv run scripts/x_setup.py --check

# Show config (secrets redacted)
uv run scripts/x_setup.py --show

# Weekly spend summary (FREE)
uv run scripts/x_setup.py --spend-report

# 30-day spend report
uv run scripts/x_setup.py --spend-report --days 30

# Set budget mode
uv run scripts/x_setup.py --budget-mode guarded|relaxed|unlimited

# Print version
uv run scripts/x_setup.py --version

# Reconfigure (change tier, re-enter keys)
uv run scripts/x_setup.py --reconfig
```

## When to Use What

| Task | Command | Cost |
|------|---------|------|
| Morning briefing | `x_briefing.py` | $0.020 |
| "How are my posts doing?" | `x_timeline.py recent --max 5` | $0.005 |
| "What was my best post this week?" | `x_timeline.py top --days 7` | **FREE** |
| "Any new replies or mentions?" | `x_mentions.py recent` | $0.005 |
| "Read this tweet" (user sends URL) | `x_read.py <URL>` | $0.005 |
| "Show me the full thread" | `x_read.py <URL> --thread` | $0.005-0.010 |
| "Save this tweet" | `x_bookmarks.py add <ID>` | **FREE** |
| "Show my bookmarks" | `x_bookmarks.py list` | $0.005 |
| "How many followers do I have?" | `x_user.py me` | $0.010 |
| "Am I on X too much?" | `x_timeline.py activity` | $0.005 |
| "How's that specific tweet doing?" | `x_timeline.py refresh <ID>` | $0.005 |
| "Look up @someone" | `x_user.py lookup someone` | $0.010 |
| "How much have I spent on API?" | `x_setup.py --spend-report` | **FREE** |
| "What would this cost?" | any command `--dry-run` | **FREE** |

## Cost Discipline — CRITICAL

Every command costs real money. Follow these rules:

1. **Never call the same command twice in one conversation** — results are cached locally
2. **Prefer `top` over `recent`** — `top` is free (local store), `recent` hits the API
3. **Don't use `--context` on mentions by default** — costs extra per reply thread
4. **Use `--max 5` for quick checks** — don't pull 20 when 5 suffices
5. **Use `--hours 24` for briefings** — don't pull the full timeline
6. **Use `x_briefing.py` for morning briefings** — not 3 separate commands
7. **Use `--dry-run` when uncertain** — shows cost without spending
8. **Watch budget warnings** — scripts warn at 50%, 80%, and 100% of daily budget
9. **Never loop or retry** — if a command fails, report the error
10. **x_read.py caches tweets** — repeated reads of the same tweet are free from local store

## Budget Modes

Configurable via `x_setup.py --budget-mode`:
- **guarded** (default): Warn at 50/80/100%, block at limit
- **relaxed**: Warn only, never block
- **unlimited**: No warnings, no blocks

## Budget Warnings

Scripts automatically warn at these thresholds (in guarded/relaxed mode):
- **50%**: `[i] Budget note: $0.050 / $0.10 (50%) used today`
- **80%**: `[!] Budget warning: $0.080 / $0.10 (80%) — approaching limit`
- **100%**: `[!] BUDGET EXCEEDED` — script blocks in guarded mode (use `--force` to override)

When blocked, tell the user: "Daily X API budget reached. Use --force to override, or wait until tomorrow."

## Output Formats

- All output is plain text to stdout
- Engagement metrics: `Impressions: 1,234 | Likes: 56 | RTs: 12 | Replies: 3`
- Cost tracking: `Est. API cost: ~$0.005 (1 tweet read)` + `Today's spend: $0.025`
- Expensive commands flagged: `[$$$ EXPENSIVE]`
- Budget warnings: `[!] Budget warning: ...` or `[i] Budget note: ...`
- Tweet links: `https://x.com/handle/status/ID`
- High-follower mentions flagged: `[HIGH-PROFILE]` (>10K followers)

## Error States

- `No config found` → Run `uv run scripts/x_setup.py`
- `401 Unauthorized` → Invalid API keys, re-run setup
- `402 Payment Required` → No API credits, load at developer.x.com
- `403 Forbidden` → App permissions wrong, check developer portal
- `Daily budget exceeded` → At limit, use `--force` or wait
- `Rate limited` → Too many calls, wait 15 minutes

## Data Persistence

Config and data live at `~/.openclaw/skills-config/x-twitter/`:
- `config.json` — credentials, budget tier, budget mode, follower history
- `data/tweets.json` — persistent tweet store (never re-fetched)
- `data/mentions.json` — persistent mention store
- `data/bookmarks.json` — persistent bookmark store
- `data/usage.json` — daily API cost tracking by date
