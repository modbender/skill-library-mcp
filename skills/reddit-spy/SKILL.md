---
name: reddit-spy
description: Stealth Reddit intelligence -- browse, read, and analyze any subreddit without getting blocked. Multi-layer fallback (OAuth API -> Stealth HTTP -> Browser Stealth -> PullPush archive).
---

# Reddit Spy -- Stealth Subreddit Intelligence

Browse any target subreddit, read full posts, analyze strategies, and extract competitive intelligence -- all without getting blocked by Reddit.

**Entry point:**

```bash
python3 /root/.openclaw/skills/reddit-spy/scripts/reddit_spy.py <command> [options]
```

All commands output JSON to stdout. Logs go to stderr.

---

## Setup

**Tor (primary, already running):**
Tor provides real-time Reddit access from any IP. It's running on this VPS as a systemd service.

```bash
# Verify Tor is running
systemctl status tor@default

# If stopped, start it
systemctl start tor@default
```

**Optional: Reddit OAuth (even more reliable):**
If you have Reddit API access, set these env vars for 60 req/min:

```bash
export REDDIT_CLIENT_ID="your-app-client-id"
export REDDIT_CLIENT_SECRET="your-app-secret"
export REDDIT_USERNAME="your-reddit-username"
export REDDIT_PASSWORD="your-reddit-password"
```

**Optional: Proxy:**
```bash
export REDDIT_PROXY_URL="http://user:pass@proxy:port"
```

---

## Fetching Layers (Cascade Order)

| Layer | Method | Speed | Data | Status |
|-------|--------|-------|------|--------|
| 1. OAuth API | Reddit API v2 | Fast | Full real-time | Optional (needs API key) |
| 2. **Tor** | SOCKS5 via Tor exit nodes | Fast | **Full real-time** | **ACTIVE -- primary layer** |
| 3. Stealth HTTP | old.reddit.com direct | Fast | Full real-time | Blocked on VPS IPs |
| 4. Browser Stealth | Playwright | Slow | Full real-time | Blocked on VPS IPs |
| 5. PullPush | Archive API | Fast | Historical (may lag) | Always works |

Each command tries layers in order, falls through on failure. Layer health is cached for 1 hour. Tor auto-rotates circuits (new IP) on rate limits.

---

## Commands

### `spy` -- Comprehensive Subreddit Intelligence

Full scan: about info + top posts + strategy analysis in one pass.

```bash
python3 .../reddit_spy.py spy --subreddit IndieHackers --sort top --timeframe week --limit 25
```

| Param | Default | Values |
|-------|---------|--------|
| `--subreddit` | (required) | Subreddit name without r/ |
| `--sort` | top | hot, new, top, rising |
| `--timeframe` | week | hour, day, week, month, year, all |
| `--limit` | 25 | Max posts to analyze |

**Returns:** about metrics, posts fetched, content type breakdown, hook patterns, timing analysis, top 5 posts, actionable recommendations.

### `deep-read` -- Full Post Deep Dive

Read complete post body + all nested comments with statistics.

```bash
python3 .../reddit_spy.py deep-read --url "https://www.reddit.com/r/.../comments/..." --depth 8
```

**Returns:** full post, flattened comment list (author, body, score, depth, is_op), comment stats.

### `bulk-scan` -- Multi-Subreddit Sweep

Scan multiple subreddits in one run with comparison.

```bash
python3 .../reddit_spy.py bulk-scan --subreddits "IndieHackers,SaaS,Entrepreneur" --timeframe all --limit 20
```

**Returns:** per-subreddit strategy analysis + cross-sub comparison (ranked by subscribers and engagement).

### `strategy` -- Strategy Pattern Extraction

Extract what content strategies work best in a subreddit.

```bash
python3 .../reddit_spy.py strategy --subreddit SaaS --sort top --timeframe month --limit 50
```

**Returns:** content types ranked, hook patterns ranked, best posting hours/days, top 5 posts, recommendations.

### `search` -- Keyword Search

Search within a subreddit for specific topics.

```bash
python3 .../reddit_spy.py search --subreddit IndieHackers --query "growth strategy" --sort top --timeframe month
```

### `user-intel` -- User Profile Analysis

Analyze a Reddit user's posting patterns across subreddits.

```bash
python3 .../reddit_spy.py user-intel --username some_user --limit 25
```

**Returns:** total posts, subreddit distribution, content patterns, hook analysis.

### `health-check` -- Test Layers

Test which fetching layers are currently working.

```bash
python3 .../reddit_spy.py health-check --test-sub python
```

---

## Radar's Intelligence Workflow

### Step 1: Health check
```bash
python3 .../reddit_spy.py health-check
```
Verify which layers are operational before starting analysis.

### Step 2: Bulk scan targets
```bash
python3 .../reddit_spy.py bulk-scan --subreddits "IndieHackers,SaaS,Entrepreneur,Automation" --timeframe week --limit 25
```

### Step 3: Deep-dive top posts
Pick high-scoring posts from Step 2 and read full content + comments:
```bash
python3 .../reddit_spy.py deep-read --url "https://reddit.com/r/.../comments/..."
```

### Step 4: Profile top contributors
```bash
python3 .../reddit_spy.py user-intel --username top_poster
```

### Step 5: Search for topic gaps
```bash
python3 .../reddit_spy.py search --subreddit IndieHackers --query "automation" --sort top
```

---

## Strategy Analysis Output

The `spy`, `bulk-scan`, and `strategy` commands return:

- **content_types**: question, how-to, tip, showcase, list, discussion, link -- with avg score/comments per type
- **hook_patterns**: question, number, bracket, emotional, personal, neutral -- with engagement metrics
- **timing_by_hour**: UTC hours ranked by avg score
- **timing_by_day**: days of week ranked by avg score
- **top_5_posts**: highest scoring with title, score, and type classification
- **recommendations**: actionable insights (best type, hook, time, day)

## Safety & Limits

- **Read-only**: never posts, comments, votes, or interacts
- **Rate limited**: jittered 3-8s delays between requests
- **OAuth**: respects Reddit API 60 req/min limit
- **PullPush**: historical archive, data may lag weeks/months behind real-time
