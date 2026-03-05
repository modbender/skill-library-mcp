# osint-social

[中文版本](./README.zh.md)

> OpenClaw skill for OSINT username lookup across 1000+ social media platforms — including Chinese platforms

An [OpenClaw](https://openclaw.ai) skill that wraps [qeeqbox/social-analyzer](https://github.com/qeeqbox/social-analyzer) for global platforms, plus a dedicated Chinese platform module covering Bilibili, Zhihu, and Weibo.

## What it does

Ask your OpenClaw agent things like:

- "Investigate the username shadowfox99"
- "Find all accounts for johndoe"
- "OSINT lookup for testuser, include Chinese platforms"
- "Check if username exists on Bilibili and Zhihu"

The agent scans 1000+ global platforms plus Chinese platforms, and returns a clean natural language summary — no raw JSON dumps.

## Platform Coverage

### Global (via social-analyzer)
- Social: Twitter/X, Instagram, Facebook, TikTok, Pinterest, Reddit, Tumblr
- Developer: GitHub, GitLab, Stack Overflow, Dev.to
- Gaming: Steam, Chess.com, Roblox, Twitch
- Music: SoundCloud, Bandcamp, Last.fm
- And 990+ more...

### Chinese Platforms (via cn_lookup.py)

| Platform | Support | Data Retrieved |
|----------|---------|----------------|
| Bilibili 哔哩哔哩 | ✅ Full | Username, followers, video count, bio |
| Zhihu 知乎 | ✅ Full | Username, followers, bio |
| Weibo 微博 | ⚠️ Degraded | Existence check + basic info |
| Xiaohongshu / Douyin | ❌ Not supported | Requires login |

## Install

```bash
git clone https://github.com/guleguleguru/osint-social.git skills/osint-social
```

Or via ClawHub:
```bash
clawhub install osint-social
```

## Requirements

- Python 3
- `pip3 install social-analyzer --break-system-packages`
- No API keys required

## File Structure

```
osint-social/
├── SKILL.md                    # Main skill instructions for OpenClaw
├── README.md                   # This file (English)
├── README.zh.md                # Chinese version
├── scripts/
│   ├── run_osint.sh            # Shell wrapper for global lookup
│   └── cn_lookup.py            # Chinese platform lookup
└── references/
    └── platforms.md            # Platform categories reference
```

## Example Output

```
Found 5 accounts:

Global platforms (social-analyzer):
• GitHub (rate: 95): github.com/johndoe — 234 followers
• Twitter (rate: 88): twitter.com/johndoe
• Instagram (rate: 82): instagram.com/johndoe — photographer

Chinese platforms (cn_lookup):
• Bilibili [95] ✅ Exact match: space.bilibili.com/12345678 — 1,200 followers
• Zhihu [92] ✅ Exact match: zhihu.com/people/johndoe — 340 followers

⚠️ All data sourced from public profiles. Use responsibly and legally.
```

## Disclaimer

This tool only accesses **publicly available information**. It is intended for legitimate use cases such as self-auditing, security research, and journalism. Do not use to stalk, harass, or violate anyone's privacy.

## Credits

- Global lookup powered by [qeeqbox/social-analyzer](https://github.com/qeeqbox/social-analyzer)
- First OSINT skill published on [ClawHub](https://clawhub.ai)
- Built by [@guleguleguru](https://github.com/guleguleguru)
