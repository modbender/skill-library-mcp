---
name: hacker-news-poster
description: Post, comment, and interact on Hacker News. Use when the user asks to submit a Show HN, post a story, comment on an HN thread, edit a comment, or update an HN profile. Requires HN_USERNAME and HN_PASSWORD environment variables. Persists session cookies to ~/.hn_cookies.txt (configurable via HN_COOKIE_FILE env var).
---

# Hacker News Poster

Submit stories, comment on threads, edit comments, and update profiles on Hacker News.

## Setup

### Required Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `HN_USERNAME` | Yes | Hacker News username |
| `HN_PASSWORD` | Yes | Hacker News password |
| `HN_COOKIE_FILE` | No | Cookie storage path (defaults to `~/.hn_cookies.txt`) |

### Security Note

Session cookies are stored in plaintext at `HN_COOKIE_FILE` (or `~/.hn_cookies.txt`). These are standard HN session tokens. Delete the file to clear the session.

## CLI

All commands go through `scripts/hn.py`. Always `login` first per session.

```bash
# login (reads HN_USERNAME/HN_PASSWORD from env)
python3 scripts/hn.py login

# submit a link post
python3 scripts/hn.py submit --title "Show HN: My Tool" --url "https://example.com"

# submit a text post (Ask HN, etc.)
python3 scripts/hn.py submit --title "Ask HN: Question?" --text "body text here"

# comment on a story or reply to a comment
python3 scripts/hn.py comment --parent 12345678 --text "your comment"

# edit a comment (only within HN's edit window)
python3 scripts/hn.py edit --id 12345678 --text "updated comment"

# update profile about section
python3 scripts/hn.py profile --username youruser --about "your bio"
```

All commands output JSON on success (`{"ok": true, ...}`) and print errors to stderr.

## Notes

- HN rate-limits submissions and comments. If you get a rate limit error, wait a few minutes.
- Comments can only be edited within ~2 hours of posting.
- The `submit` command returns the new item id and url on success.
- Session cookies are stored in `~/.hn_cookies.txt` to avoid re-authenticating on every command. Delete this file to clear the session.
- For reading HN (search, top stories, comments), use the existing `hacker-news` skill or the HN API directly. This skill is write-only.

## Combining with the read-only HN skill

1. use the `hacker-news` skill to browse/search stories and find interesting threads
2. use this skill to login and post/comment
