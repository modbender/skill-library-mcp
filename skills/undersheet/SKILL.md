---
name: undersheet
description: "Persistent thread memory for OpenClaw agents across any platform — Moltbook, Hacker News, Reddit, Discord, Twitter. Tracks threads, surfaces only new replies, feed cursor so you never re-read the same post. Zero dependencies, pure Python stdlib. Use when your agent needs to remember which threads it engaged with across heartbeat sessions."
homepage: https://github.com/ubgb/undersheet
metadata:
  {
    "openclaw":
      {
        "emoji": "🗂️",
        "requires": { "bins": ["python3"] },
      },
  }
---

# UnderSheet

**Version:** 1.2.1
**Author:** ubgb
**Tags:** memory, thread-tracking, feed-cursor, heartbeat, moltbook, hackernews, reddit, multi-platform

## What It Does

UnderSheet gives your OpenClaw agent persistent thread memory across any platform — Moltbook, Hacker News, Reddit, and more.

Every heartbeat, your agent wakes up fresh with zero context. UnderSheet fixes that:
- Tracks every thread you've engaged with and surfaces only the ones with new replies
- Feed cursor so you only see posts you haven't read yet
- Pluggable platform adapters — one skill, every platform
- Zero dependencies, pure Python stdlib

Built on the architecture of MoltMemory, generalized for everywhere.

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/ubgb/undersheet/main/undersheet.py \
  -o ~/.openclaw/skills/undersheet/undersheet.py

mkdir -p ~/.openclaw/skills/undersheet/platforms
curl -fsSL https://raw.githubusercontent.com/ubgb/undersheet/main/platforms/moltbook.py \
  -o ~/.openclaw/skills/undersheet/platforms/moltbook.py
curl -fsSL https://raw.githubusercontent.com/ubgb/undersheet/main/platforms/hackernews.py \
  -o ~/.openclaw/skills/undersheet/platforms/hackernews.py
curl -fsSL https://raw.githubusercontent.com/ubgb/undersheet/main/platforms/reddit.py \
  -o ~/.openclaw/skills/undersheet/platforms/reddit.py
```

## Setup

Configure credentials for each platform you use:

**Moltbook:**
```bash
echo '{"api_key": "YOUR_KEY", "agent_name": "YOUR_NAME"}' \
  > ~/.config/moltbook/credentials.json
```

**Hacker News** (optional, read-only works without):
```bash
echo '{"username": "YOUR_HN_USER", "password": "YOUR_HN_PASS"}' \
  > ~/.config/undersheet/hackernews.json
```

**Reddit:**
```bash
echo '{
  "client_id": "...", "client_secret": "...",
  "username": "...", "password": "...",
  "user_agent": "undersheet:v1.0 (by /u/youruser)"
}' > ~/.config/undersheet/reddit.json
```

**Discord:**
```bash
echo '{"bot_token": "Bot YOUR_TOKEN_HERE", "guild_id": "YOUR_SERVER_ID"}' \
  > ~/.config/undersheet/discord.json
```
Bot setup: https://discord.com/developers/applications → New Application → Bot → Reset Token
Required permissions: Read Messages, Send Messages, Read Message History, Use Public Threads
Invite your bot: `https://discord.com/api/oauth2/authorize?client_id=YOUR_ID&permissions=84992&scope=bot`

**Twitter / X:**
```bash
echo '{
  "bearer_token": "AAA...",
  "api_key": "...", "api_secret": "...",
  "access_token": "...", "access_token_secret": "..."
}' > ~/.config/undersheet/twitter.json
```
`bearer_token` alone works for read-only (free tier).
OAuth 1.0a keys required for posting (Basic tier, ~$100/mo).
Get keys: https://developer.twitter.com/en/portal/dashboard

## Usage

Run a heartbeat (checks tracked threads + new feed posts):
```bash
python3 ~/.openclaw/skills/undersheet/undersheet.py heartbeat --platform moltbook
python3 ~/.openclaw/skills/undersheet/undersheet.py heartbeat --platform hackernews
python3 ~/.openclaw/skills/undersheet/undersheet.py heartbeat --platform reddit
```

Start tracking a thread:
```bash
python3 ~/.openclaw/skills/undersheet/undersheet.py track --platform hackernews --thread-id 47147183
```

See only new feed posts:
```bash
python3 ~/.openclaw/skills/undersheet/undersheet.py feed-new --platform reddit --min-score 50
```

List available platform adapters:
```bash
python3 ~/.openclaw/skills/undersheet/undersheet.py platforms
```

## Proxy Support

Route agent traffic through a proxy or VPN without changing system settings.

**HTTP proxy:**
```bash
echo '{"http": "http://yourproxy:8080"}' > ~/.config/undersheet/proxy.json
```

**Or pass per-command:**
```bash
python3 undersheet.py heartbeat --platform reddit --proxy http://yourproxy:8080
```

**System VPNs (Mullvad, WireGuard, ProtonVPN):** no config needed — they route all traffic automatically. SOCKS5 users: use a system VPN instead of a local proxy.

**Env vars also work** (`HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY`) — UnderSheet respects whatever is set.

## Add to HEARTBEAT.md

```markdown
## UnderSheet (every 30 minutes)
- python3 ~/.openclaw/skills/undersheet/undersheet.py heartbeat --platform moltbook
- python3 ~/.openclaw/skills/undersheet/undersheet.py heartbeat --platform hackernews
```

## Adding a New Platform

Create `platforms/myplatform.py` with a class named `Adapter` that extends `PlatformAdapter`:

```python
from undersheet import PlatformAdapter

class Adapter(PlatformAdapter):
    name = "myplatform"

    def get_threads(self, thread_ids): ...
    def get_feed(self, limit=25, **kwargs): ...
    def post_comment(self, thread_id, content, **kwargs): ...
```

That's it. `undersheet.py heartbeat --platform myplatform` will pick it up automatically.
