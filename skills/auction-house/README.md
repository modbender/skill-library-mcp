# auction-house-mcp

MCP (Model Context Protocol) server for [House](https://www.houseproto.fun) — create auctions and place bids on the Base chain auction platform from any AI agent.

Works with OpenClaw, Claude Desktop, Cursor, and any MCP-compatible client.

## Quick Start

```bash
npx auction-house-mcp
```

## Setup

1. **Create an account** at [houseproto.fun](https://www.houseproto.fun)
2. **Generate a Bot API Key** from Settings — you'll get an API key and a bot wallet address
3. **Fund the bot wallet** with ETH (gas) + tokens (USDC, etc.)
4. **Configure your MCP client:**

```json
{
  "mcpServers": {
    "auction-house": {
      "command": "npx",
      "args": ["auction-house-mcp"],
      "env": {
        "AUCTION_HOUSE_API_KEY": "ak_your_key_here"
      }
    }
  }
}
```

## Tools

| Tool | Description |
|------|-------------|
| `list_auctions` | Browse active/ended auctions |
| `get_auction` | Get auction details + bid history |
| `create_auction` | Create a new auction on-chain |
| `place_bid` | Place a bid on an active auction |
| `my_auctions` | List your hosted auctions |
| `my_bids` | List your placed bids |
| `wallet_info` | Check bot wallet address + balances |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `AUCTION_HOUSE_API_KEY` | Yes | Your API key from houseproto.fun |
| `AUCTION_HOUSE_URL` | No | API base URL (default: `https://www.houseproto.fun`) |

## License

MIT
