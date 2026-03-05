---
name: deso-research
description: Research and analyze content across decentralized social networks (Farcaster, Lens, Nostr, Bluesky) using the deso-ag CLI tool. Use this skill when users want to research topics on decentralized social platforms, analyze trending content, extract discussion terms, browse Farcaster channels, or compare engagement across networks. Trigger on phrases like "research X on Farcaster", "what's trending on Lens", "analyze [topic] across deso networks", "search deso for [topic]", "extract trending terms", "browse Farcaster channels", "what are people saying about X on Farcaster/Lens/Nostr/Bluesky", or any query about decentralized social media content. Make sure to use this skill for any decentralized social research tasks, even if the user just says "check Farcaster" or "look up [topic] on Lens".
metadata:
  openclaw:
    emoji: "🔍"
    requires:
      bins:
        - deso-ag
    install:
      - id: npm
        kind: npm
        package: deso-ag
        global: true
        bins:
          - deso-ag
        label: "Install deso-ag CLI (npm)"
---

# deso-research

Research and analyze content across decentralized social networks using [deso-ag](https://www.npmjs.com/package/deso-ag).

deso-ag is a CLI tool that aggregates posts from Farcaster, Lens, Nostr, and Bluesky. It provides search, trending, term extraction, and channel browsing — with a `compact` output format designed specifically for AI agent consumption.

## Prerequisites

### Check Installation

```bash
which deso-ag || echo "deso-ag not found — install with: npm install -g deso-ag"
```

If deso-ag is missing, install it:

```bash
npm install -g deso-ag
```

### API Keys (Optional)

deso-ag works without any keys — Lens, Nostr, and Bluesky trending all function keyless. For full functionality, these environment variables unlock additional networks:

| Variable | Unlocks | How to Get |
|----------|---------|------------|
| `NEYNAR_API_KEY` | Farcaster search + trending | Free at neynar.com |
| `BLUESKY_IDENTIFIER` | Bluesky search | Your handle (e.g. user.bsky.social) |
| `BLUESKY_APP_PASSWORD` | Bluesky search | bsky.app/settings/app-passwords |

Without a key, that network is silently skipped. Everything else works normally.

Check which networks are available before running commands:

```bash
echo "Neynar: ${NEYNAR_API_KEY:+set}"
echo "Bluesky ID: ${BLUESKY_IDENTIFIER:+set}"
echo "Bluesky PW: ${BLUESKY_APP_PASSWORD:+set}"
```

Inform the user which networks will be included based on available keys.

## Core Workflows

### 1. Search for Content

Use `search` to find posts about a topic. Always use `--format compact` for agent consumption.

```bash
# Basic search across all available networks
deso-ag search "ethereum" --format compact --limit 20

# Multi-word AND search (all terms must match)
deso-ag search "AI crypto" --format compact --limit 15

# Network-specific search
deso-ag search "NFT" --sources farcaster --format compact

# Channel-specific (Farcaster only)
deso-ag search --channel dev --sources farcaster --format compact

# Sort by recency for latest discussions
deso-ag search "base chain" --sort recent --format compact --limit 10
```

### 2. Get Trending Content

Use `trending` to see what's popular right now.

```bash
# Trending across all networks
deso-ag trending --format compact --limit 20

# Trending on specific networks
deso-ag trending --sources farcaster,lens --format compact

# Trending over the past week
deso-ag trending --timeframe week --format compact
```

### 3. Extract Discussion Terms

Use `terms` to discover the most-discussed topics, weighted by engagement.

```bash
# Top 3 terms per platform, last 24h
deso-ag terms --format json

# Top 5 terms from Farcaster this week
deso-ag terms --top 5 --sources farcaster --timeframe week --format json

# Terms across specific networks
deso-ag terms --top 5 --sources farcaster,nostr --format json
```

### 4. Browse Farcaster Channels

```bash
deso-ag channels --limit 20
```

## Output Handling

**Always use `--format compact`** for search and trending commands. The compact format returns a single JSON object optimized for agent analysis:

```json
{
  "meta": {
    "query": "...",
    "totalPosts": 42,
    "sources": [{"name": "farcaster", "count": 15}, ...],
    "timeframe": "24h",
    "fetchedAt": "2025-01-01T00:00:00.000Z"
  },
  "posts": [
    {
      "id": "...",
      "source": "farcaster",
      "author": "username",
      "content": "full untruncated content...",
      "timestamp": "2025-01-01T00:00:00.000Z",
      "url": "https://...",
      "score": 523,
      "engagement": {"likes": 400, "reposts": 50, "replies": 23},
      "tags": []
    }
  ]
}
```

The `score` field is pre-computed: `likes + reposts×2 + replies`. Use it for ranking.

For `terms`, use `--format json` which returns structured term frequency data.

## Analysis Guidelines

After gathering data, synthesize findings into insights. Never just dump raw JSON to the user.

1. **Summarize the landscape:** How many posts found, across which networks, what timeframe
2. **Highlight top content:** Surface the highest-engagement posts with author, source, and brief summary
3. **Identify themes:** Group related posts and extract common threads
4. **Provide engagement context:** What content resonates most and why
5. **Link to originals:** Include post URLs so the user can engage directly

Only compare activity across networks if the user specifically asks for a cross-network comparison.

### Example Analysis Output

```
Pulled 42 posts about "AI agents" from Farcaster (15), Lens (12), and Nostr (15) over the last 24h.

**The dominant conversation** is around autonomous agents that can transact onchain
without human approval. @dwr's post (score: 523) kicked this off by demoing an agent
that autonomously allocated funds across DeFi protocols based on real-time yield data.
The replies are split — builders are excited about composability (agents calling other
agents via onchain messages), while others are raising concerns about liability when
an agent makes a bad trade. @jessepollak responded pointing to Base's account
abstraction work as a potential guardrail layer.

**A second thread** is forming around agent-to-agent communication standards. Several
posts reference a draft spec for a messaging protocol between onchain agents. @stani
on Lens (score: 312) argued that without a shared standard, we'll end up with walled
agent ecosystems that can't interoperate — drawing a parallel to early social media
APIs. There's skepticism in the replies about whether standardization is premature
given how fast the space is moving.

**Smaller but notable:** 3-4 posts on Nostr are discussing privacy-preserving agents
that use zk proofs to verify actions without revealing the agent's strategy or
holdings. Early stage but worth watching.

**Key voices to follow on this topic:**
- @dwr (Farcaster) — actively building and demoing agent infra
- @jessepollak (Farcaster) — connecting this to Base ecosystem work
- @stani (Lens) — framing the standards/interop conversation

**Source posts:**
- [dwr's agent demo](https://...) — score: 523
- [stani on agent standards](https://...) — score: 312
- [jessepollak on account abstraction](https://...) — score: 287
```

## Quick Command Reference

| Command | Purpose | Default Sort | Default Format |
|---------|---------|-------------|----------------|
| `search [query]` | Find posts about a topic | relevance | markdown |
| `trending` | Popular content right now | engagement | summary |
| `terms` | Top discussion terms | — | — |
| `channels` | Browse Farcaster channels | — | — |

### Common Options

| Option | Short | Values | Default |
|--------|-------|--------|---------|
| `--sources` | `-s` | farcaster,lens,nostr,bluesky | all |
| `--timeframe` | `-t` | 24h, 48h, week | 24h |
| `--format` | `-f` | json, markdown, summary, compact | varies |
| `--limit` | `-l` | any positive integer | 25 |
| `--sort` | `-o` | engagement, recent, relevance | varies |
| `--channel` | `-c` | channel ID (Farcaster only) | none |
| `--top` | `-n` | any positive integer (terms only) | 3 |

For the full command reference with output schemas and library usage, see `references/command-reference.md`.

## Error Handling

- If deso-ag is not found, install it: `npm install -g deso-ag`
- If no results return for a network, that network's API key is likely missing — inform the user
- Nostr can be slow or inconsistent — retry once if it times out
- If you hit rate limit errors, let the user know and suggest they run their own infrastructure for heavy usage