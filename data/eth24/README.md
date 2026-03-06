# ♦︎ ETH24

Daily Ethereum intelligence. The top tweets from the last 24 hours, ranked by importance with one-line commentary.

Fork it for any topic.

## How It Works

1. **Crawl** - Grok x_search finds tweets by context + X API v2 finds tweets by engagement + RSS feeds for background context
2. **Rank** - AI selects up to 10 by importance, writes one-line commentary
3. **Output** - CLI (stdout) or tweet mode (Typefully)

```
Grok x_search ──> contextual discovery
                          \
                    X API lookup ──> engagement metrics
                          /                       |
X API search ──> keyword tweets              merge + dedup
                                                  |
                                      RSS ──> AI ranking
                                                  |
                                            ♦︎ output
```

## Why This Architecture

Neither data source alone is good enough.

**Grok x_search** understands context. It finds tweets that matter even if engagement is low - a new EIP with 50 likes can be more important than a meme with 5,000. But Grok doesn't return reliable engagement metrics.

**X API v2** has real metrics (likes, retweets, replies) but finds tweets by keyword matching, which surfaces a lot of noise. Popular doesn't mean important.

**The hybrid approach:** Grok discovers what's important. X API verifies how much traction it has. The merge gives you both signal and validation. Either source can run independently if the other fails - Grok-only or X API-only both produce usable results, just less complete.

**Why the ranking is a separate AI step:** Engagement scores alone produce bad digests. A spam airdrop tweet with botted likes would outrank a meaningful protocol update. The AI ranking step filters junk, deduplicates overlapping stories, and writes commentary that adds context the original tweet doesn't provide.

No hardcoded account list - anyone can surface a top tweet. Candidates are scored by `(likes + retweets) / 2` with a configurable engagement floor that auto-lowers on quiet days.

## Cost Per Run

| Step | API | Cost |
|------|-----|------|
| Grok discovery | xAI Responses API (grok-4-1-fast + x_search) | ~$0.15 |
| X API search | X API v2 recent search (up to 300 tweets) | ~$1.50 |
| X API lookup | X API v2 tweet lookup (10-50 enrichments) | ~$0.10 |
| AI ranking | Anthropic Claude or xAI Grok (fallback) | ~$0.10 |
| **Total per run** | | **~$1.85** |
| **Monthly (daily)** | | **~$55** |

When using the Claude Code skill flow (`/eth24`), the ranking step is free - Claude handles it directly. Drops the per-run cost to ~$1.75.

X API is pay-per-use at ~$0.005/tweet read. The xAI minimum credit buy is $25, which covers ~130 daily runs of the Grok steps alone.

## Install

### Option A: ClawHub

```bash
npx clawhub@latest install eth24
```

### Option B: Claude Code Skill

Clone this repo and run `/eth24` from Claude Code. Claude handles the ranking directly - no separate AI API key needed for that step.

### Option C: Standalone

```bash
pip install -r requirements.txt
python3 main.py            # CLI mode (default)
python3 main.py --mode tweet  # Typefully draft
```

## Setup

### API Keys

```
XAI_API_KEY=...           # xAI API key (console.x.ai) - Grok discovery + ranking fallback
X_BEARER_TOKEN=...        # X API v2 bearer token (developer.x.com) - keyword search + metrics
ANTHROPIC_API_KEY=...     # Anthropic API key (optional, primary ranking provider)
```

At minimum, set `XAI_API_KEY` and `X_BEARER_TOKEN`. Add `ANTHROPIC_API_KEY` for Claude-based ranking (falls back to Grok if unavailable).

### Configure Your Topic

Edit `config.json`:

```json
{
  "topic": "Ethereum",
  "brand": {
    "name": "ETH24",
    "account": "@yourhandle",
    "repo_url": "github.com/you/your-fork"
  },
  "crawl": {
    "x_search_terms": ["Ethereum", "ETH", "EIP", "Pectra", "L2", "rollups"],
    "rss_feeds": {
      "The Block": "https://www.theblock.co/rss.xml",
      "Bankless": "https://feeds.banklesshq.com/rss"
    },
    "lookback_hours": 24,
    "max_tweets": 10,
    "engagement_floor": 200,
    "max_candidates": 50
  },
  "rank": {
    "ai_provider_order": ["anthropic", "xai"],
    "voice": "Concise, informed, direct. Short sentences. Plain language. No emojis. No emdashes."
  }
}
```

## Fork It

ETH24 is built for Ethereum but the pipeline is topic-agnostic. To run it for something else:

1. Fork this repo
2. Edit `config.json`: change `topic`, `brand`, `x_search_terms`, `rss_feeds`
3. Set your API keys
4. Run it

Examples: `SOL24`, `AI24`, `DEFI24`, `BTC24` - same architecture, different search terms.

## Output

```
ETH24 - 2/18/26

Vitalik on surveillance, EIP-7623 efficiency, privacy momentum

♦︎ Vitalik underscores the real-world harms of surveillance,
  highlighting privacy's urgency in Ethereum.
  https://x.com/VitalikButerin/status/2024106047460475063

♦︎ EIP-7623 increases calldata gas costs but keeps overall
  expenses low due to other optimizations.
  https://x.com/nero_eth/status/2023681491499163911
```

All output goes to `output/YYYY-MM-DD/`:
- `crawled.json` - raw tweet data with engagement metrics
- `ranked.json` - selected stories with commentary
- `cli.txt` - formatted plain text (CLI mode)
- `thread.txt` - formatted tweet (tweet mode)

## Credits

Built by [Pat McGowan](https://x.com/patmilkgallon) at [Number Group](https://numbergroup.xyz/) for the [Ethereum Community Foundation](https://ethcf.org/).

MIT License
