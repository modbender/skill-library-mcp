<p align="center">
  <img src="assets/banner.svg" alt="X-Research But Cheaper" width="500" />
</p>

<p align="center">
  <a href="https://clawhub.ai/skills/x-research-but-cheaper"><img src="https://img.shields.io/badge/ClawHub-Install-orange?style=flat-square&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHRleHQgeT0iMTgiIGZvbnQtc2l6ZT0iMTYiPvCfpp48L3RleHQ+PC9zdmc+" alt="ClawHub" /></a>
  <a href="https://github.com/minilozio/x-research-but-cheaper/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue?style=flat-square" alt="MIT License" /></a>
  <img src="https://img.shields.io/badge/version-1.0.0-brightgreen?style=flat-square" alt="v1.0.0" />
  <img src="https://img.shields.io/badge/OpenClaw-compatible-red?style=flat-square" alt="OpenClaw" />
</p>

---

X/Twitter research agent for [OpenClaw](https://openclaw.ai) and [Claude Code](https://code.claude.com). Search, filter, monitor — all from the terminal.

Powered by [TwitterAPI.io](https://twitterapi.io/?ref=Minilozio). No X Developer Portal account needed. Pay-per-use pricing (~$0.15/1k tweets) instead of $100+/month.

## What it does

Wraps the TwitterAPI.io API into a fast CLI so your AI agent (or you) can search tweets, pull threads, monitor accounts, and get sourced research without writing curl commands.

- **Search** with engagement sorting, time filtering, noise removal
- **Quick mode** for cheap, targeted lookups
- **Profile analysis** — user info + recent tweets
- **Thread reading** — full conversation threads
- **Watchlists** for monitoring accounts
- **Cache** to avoid repeat API charges
- **Cost transparency** — every command shows what it cost

## Install

### ClawHub (recommended)
```bash
clawhub install x-research-but-cheaper
```

### OpenClaw (manual)
```bash
cd ~/.openclaw/workspace/skills
git clone https://github.com/minilozio/x-research-but-cheaper.git
```

### Claude Code
```bash
mkdir -p .claude/skills
cd .claude/skills
git clone https://github.com/minilozio/x-research-but-cheaper.git
```

## Setup

1. **API key** — Get one from [twitterapi.io](https://twitterapi.io/?ref=Minilozio)
2. **Set the env var:**
   ```bash
   export TWITTERAPI_KEY="your-key-here"
   ```
   Or save it to your `.env` file.
3. **Node.js 18+** required (for native `fetch`). **Zero npm dependencies.**

## Usage

### Natural language (just talk to Claude)
- "What are people saying about Opus 4.6?"
- "Search X for the latest on Seedance 2.0"
- "What's the sentiment around remote work this week?"
- "Check what @minilozio posted recently"
- "Research the best takes on AI coding assistants"
- "Find viral tweets about startups this week"

### CLI commands
```bash
cd skills/x-research-but-cheaper/scripts

# Search (sorted by likes, auto-filters retweets)
npx tsx x-search.ts search "Seedance 2.0" --sort likes --limit 10

# Quick pulse check
npx tsx x-search.ts search "remote work" --quick

# Profile — user info + recent tweets
npx tsx x-search.ts profile minilozio --count 5

# Read a thread
npx tsx x-search.ts thread 1234567890123456789

# Single tweet
npx tsx x-search.ts tweet 1234567890123456789

# Replies and quotes
npx tsx x-search.ts replies 1234567890123456789 --sort likes
npx tsx x-search.ts quotes 1234567890123456789

# Mentions — who's talking about someone
npx tsx x-search.ts mentions ycombinator --since 1d

# Followers / following
npx tsx x-search.ts followers minilozio --limit 20
npx tsx x-search.ts following minilozio --limit 20

# Search for users
npx tsx x-search.ts users "machine learning engineer"

# Trending topics
npx tsx x-search.ts trending
npx tsx x-search.ts trending --woeid 23424977  # US trends

# Community research
npx tsx x-search.ts community 1234567890
npx tsx x-search.ts community tweets 1234567890

# Watchlist
npx tsx x-search.ts watchlist add minilozio "AI research"
npx tsx x-search.ts watchlist check

# Save research to file
npx tsx x-search.ts search "query" --save --markdown
```

### Search options
```
--sort likes|retweets|impressions|recent    Sort order (default: likes)
--since 1h|3h|12h|1d|7d                    Time filter
--min-likes N                               Minimum likes
--min-impressions N                         Minimum views
--pages N                                   Pages to fetch, 1-5 (default: 3)
--limit N                                   Max results (default: 15)
--quick                                     Quick mode (see below)
--from <username>                           Shorthand for from:username
--quality                                   Min 10 likes filter
--no-replies                                Exclude replies
--type Top|Latest                           Search mode (default: Latest)
--save                                      Save results to file
--json                                      Raw JSON output
--markdown                                  Markdown research doc
```

**X search operators work too:** `from:user`, `OR`, `-is:reply`, `has:links`, `min_faves:N`, `lang:en`, `$TICKER`, and more.

## Quick Mode

`--quick` is designed for fast, cheap lookups when you just need a pulse check on a topic.

**What it does:**
- Forces single page (max 10 results) — reduces API cost
- Auto-appends `-is:retweet -is:reply` noise filters
- Minimum 5 likes filter (removes spam/zero-engagement)
- Uses 1-hour cache TTL instead of the default 15 minutes
- Shows cost summary after results

**Examples:**
```bash
# Quick pulse check on a topic
npx tsx x-search.ts search "cursor IDE" --quick

# Quick check what someone is saying
npx tsx x-search.ts search "agents" --from minilozio --quick

# Quick quality-only results
npx tsx x-search.ts search "startup funding" --quality --quick
```

**Why it's cheaper:**
- Prevents multi-page fetches (biggest cost saver)
- 1hr cache means repeat searches are free
- Noise filters mean fewer junk results
- Cost displayed after every search — no surprises

## `--from` Shorthand

Adds `from:username` to your query without typing the full operator syntax.

```bash
# These are equivalent:
npx tsx x-search.ts search "React from:dan_abramov"
npx tsx x-search.ts search "React" --from dan_abramov

# Works with other flags
npx tsx x-search.ts search "LLM" --from minilozio --quick --quality
```

If your query already contains `from:`, the flag won't double-add it.

## `--quality` Flag

Filters out low-engagement tweets (≥10 likes required).

```bash
npx tsx x-search.ts search "open source AI" --quality
```

## Examples

```bash
# What are the best takes on a trending topic
npx tsx x-search.ts search "Seedance 2.0" --sort likes --since 1d --type Top

# Expert opinions with engagement filter
npx tsx x-search.ts search "AI coding assistants" --min-likes 50 --quality

# What did someone post recently
npx tsx x-search.ts profile paulg --count 10

# Deep research with multiple pages saved to markdown
npx tsx x-search.ts search "startup advice" --pages 3 --save --markdown

# Quick check on breaking news
npx tsx x-search.ts search "GPT-5" --quick

# Filter to a specific expert's takes
npx tsx x-search.ts search "transformers" --from minilozio --quality
```

## Research Loop

For deep research (not just a quick search):

1. **Broad search** — `search "topic" --sort likes` to find key voices
2. **Drill into profiles** — `profile username` for context on interesting people
3. **Read threads** — `thread <id>` for detailed takes
4. **Track ongoing** — `watchlist add` key accounts, `watchlist check` periodically
5. **Refine** — Narrow with `--since`, `--min-likes`, `--from`, `--no-replies`
6. **Save** — Use `--save --markdown` for research docs

## Why TwitterAPI.io?

| | X API Official | TwitterAPI.io |
|---|---|---|
| **Cost** | $100+/mo (Basic) | ~$0.15/1k tweets |
| **Setup** | Developer Portal, application, approval | Just an API key |
| **Rate limit** | 10 req/15min | 200 QPS |
| **Archive** | 7 days (recent search) | Full archive |

## Cost

TwitterAPI.io uses **pay-per-use pricing** with prepaid credits. No subscriptions, no monthly caps.

**Per-resource costs:**
| Resource | Cost |
|----------|------|
| Tweet fetch | $0.15 / 1,000 tweets |
| Profile lookup | $0.18 / 1,000 lookups |

**Estimated costs per operation:**
| Operation | Est. cost |
|-----------|-----------|
| Quick search (1 page, ≤20 tweets) | ~$0.003 |
| Standard search (3 pages, default) | ~$0.009 |
| Deep research (5 pages) | ~$0.015 |
| Profile check (user + tweets) | ~$0.003 |
| Watchlist check (5 accounts) | ~$0.015 |
| Cached repeat (any) | free |

**How x-research saves money:**
- Cache (15min default, 1hr in quick mode) — repeat queries are free
- Quick mode prevents accidental multi-page fetches
- Watchlist checks run in parallel (faster, same cost)
- Cost displayed after every command so you know what you're spending
- `--from` targets specific users instead of broad searches

## File Structure

```
x-research/
├── SKILL.md              # Agent instructions (Claude reads this)
├── README.md
├── package.json          # Zero dependencies
├── scripts/
│   ├── x-search.ts       # CLI entry point
│   └── lib/
│       ├── api.ts        # TwitterAPI.io wrapper
│       ├── cache.ts      # File-based cache
│       └── format.ts     # Terminal + markdown formatters
├── data/
│   ├── watchlist.json    # Accounts to monitor
│   └── cache/            # Auto-managed
└── references/
    └── twitterapi-io.md  # API reference
```

## Security

**API key handling:** x-research reads your key from the `TWITTERAPI_KEY` env var. The key is never printed to stdout, but be aware:

- **AI coding agents** (Claude Code, OpenClaw, etc.) may log tool calls in session transcripts. If you're running x-research inside an agent session, your API key could appear in those logs.
- **Recommendations:**
  - Set `TWITTERAPI_KEY` as a system env var (not inline in commands)
  - Review your agent's session log settings
  - Use environment files (`.env`) and make sure they're in `.gitignore`
  - Rotate your key if you suspect exposure

## Limitations

- Read-only — never posts or interacts with X
- Search quality depends on TwitterAPI.io's index (may include promoted/irrelevant content)
- `min_likes` uses X's native `min_faves:` operator for server-side filtering (efficient, no wasted API quota)
- Thread fetching uses replies endpoint + conversation_id search (may miss some replies in very large threads)
- Zero dependencies means no fancy CLI framework — basic arg parsing only
- Requires Node.js 18+ for native `fetch`

## License

MIT
