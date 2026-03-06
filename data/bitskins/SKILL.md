---
name: bitskins-api
description: >
  Interacts with the BitSkins REST API V2 and WebSocket API for CS2/Dota 2 skin trading.
  Supports account management, market search, buying, selling, listing, delisting, relisting,
  price updates, Steam inventory/deposits/trades, wallet operations, and real-time WebSocket
  subscriptions. Use when the user wants to search for skins, check prices, buy or sell items,
  manage their BitSkins account, check balances, or interact with the BitSkins marketplace.
metadata:
  author: custom
  version: "1.0"
  env_vars: "BITSKINS_API_KEY"
---

# BitSkins API Skill

## Authentication

All requests to the BitSkins API require authentication via the `x-apikey` header.

The API key must be set in the environment variable `BITSKINS_API_KEY`.
The user can obtain their API key from BitSkins account settings after enabling API access.

**Important:** Some endpoints (wallet withdrawals, 2FA operations) also require a `twofa_code` parameter. Always ask the user for their 2FA code when calling these endpoints rather than storing it.

## Base URL

```
https://api.bitskins.com
```

## Making Requests

Use the helper script to make API calls:

```bash
bash bitskins-api/scripts/bitskins-api.sh <METHOD> <PATH> [JSON_BODY]
```

Examples:

```bash
# GET request (no body)
bash bitskins-api/scripts/bitskins-api.sh GET /account/profile/me

# POST request with JSON body
bash bitskins-api/scripts/bitskins-api.sh POST /account/profile/balance

# POST with parameters
bash bitskins-api/scripts/bitskins-api.sh POST /market/search/730 '{"limit":10,"offset":0,"where":{}}'
```

## Rate Limits

- **Global:** 50 requests per 10 seconds
- **Market search (`/market/search/*`):** 1 request per second
- These limits are dynamic and may be reduced under heavy server load.

## Request Format

- The API accepts JSON format
- GET requests: no body required
- POST requests: JSON body with required parameters

## Response Format

All responses are JSON. Successful responses contain the data directly. Error responses include error codes documented in [references/api-endpoints.md](references/api-endpoints.md).

## API Sections Overview

The API is organized into the following sections. See [references/api-endpoints.md](references/api-endpoints.md) for the full endpoint reference.

### Account
- **Profile:** Get session info, balance, update account settings, update trade link, block account
- **Affiliate:** Get affiliate info, claim money, view reward history, set affiliate code
- **2FA:** Create, verify, disable, lock/unlock two-factor authentication
- **API Access:** Create or disable API keys

### Config
- **Currency rates:** Get current exchange rates
- **Fee plans:** Get available fee plans
- **Platform status:** Check if platform is operational

### Market (CS2 app_id=730, Dota 2 app_id=570)
- **Pricing:** Get sales history, pricing summaries
- **Search:** Browse CS2/Dota 2 markets, search own items, get item details, search by skin name, get filters
- **Buy:** Buy single item, multiple items, or bulk buy
- **Withdraw:** Withdraw single or multiple purchased items to Steam
- **Delist:** Remove single or multiple items from sale
- **Relist:** Relist single or multiple delisted items
- **Update price:** Change price on single or multiple listed items
- **History:** View item transaction history
- **Receipt:** Get purchase receipt
- **Bump:** Bump items for visibility, manage bump settings, buy bump packages
- **Skins catalog:** Get all available skin names for a game
- **In-sell items:** Get all currently listed items for a game

### Steam
- **Inventory:** List Steam inventory items
- **Deposit:** Deposit items from Steam to BitSkins
- **Trades:** View Steam trade offers and their status

### Wallet
- **Stats:** Get wallet statistics, KYC limits
- **Transactions:** List completed and pending transactions
- **Reports:** Generate and download wallet reports

### Wallet Deposit
- **Binance Pay:** Create Binance Pay deposit
- **Cryptocurrency:** Get deposit addresses for BTC, LTC, ETH
- **Gift codes:** Redeem gift codes, view used codes
- **Zen:** Create Zen deposit
- **Card (Unlimint):** Add cards, list cards, deposit via card

### Wallet Withdraw
- **Cryptocurrency:** Withdraw to BTC, LTC, ETH addresses
- **Binance Pay:** Withdraw via Binance Pay
- **Card (Unlimint):** Withdraw to Visa card

### WebSocket
Real-time updates via `wss://ws.bitskins.com`. See [references/websocket.md](references/websocket.md) for details.

## Common Patterns

### Searching the Market

The market search endpoints accept `where` objects for filtering and support `limit`/`offset` pagination:

```json
{
  "limit": 20,
  "offset": 0,
  "order": [{"field": "price", "order": "ASC"}],
  "where": {
    "skin_name": ["AK-47 | Redline"],
    "price_from": 1000,
    "price_to": 5000
  }
}
```

Note: Prices are in **cents** (e.g., 1000 = $10.00).

### Buying Items

To buy an item, you need its `id` and `app_id`. Use market search to find items, then:

```json
{"app_id": 730, "id": "ITEM_ID", "max_price": 1500}
```

The `max_price` parameter protects against price changes between search and purchase.

### Listing/Depositing Items

1. Get Steam inventory: `POST /steam/inventory/list`
2. Deposit items: `POST /steam/deposit/many` with item IDs and prices
3. Monitor trade status: `POST /steam/trade/active`

### Withdrawing Purchased Items

After buying, withdraw to Steam:
```json
{"app_id": 730, "id": "ITEM_ID"}
```

## Important Notes

- Always confirm with the user before executing buy, sell, withdraw, or any financial operation
- Prices are in cents (integer values)
- Game IDs: CS2 = 730, Dota 2 = 570
- The `where_mine` filter on "mine" endpoints accepts: `listed`, `pending_withdrawal`, `in_queue`, `given`, `need_to_withdraw`
- 2FA codes are time-sensitive; always request fresh codes from the user
