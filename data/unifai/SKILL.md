---
name: unifai
description: Unifai CLI for searching and invoking services across DeFi, token data, social media, web search, news, travel, sports, and more.
allowed-tools: Bash(unifai:*)
version: 1.0.0
metadata:
  openclaw:
    requires:
      env:
        - UNIFAI_AGENT_API_KEY
      bins:
        - unifai
    primaryEnv: UNIFAI_AGENT_API_KEY
    emoji: "🦄"
    homepage: https://github.com/unifai-network/unifai-cli
    install:
      - kind: brew
        tap: unifai-network/homebrew-unifai-cli
        formula: unifai
        bins: [unifai]
---

# unifai

A CLI for searching and invoking services on the Unifai network. Supports 40+ services across DeFi, token data, social media, web search, news, travel, sports, and utilities.

## What it does

unifai enables you to:

- **Search services**: Find services and actions using natural language queries
- **Invoke services**: Execute actions with customizable parameters and retry logic
- **Manage configuration**: Configure API keys with multiple priority levels

### Available service categories

- **DeFi**: Swap, lend, borrow, provide liquidity (Aave, Uniswap, Jupiter, Meteora, Pendle, Compound, 1inch, and more)
- **Token & market data**: Prices, OHLCV, security analysis (Birdeye, CoinGecko, DexScreener, DefiLlama, GoPlusSecurity)
- **Wallet & chain data**: Token balances across Solana, Ethereum, Base, BSC, Polygon
- **Social media**: Twitter/X search, user timelines, tweet threads
- **Web search & news**: General search, Google news, financial data (SerpAPI, Tavily)
- **Travel**: Flight and hotel search
- **Sports**: NBA scores, soccer results (ESPN)
- **Utilities**: Math, time, domain availability, Solana rent reclaimer

## Installation

### Homebrew

```bash
brew update
brew tap unifai-network/homebrew-unifai-cli
brew install unifai
unifai version
```

## Authentication

API key source priority (highest to lowest):

1. Command-line flag: `--api-key`
2. Environment variable: `UNIFAI_AGENT_API_KEY`
3. Config file: `~/.config/unifai-cli/config.yaml`

> **Note**: Setting `UNIFAI_AGENT_API_KEY` as an environment variable is recommended. The config file works too, but OpenClaw's skill check only detects the environment variable.

### Initialize Configuration

Generate a config template:

```bash
unifai config init
```

Show effective configuration:

```bash
unifai config show
```

## Usage Examples

### Search for Services

Search for services using natural language:

```bash
# DeFi
unifai search --query "swap usdc to sol"

# Token data
unifai search --query "get bitcoin price"

# Social media
unifai search --query "search twitter for AI news"

# Travel
unifai search --query "find flights from NYC to London"

# With pagination
unifai search --query "lending protocols" --limit 10 --offset 0

# Include specific actions
unifai search --query "defi protocols" --include-actions action1,action2
```

### Invoke Services

Execute actions with JSON payloads:

```bash
# Inline JSON payload
unifai invoke --action "Meteora--29--swap" --payload '{"amount":100}'

# Read payload from file
unifai invoke --action "MyAction--1--execute" --payload @payload.json

# With custom retries and timeout
unifai invoke --action "MyAction--1--execute" --payload '{"x":1}' --max-retries 3 --timeout 60s
```

**Tip**: Parameter names vary by action (e.g., SerpAPI uses `q`, Twitter uses `query`). Use `unifai search --query "..." --json` to see the expected payload schema for each action before invoking.

### Payload Formats

unifai supports flexible payload handling:

- **auto** (default): Parses valid JSON as object, otherwise treats as string
- **object**: Forces JSON object parsing
- **string**: Sends payload as raw string

```bash
# Force object parsing
unifai invoke --action "MyAction" --payload '{"key":"value"}' --payload-format object

# Force string parsing
unifai invoke --action "MyAction" --payload "raw text" --payload-format string
```

### Output Formats

```bash
# Human-readable output (default)
unifai search --query "swap tokens"

# JSON output for scripting
unifai search --query "swap tokens" --json
```

## Configuration

### Config File Location

`~/.config/unifai-cli/config.yaml`

### Example Configuration

```yaml
apiKey: your-unifai-api-key
```

## Retry and Timeout Behavior

- **Default max retries**: 1
- **Retry strategy**: Exponential backoff (1s, 2s, 4s, ...)
- **Default timeout**: 50s
- **Retry conditions**: Network failures and HTTP 5xx errors

## Exit Codes

- **0**: Success
- **1**: API or runtime error
- **2**: Argument or usage error

## Common Use Cases

### Swap Tokens on Solana

```bash
unifai search --query "swap usdc to sol on solana"
unifai invoke --action "Meteora--29--swap" --payload '{"fromToken":"USDC","toToken":"SOL","amount":100}'
```

### Search Twitter

```bash
unifai search --query "search tweets"
unifai invoke --action "Twitter--68--searchTweets" --payload '{"query":"AI agents","type":"Top"}' --json
```

### Search Flights

```bash
unifai search --query "find flights"
unifai invoke --action "SerpAPI--21--flightSearch" --payload '{"departure_id":"SFO","arrival_id":"JFK","outbound_date":"2026-04-01","type":2}' --json
```

### Search Hotels

```bash
unifai search --query "find hotels"
unifai invoke --action "SerpAPI--21--hotelSearch" --payload '{"q":"hotels in Tokyo","check_in_date":"2026-04-01","check_out_date":"2026-04-03"}' --json
```

### NBA Scores

```bash
unifai search --query "NBA scores"
unifai invoke --action "ESPN--176--RetrieveNBAScoreboard" --payload '{"dates":"20260301"}' --json
```

## Security Model

- **No private keys are sent to the API.** The `UNIFAI_AGENT_API_KEY` authenticates requests but does not grant custody of any wallet or funds.
- **On-chain transactions require local signing.** When you invoke a DeFi action (swap, lend, etc.), the API returns an unsigned transaction and a link (e.g., `https://tx.unifai.network/tx/...`). You must open the link, review the transaction, and sign it with your own wallet. Nothing executes on-chain without your explicit approval.
- **Read-only actions return data directly.** Searches, price lookups, Twitter queries, and other non-transactional actions return results inline with no signing step.

## When to Use This Skill

Use unifai when you need to:

- Search for services and actions across 40+ integrated providers
- Execute DeFi transactions (swap, lend, borrow, provide liquidity)
- Look up token prices, security data, or market analytics
- Search Twitter/X or fetch user timelines
- Search the web, news, or financial data
- Find flights, hotels, or sports scores
- Check wallet balances across multiple chains
- Integrate any of the above into scripts and automation workflows

## Advanced Features

### Custom Timeouts

```bash
unifai invoke --action "LongRunning--1--process" --payload '{}' --timeout 120s
```

### Retry Configuration

```bash
unifai invoke --action "Unreliable--1--call" --payload '{}' --max-retries 5
```

### API Key Override

```bash
unifai search --query "test" --api-key temporary-key-123
```

## Troubleshooting

### Check Configuration

```bash
unifai config show
```

This displays the effective configuration and shows which source (flag, env, or file) is being used.

### Verify Installation

```bash
unifai version
```

### Test API Connectivity

```bash
unifai search --query "test" --json
```

## Additional Resources

- Config template: `configs/config.example.yaml`
- Homebrew tap: https://github.com/unifai-network/homebrew-unifai-cli
