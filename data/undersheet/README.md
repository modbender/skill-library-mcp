# UnderSheet 🗂️

[![GitHub Stars](https://img.shields.io/github/stars/ubgb/undersheet?style=social)](https://github.com/ubgb/undersheet/stargazers)
[![ClawHub](https://img.shields.io/badge/clawhub-install-blue)](https://clawhub.com/skills/undersheet)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

**Persistent thread memory for OpenClaw agents. Works everywhere.**

Zero dependencies. Pure Python stdlib. One file to rule them all.

---

## The Problem

You've already solved the memory problem: `MEMORY.md`, daily logs, SOUL.md. You write things down. That part works.

What you haven't solved is **threading**.

Your agent wakes up, reads its memory files, and has no idea:
- Which threads you were part of that got new replies
- Which posts you already read vs. which are actually new
- What changed on any given platform since the last session

So you either re-check everything (token expensive) or ignore everything (miss replies). Neither is right.

This is the threading gap. UnderSheet closes it.

## The Solution

UnderSheet tracks your threads across heartbeats — on any platform.

```
$ python3 undersheet.py heartbeat --platform hackernews

[undersheet:hackernews] heartbeat @ 09:01 UTC

💬 2 thread(s) with new replies:
  +4 — Ask HN: Share your productive usage of OpenClaw
       https://news.ycombinator.com/item?id=47147183
  +1 — Show HN: UnderSheet – thread memory for AI agents
       https://news.ycombinator.com/item?id=47149006

📰 5 new post(s) in feed:
  [451↑] I pitched a roller coaster to Disneyland at age 10 in 1978
  [397↑] Amazon accused of widespread scheme to inflate prices
  [316↑] Nearby Glasses
  [245↑] Hacking an old Kindle to display bus arrival times
  [207↑] Steel Bank Common Lisp

[undersheet] State saved.

$ python3 undersheet.py status --platform hackernews

[undersheet:hackernews] status
  Last heartbeat : 2026-02-25T09:01:44+00:00
  Tracked threads: 2
  Seen post IDs  : 47

  Threads:
    [24💬] Ask HN: Share your productive usage of OpenClaw  (last seen 2026-02-25)
           https://news.ycombinator.com/item?id=47147183
    [1💬]  Show HN: UnderSheet – thread memory for AI agents (last seen 2026-02-25)
           https://news.ycombinator.com/item?id=47149006
```

Your agent picks up exactly where it left off. Every platform. Every heartbeat.

---

## Supported Platforms

| Platform | Read | Post | Auth |
|----------|------|------|------|
| Moltbook | ✅ | ✅ (CAPTCHA solver included) | API key |
| Hacker News | ✅ | ✅ | Username/password |
| Reddit | ✅ | ✅ | OAuth (client ID/secret) |
| Twitter / X | ✅ | ✅ | Bearer token (read) + OAuth 1.0a (write) |
| Discord | ✅ | ✅ | Bot token |
| _Your platform_ | [add adapter →](#adding-a-platform) | | |

---

## Install

**Recommended — clone from GitHub (always latest):**
```bash
git clone https://github.com/ubgb/undersheet ~/.openclaw/skills/undersheet
```

Or grab individual files:
```bash
# Core engine
curl -fsSL https://raw.githubusercontent.com/ubgb/undersheet/main/undersheet.py \
  -o ~/.openclaw/skills/undersheet/undersheet.py

# Platform adapters (grab what you need)
mkdir -p ~/.openclaw/skills/undersheet/platforms
curl -fsSL https://raw.githubusercontent.com/ubgb/undersheet/main/platforms/moltbook.py \
  -o ~/.openclaw/skills/undersheet/platforms/moltbook.py
curl -fsSL https://raw.githubusercontent.com/ubgb/undersheet/main/platforms/hackernews.py \
  -o ~/.openclaw/skills/undersheet/platforms/hackernews.py
curl -fsSL https://raw.githubusercontent.com/ubgb/undersheet/main/platforms/reddit.py \
  -o ~/.openclaw/skills/undersheet/platforms/reddit.py
```

ClawHub: `clawhub install undersheet` (may lag behind GitHub)

> **Twitter/X adapter:** also grab `platforms/twitter.py`
> ```bash
> curl -fsSL https://raw.githubusercontent.com/ubgb/undersheet/main/platforms/twitter.py \
>   -o ~/.openclaw/skills/undersheet/platforms/twitter.py
> ```

---

## Quick Start

**1. Configure a platform:**
```bash
# Hacker News (no auth needed for read-only)
echo '{"username": "myuser", "password": "mypass"}' \
  > ~/.config/undersheet/hackernews.json
```

**2. Run a heartbeat:**
```bash
python3 ~/.openclaw/skills/undersheet/undersheet.py heartbeat --platform hackernews
```

**3. Track a specific thread:**
```bash
python3 ~/.openclaw/skills/undersheet/undersheet.py track \
  --platform hackernews --thread-id 47147183
```

**4. Add to HEARTBEAT.md:**
```markdown
## UnderSheet (every 30 minutes)
Run: python3 ~/.openclaw/skills/undersheet/undersheet.py heartbeat --platform hackernews
```

---

## Commands

```
heartbeat   Check tracked threads + new feed posts
feed-new    Show only unseen posts from the feed
track       Start tracking a thread by ID
unread      List threads with new replies (no feed)
status      Overview of tracked threads + last run
platforms   List installed platform adapters
```

## Proxy Support

Route agent traffic through a proxy without changing your system settings.

```bash
# Config file (persists across runs)
echo '{"http": "http://yourproxy:8080"}' > ~/.config/undersheet/proxy.json

# Per-command override
python3 undersheet.py heartbeat --platform reddit --proxy http://yourproxy:8080

# Env vars work too
HTTP_PROXY=http://yourproxy:8080 python3 undersheet.py heartbeat --platform hackernews
```

**System VPNs (Mullvad, WireGuard, ProtonVPN):** no config needed — they route all traffic automatically.

---

## Adding a Platform

Drop a file in `platforms/` with a class named `Adapter`:

```python
from undersheet import PlatformAdapter

class Adapter(PlatformAdapter):
    name = "myplatform"

    def get_threads(self, thread_ids: list) -> list:
        # Return: [{"id", "title", "url", "comment_count", "score"}, ...]
        ...

    def get_feed(self, limit=25, **kwargs) -> list:
        # Return: [{"id", "title", "url", "score", "created_at"}, ...]
        ...

    def post_comment(self, thread_id: str, content: str, **kwargs) -> dict:
        # Return: {"success": True} or {"error": "..."}
        ...
```

Run `undersheet.py platforms` to confirm it's detected.

---

## State

State is stored per-platform at `~/.config/undersheet/<platform>_state.json`. Safe to inspect, edit, or back up.

---

## Relationship to MoltMemory

UnderSheet is the generalized successor to [MoltMemory](https://github.com/ubgb/moltmemory). MoltMemory is Moltbook-specific and stays maintained. UnderSheet brings the same architecture to every platform.

---

## Contributing

UnderSheet is community-driven. The most wanted contribution: **new platform adapters**. Adding Bluesky, Mastodon, Lemmy, or anything else? Just drop a file in `platforms/` following the adapter template.

You don't need to write code to contribute:

- **Got an idea?** → [Open a GitHub issue](https://github.com/ubgb/undersheet/issues/new) — one paragraph is enough
- **Found a bug?** → [Report it here](https://github.com/ubgb/undersheet/issues/new) with what you expected vs. what happened
- **Want to build an adapter?** → Pick a platform from the [open issues](https://github.com/ubgb/undersheet/issues) tagged `good first issue`

All code changes go through pull requests — `main` is protected and reviewed before anything merges.

→ See [CONTRIBUTING.md](CONTRIBUTING.md) for the full guide.

---

**⭐ If UnderSheet saves you plumbing work, a GitHub star helps others find it.**
[Star on GitHub](https://github.com/ubgb/undersheet) · [Open an issue](https://github.com/ubgb/undersheet/issues/new) · [Browse open issues](https://github.com/ubgb/undersheet/issues) · [Install on ClawHub](https://clawhub.com/skills/undersheet)

---

## License

MIT
