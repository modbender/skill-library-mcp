---
name: twitter-autopilot
description: Automate Twitter/X posting, engagement, and growth for OpenClaw AI agents. Use when setting up an agent's Twitter presence, posting tweets, running engagement crons, managing drafts, following accounts, or building a Twitter growth strategy. Handles OAuth setup, thread splitting, draft workflows, and engagement automation.
---

# Twitter Autopilot

End-to-end Twitter/X automation for AI agents running on OpenClaw.

## Requirements & Scope

### Credentials (all set as env vars)
| Variable | Required | Description |
|----------|----------|-------------|
| `TWITTER_API_KEY` | ✅ | OAuth 1.0a consumer key |
| `TWITTER_API_SECRET` | ✅ | OAuth 1.0a consumer secret |
| `TWITTER_ACCESS_TOKEN` | ✅ | OAuth 1.0a user token |
| `TWITTER_ACCESS_SECRET` | ✅ | OAuth 1.0a user secret |
| `TWITTER_BEARER_TOKEN` | Optional | OAuth 2.0 bearer (needed for reads/follows) |

### Dependencies
- `tweepy` (pip install)

### Files Read/Written
| Path | Access | Purpose |
|------|--------|---------|
| `twitter/MODE.md` | Read | Draft vs auto mode flag |
| `twitter/queue.md` | Read/Write | Approved tweets waiting to post |
| `twitter/drafts/pending.md` | Read/Write | Unapproved drafts |
| `twitter/posted-log.md` | Read/Write | Full history of posted tweets (duplicate check) |
| `twitter/logs/` | Write | Engagement and posting logs |

### Scope
- ⚠️ Posts tweets to Twitter/X (public, real-world impact)
- Reads/writes local draft and log files
- Can run autonomously via cron (check MODE.md to control)

## Setup

### 1. Get API Keys
1. Go to [developer.x.com](https://developer.x.com) → create a project + app
2. Set app permissions to **Read and Write**
3. Generate: API Key, API Secret, Access Token, Access Token Secret
4. Generate Bearer Token: `curl -u "API_KEY:API_SECRET" -d "grant_type=client_credentials" "https://api.twitter.com/oauth2/token"`

### 2. Set Environment Variables
```bash
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_SECRET=your_access_token_secret
TWITTER_BEARER_TOKEN=your_bearer_token
```

### 3. Install Dependency
```bash
pip install tweepy
```

## Usage

All commands via `scripts/tweet.py`:

```bash
# Post (auto-threads if >280 chars)
python tweet.py post "your tweet text here"

# Reply to a tweet
python tweet.py reply TWEET_ID "your reply"

# Quote tweet
python tweet.py quote TWEET_ID "your take"

# Retweet
python tweet.py retweet TWEET_ID

# Delete
python tweet.py delete TWEET_ID

# Follow / Unfollow
python tweet.py follow @username
python tweet.py unfollow @username

# Check mentions
python tweet.py mentions

# Account stats
python tweet.py me
```

### Long Tweets → Auto-Thread
Free API tier limits single tweets to 280 chars. The `post` command auto-splits at sentence boundaries into a thread when text exceeds 280 chars.

For manual threads, call `thread` from Python:
```python
from tweet import thread
thread(["Tweet 1", "Tweet 2", "Tweet 3"])
```

## Draft Workflow

For agents that need human approval before posting:

1. Create `twitter/MODE.md` with content `DRAFT` or `AUTO`
2. Create `twitter/drafts/pending.md` for queued drafts
3. In cron jobs, check MODE.md before posting:
   - DRAFT → append to pending.md, notify human
   - AUTO → post directly, log to `twitter/logs/`

## Gotchas

- **Free tier**: 280 char limit per tweet, rate limits on posting (~50/day write, reads limited)
- **401 on follows/reads**: You need a Bearer Token (OAuth 2.0), not just OAuth 1.0a keys
- **403 on long tweets**: Free tier rejects >280 chars — use auto-thread
- **Shell escaping**: Avoid passing tweets with quotes via shell args — use Python directly for complex text
- **Rate limits**: Add `time.sleep(1)` between batch operations (follows, thread posts)

## Strategy

See `references/content-strategy.md` for the full tweet writing playbook:
- X algorithm breakdown (engagement hierarchy, peak times, dwell time)
- 6 hook formulas with examples (bold, specific result, curiosity gap, story, pattern interrupt, question)
- 6 tweet formats (listicle, contrarian, before/after, framework, universal experience, fill-in-blank)
- Copywriting frameworks (PAS, BAB, AIDA)
- Thread structure template (7-8 tweet sweet spot)
- Growth tactics (30-day subtopic, reply strategy, 80/20 rule)
- AI agent-specific tips

See `references/strategy-templates.md` for content pillars, engagement playbooks, and cron schedule templates.

## Key Lessons (from real usage)

1. AIs that BUILD things get followers. AIs that post thoughts don't.
2. Engage with the AI agent community — they engage back.
3. High volume matters early (5-10+ posts/day including replies).
4. Self-deprecating humor > motivational quotes.
5. Draft mode for new accounts — one bad tweet can tank trust.
6. **ALWAYS check `twitter/posted-log.md` before posting** — crons can reword the same topic and create duplicates. Compare ideas, not just exact text.
7. Say your human's name (e.g. "Alex"), not "my human" — sounds more personal and real.
8. Log EVERY posted tweet to `twitter/posted-log.md` with full text, ID, date, and source.
