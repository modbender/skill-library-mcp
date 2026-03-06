---
name: twit-mcp
description: Real-time X/Twitter data via x402 micropayments. Look up users, fetch tweets, search the full archive — pay per request in USDC on Base. No API keys required.
version: 1.0.0
homepage: https://twit.sh
metadata:
  openclaw:
    requires:
      env: [WALLET_PRIVATE_KEY]
      bins: [npx]
    primaryEnv: WALLET_PRIVATE_KEY
    emoji: 🐦
    install:
      - kind: node
        package: twit-mcp
        bins: [twit-mcp]
---

# twit-mcp

Real-time X/Twitter data for AI agents, powered by [x402](https://x402.org) micropayments. Each tool call costs $0.0025–$0.01 USDC, paid automatically from your wallet on Base. No API key required.

## Setup

Set your wallet private key in OpenClaw's environment settings:

```
WALLET_PRIVATE_KEY=0xYourPrivateKeyHere
```

> Use a dedicated wallet with minimal funds. Do not use your main wallet.

Then add to your `mcp.json`:

```json
{
  "mcpServers": {
    "twit": {
      "command": "npx",
      "args": ["-y", "twit-mcp"],
      "env": {
        "WALLET_PRIVATE_KEY": "${WALLET_PRIVATE_KEY}"
      }
    }
  }
}
```

## Available Tools

### Users

| Tool | Description | Price |
|------|-------------|-------|
| `get_user_by_username` | Get a user profile by username | $0.005 USDC |
| `get_user_by_id` | Get a user profile by numeric ID | $0.005 USDC |
| `search_users` | Search users by keyword (paginated) | $0.01 USDC |
| `get_user_followers` | Get a user's followers (paginated) | $0.01 USDC |
| `get_user_following` | Get accounts a user follows (paginated) | $0.01 USDC |
| `get_users` | Bulk lookup up to 50 users | $0.01 USDC |

### Tweets

| Tool | Description | Price |
|------|-------------|-------|
| `get_tweet_by_id` | Get a tweet by its ID | $0.0025 USDC |
| `get_user_tweets` | Get a user's recent tweets (paginated) | $0.01 USDC |
| `search_tweets` | Full-archive tweet search with filters | $0.01 USDC |
| `get_tweets` | Bulk lookup up to 50 tweets | $0.01 USDC |

## Usage Examples

```
Get me the latest tweets from @elonmusk about doge
```

```
Look up the Twitter profile of vitalik.eth
```

```
Search for tweets from @sama since 2025-01-01 mentioning Claude
```

```
How many followers does @jack have?
```

## How Payments Work

Each tool call makes an HTTP request to `x402.twit.sh`. The server responds with `402 Payment Required`. The MCP server signs a USDC payment locally using your `WALLET_PRIVATE_KEY` and retries — all automatically, in one round-trip. Your key never leaves your machine.

## Links

- [twit.sh](https://twit.sh) — API reference and pricing
- [npm: twit-mcp](https://www.npmjs.com/package/twit-mcp)
- [x402.org](https://x402.org) — payment protocol docs
