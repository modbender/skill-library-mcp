---
name: twitter-agent-skill
description: "Cookie-based Twitter/X automation toolkit (timeline, notifications, posting, follow ops) for OpenClaw agents."
metadata:
  openclaw:
    emoji: "🐦"
    requires:
      bins: ["python", "git"]
---

# twitter-agent-skill

## Summary
Async Twitter/X client and scripts that rely on auth_token + ct0 cookies (no official API keys). Supports:
- Home timeline fetch + summary (`scripts/timeline_summary.py`).
- Notifications fetch + signal analysis (`scripts/fetch_notifications.py`, `scripts/analyze_signal.py`).
- Posting and follow automation via env-driven account labels (`scripts/post_custom_tweet.py`, `scripts/follow_account.py`).
- Full async client (`twitter_api/`) with modules for tweets, users, relationships, DMs, etc.

## Setup
1. `pip install -r requirements.txt` (Python 3.10+).
2. Copy `.env.example` → `.env` and fill cookies per account (auth_token + ct0 from logged-in sessions).
3. Run scripts from repo root, e.g.:
   ```
   python scripts/timeline_summary.py
   python scripts/post_custom_tweet.py account_a "hello"
   python scripts/follow_account.py thenfter07
   ```

## Notes
- Env variable names are generic (`ACCOUNT_A_AUTH_TOKEN`, etc.); rename as needed and adjust `ACCOUNT_ENV` dicts in the scripts.
- Respect Twitter/X ToS and do not spam.
- Designed for GanClaw social ops, but neutral enough for other agents to reuse.
