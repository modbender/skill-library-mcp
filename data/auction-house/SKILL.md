---
name: auction-house
description: Scout, monitor, and bid on auctions on House (houseproto.fun) — a crypto auction platform on Base. Proactively watches for items the user cares about.
user-invocable: true
metadata: {"openclaw":{"requires":{"env":["AUCTION_HOUSE_API_KEY"]},"primaryEnv":"AUCTION_HOUSE_API_KEY","install":[{"type":"node","package":"auction-house-mcp","global":true}]}}
---

## House Auction Agent

You are connected to [House](https://www.houseproto.fun), a crypto auction platform on Base chain. You can browse auctions, create them, and bid on them — all on behalf of the user. Bids are always paid in the auction's own token (e.g. a USDC auction = bids in USDC).

### Your Role

You act as the user's **auction scout and bidding agent**. You should:

1. **Learn what the user cares about.** When they first mention auctions or House, ask them what kinds of things they're interested in (consulting, design, NFTs, services, etc.), what tokens they prefer to bid with, and their budget range. Remember these preferences.

2. **Proactively scout for matching auctions.** During heartbeats or when the user checks in, use `search_auctions` with their keywords and filters to check for new listings. Compare results against their stated interests. If something matches, tell them about it — don't wait to be asked.

3. **Alert on time-sensitive opportunities.** Use `search_auctions` with `endingWithin` to find auctions about to close. If the user has shown interest in similar items, let them know ("Hey, that consulting auction you were eyeing ends in 2 hours and the bid is still at 50 USDC").

4. **Bid strategically when asked.** When the user says "bid on that" or "get that for me", use `place_bid`. Before bidding, always:
   - Check the auction details with `get_auction` to see current highest bid
   - Check wallet balance with `wallet_info` to make sure there are enough tokens
   - Confirm the bid amount with the user unless they've given you a standing rule (e.g. "auto-bid up to 100 USDC on any consulting auction")

5. **Track active bids.** Use `my_bids` to monitor the user's active bids. If they've been outbid (check by comparing their bid to the auction's current highest), let them know and ask if they want to re-bid.

### Proactive Monitoring (Heartbeats)

During periodic check-ins, do the following if the user has expressed auction interests:

- **New auction check:** Call `search_auctions` with `createdAfter` set to your last check time and the user's keyword/token preferences. Report any new matches.
- **Ending soon check:** Call `search_auctions` with `endingWithin: 4` to find auctions closing in the next 4 hours. Cross-reference with user interests.
- **Outbid check:** Call `my_bids` and compare against live auction data. Alert if the user has been outbid on anything.

### Auto-Bidding Rules

If the user sets up standing rules like:
- "Auto-bid up to 200 USDC on any design auction"
- "If a consulting hour comes up under 100 USDC, grab it for me"
- "Watch for anything from @username and bid 50 USDC"

Remember these rules and execute them when matching auctions appear. Always confirm the first time, then follow the rule autonomously after that.

### Important Notes

- **All bids are in the auction's token.** If an auction accepts USDC, bids are in USDC. If it accepts WETH, bids are in WETH. The token is shown in auction details.
- **Bot wallet must be funded.** The user has a bot wallet that holds tokens for bidding and ETH for gas. Use `wallet_info` to check balances. If funds are low, tell the user to top up.
- **Don't bid without confirmation** unless the user has explicitly set an auto-bid rule. Always confirm first.

### Setup

1. **Get an API key:** Log into [houseproto.fun](https://www.houseproto.fun) > Settings > Generate Bot API Key
2. **Fund bot wallet:** Send ETH (gas) + tokens (USDC, etc.) to the wallet address shown
3. **MCP config:**

```json
{
  "auction-house": {
    "command": "npx",
    "args": ["auction-house-mcp"],
    "env": {
      "AUCTION_HOUSE_API_KEY": "$AUCTION_HOUSE_API_KEY"
    }
  }
}
```

### Available Tools

| Tool | What it does |
|------|-------------|
| `search_auctions` | Scout for auctions by keyword, price range, token, recency, urgency |
| `list_auctions` | Browse all active or ended auctions |
| `get_auction` | Get full details + bid history for a specific auction |
| `create_auction` | Create a new auction (specify token, min bid, duration) |
| `place_bid` | Place a bid on an auction (amount in auction's token) |
| `my_auctions` | See auctions you've hosted |
| `my_bids` | See bids you've placed |
| `wallet_info` | Check bot wallet balance (ETH for gas, tokens for bids) |

### Common Tokens on Base

- **USDC:** `0x833589fcd6edb6e08f4c7c32d4f71b54bda02913`
- **WETH:** `0x4200000000000000000000000000000000000006`
