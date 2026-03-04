---
name: x-research
description: >
  X/Twitter research skill powered by TwitterAPI.io. Agentic search, profile analysis,
  thread reading, watchlists, and sourced briefings. Use when asked to search X/Twitter,
  check what people are saying about a topic, monitor accounts, or research crypto/tech
  narratives on X.
metadata:
  {
    "openclaw":
      {
        "emoji": "🐦",
        "requires": { "bins": ["node", "npx"] },
        "primaryEnv": "TWITTERAPI_KEY",
        "envHint": "Get your API key from https://twitterapi.io — pay-per-use, no subscription needed"
      },
    "clawhub":
      {
        "category": "research",
        "tags": ["twitter", "x", "research", "search", "social-media"],
        "website": "https://twitterapi.io"
      }
  }
---

# X Research

General-purpose X/Twitter research agent powered by [TwitterAPI.io](https://twitterapi.io). Search, filter, monitor — all from the terminal. No X Developer Portal account needed.

For API details: read `references/twitterapi-io.md`.

## Why TwitterAPI.io?

| | X API Official | TwitterAPI.io |
|---|---|---|
| **Cost** | $100+/mo (Basic plan) | ~$0.15/1k tweets (pay-per-use) |
| **Setup** | Developer Portal application | Just an API key |
| **Rate limit** | 10 req/15min | 200 QPS |
| **Archive** | 7 days (recent) | Full archive |

## Setup

1. Get a TwitterAPI.io key from [twitterapi.io](https://twitterapi.io)

2. Set the env var:
```bash
export TWITTERAPI_KEY="your-key-here"
```
Or add to your `.env` file.

3. Node.js 18+ required (for native `fetch`). No `npm install` needed — zero dependencies.

## CLI Tool

All commands run from the scripts directory:

```bash
cd <skill-dir>/scripts
```

### Search

```bash
npx tsx x-search.ts search "<query>" [options]
```

**Options:**
- `--sort likes|retweets|impressions|recent` — sort order (default: likes)
- `--since 1h|3h|12h|1d|7d` — time filter
- `--min-likes N` — filter minimum likes
- `--min-impressions N` — filter minimum views
- `--pages N` — pages to fetch, 1-5 (default: 1)
- `--limit N` — max results to display (default: 15)
- `--quick` — fast mode: 1 page, max 10 results, noise filter, 1hr cache
- `--from <username>` — shorthand for `from:username` in query
- `--quality` — filter low-engagement tweets (≥10 likes)
- `--no-replies` — exclude replies
- `--save` — save results to file
- `--type Top|Latest` — search mode (default: Latest; Top returns algorithmic ranking)
- `--json` — raw JSON output
- `--markdown` — markdown formatted output

Auto-adds `-is:retweet` unless query already includes it. Cost estimate shown after each search.

**Examples:**
```bash
npx tsx x-search.ts search "AI agents Base chain" --sort likes --limit 10
npx tsx x-search.ts search "BNKR" --quick
npx tsx x-search.ts search "from:frankdegods" --sort recent
npx tsx x-search.ts search "(opus OR claude) trading" --pages 2 --save
npx tsx x-search.ts search "$SOL memecoin" --min-likes 50 --since 1d
```

**Search operators** (passed through to X):

| Operator | Example | Notes |
|----------|---------|-------|
| keyword | `bun 2.0` | Implicit AND |
| `OR` | `bun OR deno` | Must be uppercase |
| `-` | `-is:retweet` | Negation |
| `()` | `(fast OR perf)` | Grouping |
| `from:` | `from:elonmusk` | Posts by user |
| `to:` | `to:elonmusk` | Replies to user |
| `#` | `#buildinpublic` | Hashtag |
| `$` | `$AAPL` | Cashtag |
| `lang:` | `lang:en` | Language filter |
| `is:retweet` | `-is:retweet` | Filter retweets |
| `is:reply` | `-is:reply` | Filter replies |
| `has:media` | `has:media` | Contains media |
| `has:links` | `has:links` | Contains links |
| `min_faves:` | `min_faves:100` | Min likes (native) |

### Profile

```bash
npx tsx x-search.ts profile <username> [--count N] [--replies] [--json]
```

Fetches user info and recent tweets. Excludes replies by default.

### Single Tweet

```bash
npx tsx x-search.ts tweet <tweet_id> [--json]
```

### Thread

```bash
npx tsx x-search.ts thread <tweet_id>
```

Fetches root tweet, author thread continuations, and replies in chronological order.

### Replies

```bash
npx tsx x-search.ts replies <tweet_id> [--sort likes|recent] [--limit N]
```

Get replies to a specific tweet, sorted by engagement.

### Quote Tweets

```bash
npx tsx x-search.ts quotes <tweet_id> [--sort likes|recent] [--limit N]
```

See who quoted a tweet and what they said.

### Mentions

```bash
npx tsx x-search.ts mentions <username> [--since 1d|7d] [--sort recent|likes] [--limit N]
```

Get tweets that mention a user. Great for tracking what people are saying about someone.

### Followers / Following

```bash
npx tsx x-search.ts followers <username> [--limit N]
npx tsx x-search.ts following <username> [--limit N]
```

List a user's followers or who they follow. Shows name, follower count, and bio snippet.

### Search Users

```bash
npx tsx x-search.ts users "<query>" [--limit N]
```

Search for user accounts by keyword.

### Trending

```bash
npx tsx x-search.ts trending [--woeid N] [--count N]
```

Get trending topics. Default: worldwide (woeid=1). Common WOEIDs: US=23424977, UK=23424975, Italy=23424853.

### Community

```bash
npx tsx x-search.ts community <id>           # Community info
npx tsx x-search.ts community tweets <id>    # Community tweets
```

Research X Communities by ID.

### Watchlist

```bash
npx tsx x-search.ts watchlist                       # Show all
npx tsx x-search.ts watchlist add <user> [note]     # Add account
npx tsx x-search.ts watchlist remove <user>          # Remove account
npx tsx x-search.ts watchlist check                  # Check recent from all
```

Watchlist stored in `data/watchlist.json`. Use for periodic monitoring — check if key accounts posted anything notable.

### Cache

```bash
npx tsx x-search.ts cache clear    # Clear all cached results
```

Default 15-minute TTL. Quick mode uses 1-hour TTL. Avoids repeat API charges.

## Research Loop (Agentic)

When doing deep research (not just a quick search), follow this loop:

### 1. Decompose the Question into Queries

Turn the research question into 3-5 keyword queries:

- **Core query**: Direct keywords for the topic
- **Expert voices**: `from:` specific known experts
- **Pain points**: Keywords like `(broken OR bug OR issue)`
- **Positive signal**: Keywords like `(shipped OR love OR fast)`
- **Links**: `has:links` for resource-rich tweets
- **Crypto spam**: Add `-airdrop -giveaway -whitelist` if needed

### 2. Search and Extract

Run each query via CLI. After each, assess:
- Signal or noise? Adjust operators.
- Key voices worth searching `from:` specifically?
- Threads worth following via `thread` command?

### 3. Follow Threads

When a tweet has high engagement or is a thread starter:
```bash
npx tsx x-search.ts thread <tweet_id>
```

### 4. Synthesize

Group findings by theme, not by query:

```
### [Theme/Finding Title]

[1-2 sentence summary]

- @username: "[key quote]" (♥ N, 👁 N) [Tweet](url)
- @username2: "[another perspective]" (♥ N, 👁 N) [Tweet](url)
```

### 5. Save

Use `--save` flag or `--markdown` for research docs.

## Refinement Heuristics

- **Too much noise?** Add `--no-replies`, use `--sort likes`, narrow keywords
- **Too few results?** Broaden with `OR`, remove restrictive operators
- **Crypto spam?** Add `-airdrop -giveaway -whitelist` to query
- **Expert takes only?** Use `from:` or `--min-likes 50`
- **Substance over hot takes?** Search with `has:links`

## Heartbeat Integration

On heartbeat, run `watchlist check` to see if key accounts posted anything notable. Flag only if genuinely interesting/actionable.

## Cost

TwitterAPI.io pay-per-use pricing:
- ~$0.15 per 1,000 tweets fetched
- ~$0.18 per profile lookup
- Cost estimate shown after each command
- Cache prevents redundant charges

## File Structure

```
skills/x-research/
├── SKILL.md                # This file
├── package.json            # Zero dependencies
├── scripts/
│   ├── x-search.ts         # CLI entry point
│   └── lib/
│       ├── api.ts          # TwitterAPI.io wrapper
│       ├── cache.ts        # File-based cache (15min/1hr TTL)
│       └── format.ts       # Terminal + markdown formatters
├── data/
│   ├── watchlist.json      # Accounts to monitor
│   └── cache/              # Auto-managed
└── references/
    └── twitterapi-io.md    # API endpoint reference
```

## Requirements

- Node.js 18+ (for native `fetch`)
- A TwitterAPI.io API key
- No npm install needed — zero dependencies
