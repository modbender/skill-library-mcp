---
name: reddit-research
description: >
  Reddit research skill — zero auth, zero dependencies, three data providers.
  Search posts, read threads with comments, monitor subreddits, analyze users,
  track cross-posts, search comments, and run watchlists. Default provider uses
  old.reddit.com JSON endpoints. PullPush and Arctic Shift available for
  historical/deleted content. Use when asked to search Reddit, check what people
  are saying, find solutions to problems, or research any topic with real
  community opinions.
---

# Reddit Research

General-purpose Reddit research agent. Search, read, monitor — all from the terminal. No API key needed.

## Why?

Reddit is the largest collection of authentic human opinions on the internet. Unlike SEO-optimized blog posts or sponsored content, Reddit threads contain real experiences, tested solutions, and unfiltered takes.

**Zero auth. Zero cost. Zero dependencies.**

## Data Providers

| Provider | Flag | Best For | Limitation |
|----------|------|----------|------------|
| **Reddit** (default) | `--provider reddit` | Real-time data, feeds, threads | ~60 req/min |
| **PullPush** | `--provider pullpush` | Historical/deleted posts, global comment search | Sometimes down |
| **Arctic Shift** | `--provider arctic-shift` | Archived data, deep history | Requires `--sub` or `--author` |

**Default is Reddit** (real-time). Switch to PullPush or Arctic Shift when you need historical data or deleted content.

## Setup

Node.js 18+ required (for native `fetch`). No `npm install` needed.

```bash
cd <skill-dir>/scripts
```

## CLI Tool

### Search

```bash
npx tsx reddit.ts search "<query>" [options]
```

**Options:**
- `--sub <subreddit>` — restrict to a subreddit
- `--sort relevance|top|new|hot|comments` — sort order (default: relevance)
- `--time hour|day|week|month|year|all` — time filter (default: week)
- `--limit N` — max results (default: 15)
- `--provider reddit|pullpush|arctic-shift` — data source
- `--author <username>` — filter by author (Arctic Shift only)
- `--compact` — one-line format
- `--save` — save results to file
- `--json` — raw JSON output
- `--markdown` — markdown formatted output

**Examples:**
```bash
npx tsx reddit.ts search "pumpfun scam" --sort top --time month
npx tsx reddit.ts search "best VPN" --sub privacy --sort top --time year
npx tsx reddit.ts search "openclaw" --provider pullpush --limit 20
npx tsx reddit.ts search "agent" --provider arctic-shift --sub openclaw
```

### Comment Search

Search through comments using PullPush or Arctic Shift:

```bash
npx tsx reddit.ts comments "<query>" [--sub <subreddit>] [--provider pullpush|arctic-shift] [--limit N]
```

```bash
npx tsx reddit.ts comments "solana scam" --provider pullpush --limit 10
npx tsx reddit.ts comments "openclaw" --provider arctic-shift --sub openclaw
```

### Subreddit Feeds

```bash
npx tsx reddit.ts hot <subreddit> [--limit N] [--time day|week]
npx tsx reddit.ts new <subreddit> [--limit N]
npx tsx reddit.ts rising <subreddit> [--limit N]
npx tsx reddit.ts top <subreddit> [--time day|week|month|year|all] [--limit N]
npx tsx reddit.ts controversial <subreddit> [--time day|week] [--limit N]
```

### Multi-Subreddit Feed

```bash
npx tsx reddit.ts multi <sub1+sub2+sub3> [--sort hot|new|top] [--time day|week] [--limit N]
```

### Read Thread

```bash
npx tsx reddit.ts thread <url> [--sort top|best|new|controversial] [--limit N] [--depth N]
```

### User Profile

```bash
npx tsx reddit.ts user <username> [--posts|--comments] [--sort new|top|hot] [--limit N]
```

### Subreddit Info

```bash
npx tsx reddit.ts subreddit <name>
```

### Find Subreddits

```bash
npx tsx reddit.ts find-subs "<query>" [--limit N]
```

### Popular Subreddits

```bash
npx tsx reddit.ts popular [--limit N]
```

### Cross-Posts / Duplicates

```bash
npx tsx reddit.ts duplicates <post_id>
```

### Wiki

```bash
npx tsx reddit.ts wiki <subreddit> [page]
```

### Watchlist

```bash
npx tsx reddit.ts watchlist                       # Show all
npx tsx reddit.ts watchlist add <sub> [note]      # Add subreddit
npx tsx reddit.ts watchlist remove <sub>          # Remove
npx tsx reddit.ts watchlist check                 # Check hot posts from all
```

### Cache

```bash
npx tsx reddit.ts cache stats     # Cache statistics
npx tsx reddit.ts cache clear     # Clear all cached data
```

## Research Loop (Agentic)

When doing deep research, follow this loop:

### 1. Decompose the Question

Turn the research question into 3-5 search queries:
- **Direct query**: Core keywords
- **Subreddit-specific**: Search within the most relevant sub
- **Solution-focused**: Add "solved", "fix", "how to"
- **Experience-focused**: Add "experience", "review", "worth it"
- **Negative signal**: "scam", "avoid", "warning"
- **Historical**: Use `--provider pullpush` for deleted/old content

### 2. Search and Triage

Run each query. For each result set:
- High score + lots of comments = worth reading the thread
- Low score but specific = might have niche info
- Cross-posted = narrative spreading

### 3. Read Key Threads

```bash
npx tsx reddit.ts thread <url> --sort top --limit 30
```

### 4. Cross-Reference

```bash
npx tsx reddit.ts duplicates <post_id>
```

### 5. Comment Deep Dive

Search through comments when posts don't surface the answer:
```bash
npx tsx reddit.ts comments "specific error message" --provider pullpush --limit 20
```

### 6. Synthesize

Group findings by theme:

```
### [Finding/Theme]
[Summary]
- u/username in r/subreddit (⬆️ N): "[key quote]" [Link](url)
- u/username2 in r/subreddit2 (⬆️ N): "[another take]" [Link](url)
```

## Heartbeat Integration

On heartbeat, run `watchlist check` to see if watched subreddits have notable activity. Flag only if genuinely interesting/actionable.

## Rate Limits

- **Reddit JSON**: ~60 req/min, User-Agent required, auto-retry with backoff
- **PullPush**: Generous, no official limit, sometimes down
- **Arctic Shift**: Generous, no official limit
- **Cache**: 15min TTL prevents redundant hits

## File Structure

```
skills/reddit-research/
├── SKILL.md                # This file
├── README.md
├── package.json            # Zero dependencies
├── assets/
│   └── banner.svg
├── scripts/
│   ├── reddit.ts           # CLI entry point
│   └── lib/
│       ├── api.ts          # Reddit + PullPush + Arctic Shift wrapper
│       ├── cache.ts        # File-based cache
│       └── format.ts       # Terminal + markdown formatters
├── data/
│   ├── watchlist.json      # Watched subreddits
│   └── cache/              # Auto-managed
└── references/
    └── reddit-json-api.md  # API endpoint reference
```

## Requirements

- Node.js 18+ (for native `fetch`)
- No API key needed
- No npm install needed — zero dependencies
