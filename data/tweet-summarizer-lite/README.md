# Tweet Summarizer Lite

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An **OpenClaw agent skill** — fetch, save, and summarize a single tweet from Twitter/X using natural language. Simple and lightweight: one command, one save folder, no setup.

## How to Use

Once installed, just talk to your agent naturally:

> *"What does this tweet say?"* → paste an x.com URL  
> *"Grab this tweet and save it"*  
> *"Summarize that tweet I saved earlier"*  
> *"Search my saved tweets for AI"*  
> *"Find tweets I saved from @elonmusk"*

Your agent handles everything — no commands needed.

## Features

- 🐦 **Single tweet fetching** — fetch any tweet by URL
- 📊 **Auto-summary** — key points extracted automatically after fetching
- 💾 **Simple storage** — all tweets saved to one flat folder
- 🔍 **Basic search** — find saved tweets by text, author, or date

## Prerequisites

Requires the [`bird`](https://github.com/steipete/bird) CLI and valid Twitter session cookies.

```bash
npm install -g @steipete/bird
```

Set your credentials (see [SECURITY.md](SECURITY.md) for how to get these):

```bash
export AUTH_TOKEN="your_auth_token"
export CT0="your_ct0_token"
```

## Installation

Install via [ClawHub](https://clawhub.ai) or clone manually:

```bash
git clone https://github.com/FranciscoBuiltDat/openclaw-tweet-summarizer-lite.git
```

## Scripts

| Script | Description |
|--------|-------------|
| `tweet.py` | Fetch a single tweet, save it, auto-summarize |
| `search_tweets.py` | Search saved tweets by text, author, or date |
| `summarize.py` | Re-summarize a previously saved tweet |
| `config.py` | Toggle auto-summary on/off |

## Storage

All tweets saved to `~/.openclaw/workspace/data/tweets/index.json` — one flat file, no folders or organization.

## Pro Version

Need threads, user timelines, collections, or folder organization? Upgrade to [tweet-summarizer-pro](https://github.com/FranciscoBuiltDat/openclaw-tweet-summarizer-pro):

- 🧵 Full thread fetching
- 👤 User & home timelines
- 📂 Virtual collections with archive/restore
- 🔍 Advanced search across folders and collections
- 📊 Rich summaries with engagement metrics

## Contributing

Contributions welcome! Please read [SECURITY.md](SECURITY.md) before contributing.

## License

MIT — see [LICENSE](LICENSE)
