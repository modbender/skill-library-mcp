<p align="center">
  <img src="assets/banner.svg" alt="Reddit Research" width="500" />
</p>

<p align="center">
  <a href="https://github.com/minilozio/reddit-research/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue?style=flat-square" alt="MIT License" /></a>
  <img src="https://img.shields.io/badge/version-1.0.0-brightgreen?style=flat-square" alt="v1.0.0" />
  <img src="https://img.shields.io/badge/OpenClaw-compatible-red?style=flat-square" alt="OpenClaw" />
  <img src="https://img.shields.io/badge/auth-none-orange?style=flat-square" alt="No Auth" />
  <img src="https://img.shields.io/badge/cost-$0-success?style=flat-square" alt="Free" />
</p>

---

Reddit research agent for [OpenClaw](https://github.com/openclaw/openclaw) and [Claude Code](https://code.claude.com). Search, read threads, monitor subreddits, and analyze user activity — all from the terminal.

**Zero auth. Zero cost. Zero dependencies.**

## Why?

Reddit is the internet's largest collection of **authentic human opinions**. Unlike SEO-optimized blogs or sponsored content, Reddit threads contain real experiences, tested solutions, and unfiltered takes.

This skill lets your agent tap into that — instantly.

## Features

| Command | Description |
|---------|-------------|
| `search` | Global or subreddit-specific search with filters |
| `comments` | Search comments across Reddit (via PullPush/Arctic Shift) |
| `hot` / `new` / `rising` / `top` | Subreddit feeds by sort |
| `controversial` | Controversial posts in a subreddit |
| `multi` | Combined feed from multiple subreddits |
| `thread` | Read post + top comments (pass any Reddit URL) |
| `user` | Profile info + recent posts/comments |
| `subreddit` | Subscriber count, active users, description |
| `find-subs` | Discover subreddits by topic |
| `popular` | List trending subreddits |
| `duplicates` | Find cross-posts across Reddit |
| `wiki` | Read subreddit wiki pages |
| `watchlist` | Monitor subreddits for new activity |
| `cache` | Built-in request caching (15min TTL) |

## Data Providers

Three providers, all free, all zero-auth:

| Provider | Flag | Best For | Limitation |
|----------|------|----------|------------|
| **Reddit** (default) | `--provider reddit` | Real-time data, feeds, threads | ~60 req/min |
| **PullPush** | `--provider pullpush` | Historical/deleted posts, global comment search | Sometimes down |
| **Arctic Shift** | `--provider arctic-shift` | Archived data, deep history | Requires `--sub` or `--author` |

## Install

### OpenClaw
```bash
cd ~/.openclaw/workspace/skills
git clone https://github.com/minilozio/reddit-research.git
```

### Claude Code
```bash
mkdir -p .claude/skills
cd .claude/skills
git clone https://github.com/minilozio/reddit-research.git
```

## Setup

**Node.js 18+** required (for native `fetch`). No API key. No npm install. **Zero dependencies.**

## Usage

All commands run from the scripts directory:

```bash
cd <skill-dir>/scripts
```

### Search

```bash
# Default (Reddit JSON)
npx tsx reddit.ts search "best VPN 2026" --sort top --time year

# Within a subreddit
npx tsx reddit.ts search "memecoin" --sub solana --sort top --time week

# Via PullPush (historical/deleted)
npx tsx reddit.ts search "openclaw" --provider pullpush --limit 10

# Via Arctic Shift (archived)
npx tsx reddit.ts search "agent" --provider arctic-shift --sub openclaw
```

**Options:**
- `--sub <subreddit>` — restrict to a subreddit
- `--sort relevance|top|new|hot|comments` — sort order (default: relevance)
- `--time hour|day|week|month|year|all` — time filter (default: week)
- `--limit N` — max results (default: 15)
- `--provider reddit|pullpush|arctic-shift` — data source
- `--author <username>` — filter by author (Arctic Shift only)
- `--compact` — one-line format
- `--quick` — fast mode with 1hr cache
- `--save` — save results to file
- `--json` / `--markdown` — output format

### Comment Search

Search through comments across Reddit using PullPush or Arctic Shift:

```bash
npx tsx reddit.ts comments "solana scam" --provider pullpush --limit 10
npx tsx reddit.ts comments "openclaw skill" --provider arctic-shift --sub openclaw
```

### Subreddit Feeds

```bash
npx tsx reddit.ts hot solana --limit 10
npx tsx reddit.ts new cryptocurrency --limit 20
npx tsx reddit.ts rising wallstreetbets
npx tsx reddit.ts top cryptocurrency --time week --limit 20
npx tsx reddit.ts controversial politics --time day
```

### Multi-Subreddit Feed

Combine multiple subreddits into one feed:

```bash
npx tsx reddit.ts multi solana+cryptocurrency+defi --sort top --time week
npx tsx reddit.ts multi selfhosted+homelab+linux --sort hot
```

### Read Thread

Read a post with its top comments. Pass any Reddit URL:

```bash
npx tsx reddit.ts thread https://reddit.com/r/solana/comments/abc123/some_title/
npx tsx reddit.ts thread https://reddit.com/r/ClaudeAI/comments/xyz789/usage/ --sort new --limit 50 --depth 5
```

**Options:**
- `--sort top|best|new|controversial|old|qa` — comment sort
- `--limit N` — max comments
- `--depth N` — comment tree depth (default: 3)

### User Profile

```bash
npx tsx reddit.ts user vbuterin --posts --limit 5
npx tsx reddit.ts user spez --comments --sort top
```

### Subreddit Info

```bash
npx tsx reddit.ts subreddit solana
npx tsx reddit.ts sub cryptocurrency
```

### Find Subreddits

```bash
npx tsx reddit.ts find-subs "artificial intelligence" --limit 10
npx tsx reddit.ts find-subs "solana trading"
```

### Popular Subreddits

```bash
npx tsx reddit.ts popular --limit 25
```

### Cross-Posts / Duplicates

Track where a post has been cross-posted:

```bash
npx tsx reddit.ts duplicates <post_id>
```

### Wiki

Read subreddit wiki pages (FAQs, rules, guides):

```bash
npx tsx reddit.ts wiki cryptocurrency
npx tsx reddit.ts wiki privacy "vpn-recommendations"
```

### Watchlist

Monitor specific subreddits:

```bash
npx tsx reddit.ts watchlist                       # Show all
npx tsx reddit.ts watchlist add solana "Solana ecosystem"
npx tsx reddit.ts watchlist add ClaudeAI "AI updates"
npx tsx reddit.ts watchlist remove solana
npx tsx reddit.ts watchlist check                 # Check hot from all
```

### Cache

```bash
npx tsx reddit.ts cache stats     # Cache statistics
npx tsx reddit.ts cache clear     # Clear all cached data
```

## Use Cases

- **Crypto research** — What's r/solana saying about a new token?
- **Scam detection** — Has this project been flagged before?
- **Problem solving** — Real solutions from real people (not AI slop)
- **Trend detection** — What's rising across communities?
- **Competitive research** — What do users say about X vs Y?
- **Monitoring** — Track subreddits for new developments
- **Historical data** — Find deleted/old posts via PullPush or Arctic Shift

## How It Works

**Reddit provider** uses `old.reddit.com/*.json` — Reddit serves JSON data by appending `.json` to any URL. This is a documented, public interface that doesn't require authentication.

**PullPush** (`api.pullpush.io`) is a community-maintained Reddit archive that indexes posts and comments. Great for historical searches and finding deleted content.

**Arctic Shift** (`arctic-shift.photon-reddit.com`) is another community archive focused on comprehensive Reddit data preservation. Requires a subreddit or author filter.

All three are free, require zero authentication, and have generous rate limits.

## File Structure

```
reddit-research/
├── README.md
├── SKILL.md              # OpenClaw skill definition
├── package.json
├── assets/
│   └── banner.svg
├── scripts/
│   ├── reddit.ts         # CLI entry point
│   └── lib/
│       ├── api.ts        # Reddit + PullPush + Arctic Shift API wrapper
│       ├── cache.ts      # File-based cache (15min TTL)
│       └── format.ts     # Terminal + markdown formatters
├── data/
│   ├── watchlist.json    # Watched subreddits
│   └── cache/            # Auto-managed
└── references/
    └── reddit-json-api.md
```

## Requirements

- Node.js 18+ (for native `fetch`)
- No API key needed
- No npm install needed
- Zero dependencies

## License

MIT

---

Built with 🦎 by [Lozio](https://github.com/minilozio) — an [OpenClaw](https://github.com/openclaw/openclaw) skill.
