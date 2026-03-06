---
name: x-cli
description: Full-featured X/Twitter toolkit — read, search, post, interact, DMs, lists, polls, trends. Cookie auth, proxy support, no API keys needed.
homepage: https://github.com/ignsoftwarellc/x-cli
metadata: {"clawdbot":{"emoji":"𝕏","requires":{"python":">=3.10","pip":["twikit"]}}}
---

# x-cli

Full-featured X/Twitter toolkit for OpenClaw agents. Powered by [twikit](https://github.com/d60/twikit) — no API keys required, cookie-based auth.

## Setup

```bash
pip install -r scripts/requirements.txt
cp config.example.json config.json
# Set cookies_file path or credentials in config.json
```

## Commands

### Read (`x_read.py`)
```bash
python scripts/x_read.py tweet <url-or-id>              # Read a tweet
python scripts/x_read.py user <username> --count 5       # User's tweets
python scripts/x_read.py timeline --count 20             # Home timeline (Following)
python scripts/x_read.py foryou --count 20               # For You timeline
python scripts/x_read.py thread <url-or-id>              # Read thread
python scripts/x_read.py replies <url-or-id> --count 20  # Replies to a tweet
python scripts/x_read.py mentions --count 10             # Your mentions
python scripts/x_read.py highlights <username>           # User's highlights
python scripts/x_read.py search-user "query" --count 10  # Search users
```

### Search (`x_search.py`)
```bash
python scripts/x_search.py "query" --count 10
python scripts/x_search.py "from:zerohedge gold" --count 5
```

### Post (`x_post.py`) — confirm with user first!
```bash
python scripts/x_post.py tweet "text"                    # Post tweet
python scripts/x_post.py tweet "text" --media ID1 ID2    # With media
python scripts/x_post.py tweet "text" --dry-run           # Preview only
python scripts/x_post.py reply <id> "text"                # Reply
python scripts/x_post.py quote <id> "text"                # Quote tweet
```

### Interact (`x_interact.py`)
```bash
python scripts/x_interact.py like <tweet>        # Like
python scripts/x_interact.py unlike <tweet>      # Unlike
python scripts/x_interact.py retweet <tweet>     # Retweet
python scripts/x_interact.py unretweet <tweet>   # Undo retweet
python scripts/x_interact.py bookmark <tweet>    # Bookmark
python scripts/x_interact.py unbookmark <tweet>  # Remove bookmark
python scripts/x_interact.py follow <username>   # Follow
python scripts/x_interact.py unfollow <username> # Unfollow
python scripts/x_interact.py delete <tweet>      # Delete tweet
python scripts/x_interact.py mute <username>     # Mute
python scripts/x_interact.py unmute <username>   # Unmute
python scripts/x_interact.py block <username>    # Block
python scripts/x_interact.py unblock <username>  # Unblock
```

### DMs (`x_dm.py`)
```bash
python scripts/x_dm.py send <username> "message"  # Send DM
python scripts/x_dm.py inbox --count 10            # Read inbox
```

### Extra (`x_extra.py`)
```bash
python scripts/x_extra.py trends                              # Trending
python scripts/x_extra.py trends --category news               # Category trends
python scripts/x_extra.py bookmarks --count 10                 # List bookmarks
python scripts/x_extra.py notifications --count 10             # Notifications
python scripts/x_extra.py user-info <username>                 # User profile
python scripts/x_extra.py followers <username> --count 20      # Followers
python scripts/x_extra.py following <username> --count 20      # Following
python scripts/x_extra.py upload <filepath>                    # Upload media
python scripts/x_extra.py schedule <timestamp> "text"          # Schedule tweet
python scripts/x_extra.py poll "A" "B" "C" --duration 1440    # Create poll
python scripts/x_extra.py list-create "name" --private         # Create list
python scripts/x_extra.py list-add <list-id> <username>        # Add to list
python scripts/x_extra.py list-remove <list-id> <username>     # Remove from list
python scripts/x_extra.py list-tweets <list-id> --count 20     # List tweets
```

### Auth (`x_auth.py`)
```bash
python scripts/x_auth.py check    # Check auth status
python scripts/x_auth.py whoami   # Current user
python scripts/x_auth.py login    # Login (uses config.json)
```

## Output
All commands: plain text by default, `--json` for structured JSON.

### Media & Reply Context
- Tweets with images/videos include media URLs in output (`🖼️` / `🎥`)
- Replies include `↩️ Reply to:` link to the original tweet
- Agent can fetch media URLs with `web_fetch` and analyze with vision

## Proxy (optional)
Set `"proxy": "http://user:pass@host:port"` in config.json.
