# readx — Twitter/X Intelligence Toolkit

A Claude Code skill for Twitter/X data analysis. Analyze users, tweets, trends, communities, and networks with actionable insights.

## Features

- **User Deep Profiling** — influence score, engagement quality, content style
- **Influence & Network Mapping** — relationships, clusters, connectors
- **Viral & Engagement Analysis** — propagation chains, virality metrics
- **Sentiment & Topic Monitoring** — narrative tracking, sentiment shifts
- **Competitive Benchmarking** — head-to-head account comparison
- **Community Intelligence** — community health, key voices
- **Trend Forecasting** — multi-region trend tracking, breakout detection
- **KOL Discovery** — find and rank influencers in any niche
- **Account Authenticity Audit** — bot detection, credibility scoring

## Setup

### Step 1: Get an API Key

Go to **https://readx.cc**, sign up, and copy your API key from the dashboard.

### Step 2: Add MCP Server

No installation needed — readx runs as a remote MCP server.

**Claude Code:**
```bash
claude mcp add --transport http readx -s user https://readx.cc/mcp?apikey=<API_KEY>
```

**Other editors** (Cursor, Windsurf, Claude Desktop, etc.) — add to your MCP config:

```json
{
  "mcpServers": {
    "readx": {
      "url": "https://readx.cc/mcp?apikey=<API_KEY>"
    }
  }
}
```

## Key Metrics

| Metric | Formula |
|--------|---------|
| Engagement Rate | (likes + RTs + replies) / followers x 100 |
| Virality Ratio | retweets / likes (>0.3 = highly shareable) |
| Controversy Ratio | replies / likes (>0.5 = polarizing) |
| Authority Ratio | followers / following (>10 = high authority) |

## License

MIT
