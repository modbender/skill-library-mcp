# twit-mcp

An MCP server that gives AI agents real-time access to X/Twitter data through [twit.sh](https://twit.sh) — powered by [x402](https://x402.org) micropayments. No API keys, no sign-up. Agents pay per request in USDC on Base.

## Tools

| Tool | Description | Price |
|------|-------------|-------|
| `get_user_by_username` | Get a user profile by username | $0.005 USDC |
| `get_user_by_id` | Get a user profile by numeric ID | $0.005 USDC |
| `search_users` | Search users by keyword (paginated) | $0.01 USDC |
| `get_user_followers` | Get a user's followers (paginated) | $0.01 USDC |
| `get_user_following` | Get accounts a user follows (paginated) | $0.01 USDC |
| `get_users` | Bulk lookup up to 50 users by ID | $0.01 USDC |
| `get_tweet_by_id` | Get a tweet by its ID | $0.0025 USDC |
| `get_user_tweets` | Get a user's recent tweets (paginated) | $0.01 USDC |
| `search_tweets` | Full-archive tweet search with filters | $0.01 USDC |
| `get_tweets` | Bulk lookup up to 50 tweets by ID | $0.01 USDC |

## Requirements

- Node.js 20+
- A wallet with a small amount of USDC on Base Mainnet
- The wallet's private key (used locally to sign payments — never sent anywhere)

> **Use a dedicated wallet with minimal funds. Do not use your main wallet.**

## Setup

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "twit": {
      "command": "npx",
      "args": ["-y", "twit-mcp"],
      "env": {
        "WALLET_PRIVATE_KEY": "0xYourPrivateKeyHere"
      }
    }
  }
}
```

### Claude Code

```bash
claude mcp add -e WALLET_PRIVATE_KEY=0xYourPrivateKeyHere twit -- npx -y twit-mcp
```

### OpenClaw

In OpenClaw chat:

```
/install twit-mcp
```

Then set `WALLET_PRIVATE_KEY` in OpenClaw's environment settings.

### Cursor

Add to your Cursor MCP settings:

```json
{
  "mcpServers": {
    "twit": {
      "command": "npx",
      "args": ["-y", "twit-mcp"],
      "env": {
        "WALLET_PRIVATE_KEY": "0xYourPrivateKeyHere"
      }
    }
  }
}
```

## How It Works

1. Your agent calls a tool (e.g. `get_user_tweets`)
2. The MCP server requests the data from `x402.twit.sh`
3. The API responds with `402 Payment Required` and a USDC amount
4. The MCP server signs the payment locally using your private key
5. The API verifies the payment on Base and returns the data
6. Your agent gets the result — all in one round-trip

Your private key never leaves your machine. It is only used locally to sign EIP-712 typed data for x402 payments.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `WALLET_PRIVATE_KEY` | Yes | Private key of the wallet that will pay for requests (hex, `0x`-prefixed) |
| `API_BASE` | No | Override the API base URL (default: `https://x402.twit.sh`) |

## Links

- [twit.sh](https://twit.sh) — API reference and pricing
- [x402.org](https://x402.org) — x402 protocol documentation
- [Base](https://base.org) — L2 network used for payments
