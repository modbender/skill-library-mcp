---
name: steam-community-inventory
description: Retrieves Steam inventory data and manages trade offers on steamcommunity.com
homepage: https://steamcommunity.com/dev
metadata: {"clawdbot":{"emoji":"\u2694","requires":{"bins":["jq","curl"],"env":["STEAM_ID","STEAM_COOKIES","STEAM_API_KEY","STEAM_SESSION_ID"]}}}
---


# Steam Community Inventory Skill

Retrieve and browse a Steam user's inventory, and send/manage trade offers on steamcommunity.com.

## Setup

1. Find your **Steam ID (SteamID64)**:
   - Go to your Steam profile page
   - If your URL is `https://steamcommunity.com/profiles/76561198012345678`, your Steam ID is `76561198012345678`
   - If your URL uses a vanity name like `https://steamcommunity.com/id/myname`, visit [steamid.io](https://steamid.io) and paste your profile URL to get your SteamID64

2. Get your **Steam Web API key**:
   - Go to [https://steamcommunity.com/dev/apikey](https://steamcommunity.com/dev/apikey)
   - Register a domain name (any value works, e.g., `localhost`)
   - Copy the API key shown on the page

3. Get your **Steam session cookies** (required for trade offers and bypassing inventory rate limits):
   - Log in to [steamcommunity.com](https://steamcommunity.com) in your browser
   - Open Developer Tools (F12) > Application tab > Cookies > `https://steamcommunity.com`
   - Copy the value of the `steamLoginSecure` cookie
   - Copy the value of the `sessionid` cookie

4. Set environment variables:
   ```bash
   export STEAM_ID="your-steamid64"
   export STEAM_API_KEY="your-api-key"
   export STEAM_COOKIES="steamLoginSecure=your-cookie-value"
   export STEAM_SESSION_ID="your-sessionid-cookie-value"
   ```

## Usage

All commands use curl to hit the Steam Community inventory endpoint. The context ID is `2` for all standard game inventories.

### Common App IDs

| Game | App ID |
|------|--------|
| CS2 / CS:GO | 730 |
| Team Fortress 2 | 440 |
| Dota 2 | 570 |
| Rust | 252490 |
| PUBG | 578080 |
| Steam Community (trading cards, etc.) | 753 |

### Get inventory for a game

Replace `$APP_ID` with the game's App ID (see table above). Context ID is `2` for all standard game inventories.

```bash
curl -s "https://steamcommunity.com/inventory/$STEAM_ID/$APP_ID/2?l=english&count=2000" \
  -H "Cookie: $STEAM_COOKIES" | jq '.'
```

### Get CS2 inventory

```bash
curl -s "https://steamcommunity.com/inventory/$STEAM_ID/730/2?l=english&count=2000" \
  -H "Cookie: $STEAM_COOKIES" | jq '.'
```

### Get a summary of items (names and quantities)

```bash
curl -s "https://steamcommunity.com/inventory/$STEAM_ID/730/2?l=english&count=2000" \
  -H "Cookie: $STEAM_COOKIES" | jq '[.descriptions[] | {market_hash_name, type}]'
```

### Get item details (asset IDs mapped to descriptions)

```bash
curl -s "https://steamcommunity.com/inventory/$STEAM_ID/730/2?l=english&count=2000" \
  -H "Cookie: $STEAM_COOKIES" | jq '{assets: [.assets[] | {assetid, classid, instanceid, amount}], total: .total_inventory_count}'
```

### Paginated fetch (for inventories over 2000 items)

The API returns a `last_assetid` field when there are more items. Pass it as `start_assetid` to get the next page:

```bash
curl -s "https://steamcommunity.com/inventory/$STEAM_ID/730/2?l=english&count=2000&start_assetid=$LAST_ASSET_ID" \
  -H "Cookie: $STEAM_COOKIES" | jq '.'
```

Check for more pages by looking at the `more_items` field in the response (equals `1` if there are more).

## Response Format

The inventory endpoint returns JSON with these key fields:

| Field | Description |
|-------|-------------|
| `assets` | Array of items with `appid`, `contextid`, `assetid`, `classid`, `instanceid`, `amount` |
| `descriptions` | Array of item metadata: `market_hash_name`, `name`, `type`, `icon_url`, `tradable`, `marketable`, tags, etc. |
| `total_inventory_count` | Total number of items in the inventory |
| `more_items` | `1` if more pages available (absent otherwise) |
| `last_assetid` | Last asset ID returned; use as `start_assetid` for next page |
| `success` | `1` if the request succeeded |

Assets are linked to descriptions via `classid` + `instanceid`.

## Notes

- **Rate limits**: The community endpoint is heavily rate-limited by IP. Using your own cookies bypasses this for your own inventory. Without cookies, expect IP bans after a few requests (cooldown ~6 hours).
- **Spacing**: If fetching multiple inventories or pages, wait at least 4 seconds between requests.
- **count parameter**: Max value is 5000, but 2000 is recommended to avoid issues.
- **Context ID**: Use `2` for all standard game inventories. Steam Community items (appid 753) also use context ID `6` for some item types.
- **Private profiles**: Inventory must be set to public, or you must be authenticated as the owner.

---

## Trade Offers

Trade offers require an authenticated session (cookies) and a Steam Web API key. The `sessionid` cookie is sent as both a cookie and a POST body parameter.

### Partner identification

Trade partners can be identified two ways:

1. **By SteamID64** — e.g., `76561198012345678`. Convert to a 32-bit account ID for the `partner` field: subtract `76561197960265728` from the SteamID64.
2. **By trade URL** — e.g., `https://steamcommunity.com/tradeoffer/new/?partner=52079950&token=YDAlR4bC`. The `partner` value is the 32-bit account ID. The `token` is needed when the partner is not on your friends list.

### Send a trade offer

This sends items from your inventory to another user (and/or requests items from theirs). Each item requires its `appid`, `contextid`, and `assetid` (obtained from the inventory endpoint above).

The `json_tradeoffer` parameter is a JSON string describing what each side gives. The `me` object holds your items to give; the `them` object holds items you want to receive.

```bash
# Set trade parameters
PARTNER_ACCOUNT_ID="52079950"  # 32-bit account ID (from trade URL or SteamID64 - 76561197960265728)
PARTNER_STEAM_ID="76561198012345678"  # Full SteamID64 (= 76561197960265728 + PARTNER_ACCOUNT_ID)
TRADE_TOKEN="YDAlR4bC"         # From partner's trade URL (omit if partner is on your friends list)
TRADE_MESSAGE="Here's the trade we discussed"

# Build the json_tradeoffer payload
# me.assets = items YOU are giving, them.assets = items you WANT from them
JSON_TRADEOFFER='{
  "newversion": true,
  "version": 4,
  "me": {
    "assets": [
      {"appid": 730, "contextid": "2", "amount": 1, "assetid": "YOUR_ASSET_ID"}
    ],
    "currency": [],
    "ready": false
  },
  "them": {
    "assets": [
      {"appid": 730, "contextid": "2", "amount": 1, "assetid": "THEIR_ASSET_ID"}
    ],
    "currency": [],
    "ready": false
  }
}'

# Send with trade token (non-friend)
curl -s "https://steamcommunity.com/tradeoffer/new/send" \
  -X POST \
  -H "Cookie: sessionid=$STEAM_SESSION_ID; $STEAM_COOKIES" \
  -H "Referer: https://steamcommunity.com/tradeoffer/new/?partner=$PARTNER_ACCOUNT_ID&token=$TRADE_TOKEN" \
  -H "Origin: https://steamcommunity.com" \
  -d "sessionid=$STEAM_SESSION_ID" \
  -d "serverid=1" \
  -d "partner=$PARTNER_STEAM_ID" \
  --data-urlencode "tradeoffermessage=$TRADE_MESSAGE" \
  --data-urlencode "json_tradeoffer=$JSON_TRADEOFFER" \
  -d "captcha=" \
  --data-urlencode "trade_offer_create_params={\"trade_offer_access_token\":\"$TRADE_TOKEN\"}" \
  | jq '.'
```

To send to a **friend** (no token needed), omit the `token` from the Referer and set `trade_offer_create_params` to `{}`:

```bash
curl -s "https://steamcommunity.com/tradeoffer/new/send" \
  -X POST \
  -H "Cookie: sessionid=$STEAM_SESSION_ID; $STEAM_COOKIES" \
  -H "Referer: https://steamcommunity.com/tradeoffer/new/?partner=$PARTNER_ACCOUNT_ID" \
  -H "Origin: https://steamcommunity.com" \
  -d "sessionid=$STEAM_SESSION_ID" \
  -d "serverid=1" \
  -d "partner=$PARTNER_STEAM_ID" \
  --data-urlencode "tradeoffermessage=$TRADE_MESSAGE" \
  --data-urlencode "json_tradeoffer=$JSON_TRADEOFFER" \
  -d "captcha=" \
  -d "trade_offer_create_params={}" \
  | jq '.'
```

The response returns a `tradeofferid` on success:
```json
{"tradeofferid": "1234567890", "needs_mobile_confirmation": true, "needs_email_confirmation": false}
```

#### Sending a gift (no items requested in return)

Set `them.assets` to an empty array `[]`:

```bash
JSON_TRADEOFFER='{
  "newversion": true,
  "version": 4,
  "me": {
    "assets": [
      {"appid": 730, "contextid": "2", "amount": 1, "assetid": "YOUR_ASSET_ID"}
    ],
    "currency": [],
    "ready": false
  },
  "them": {
    "assets": [],
    "currency": [],
    "ready": false
  }
}'
```

### Get trade offers (sent and received)

Uses the official Steam Web API with your API key.

```bash
# Get all active trade offers (sent and received)
curl -s "https://api.steampowered.com/IEconService/GetTradeOffers/v1/?key=$STEAM_API_KEY&get_sent_offers=1&get_received_offers=1&active_only=1&get_descriptions=1&language=english" \
  | jq '.'
```

```bash
# Get only received active offers
curl -s "https://api.steampowered.com/IEconService/GetTradeOffers/v1/?key=$STEAM_API_KEY&get_sent_offers=0&get_received_offers=1&active_only=1&get_descriptions=1&language=english" \
  | jq '.response.trade_offers_received'
```

```bash
# Get only sent active offers
curl -s "https://api.steampowered.com/IEconService/GetTradeOffers/v1/?key=$STEAM_API_KEY&get_sent_offers=1&get_received_offers=0&active_only=1&get_descriptions=1&language=english" \
  | jq '.response.trade_offers_sent'
```

### Get a specific trade offer

```bash
curl -s "https://api.steampowered.com/IEconService/GetTradeOffer/v1/?key=$STEAM_API_KEY&tradeofferid=$TRADE_OFFER_ID&language=english&get_descriptions=1" \
  | jq '.response.offer'
```

### Get trade offers summary (counts)

```bash
curl -s "https://api.steampowered.com/IEconService/GetTradeOffersSummary/v1/?key=$STEAM_API_KEY&time_last_visit=0" \
  | jq '.response'
```

### Accept a trade offer

Accepting uses the Steam Community web endpoint (not the Web API). You need the `tradeofferid` and the partner's SteamID64.

```bash
TRADE_OFFER_ID="1234567890"
PARTNER_STEAM_ID="76561198012345678"

curl -s "https://steamcommunity.com/tradeoffer/$TRADE_OFFER_ID/accept" \
  -X POST \
  -H "Cookie: sessionid=$STEAM_SESSION_ID; $STEAM_COOKIES" \
  -H "Referer: https://steamcommunity.com/tradeoffer/$TRADE_OFFER_ID/" \
  -d "sessionid=$STEAM_SESSION_ID" \
  -d "tradeofferid=$TRADE_OFFER_ID" \
  -d "serverid=1" \
  -d "partner=$PARTNER_STEAM_ID" \
  -d "captcha=" \
  | jq '.'
```

### Cancel a sent trade offer

```bash
curl -s "https://api.steampowered.com/IEconService/CancelTradeOffer/v1/" \
  -X POST \
  -d "key=$STEAM_API_KEY" \
  -d "tradeofferid=$TRADE_OFFER_ID"
```

### Decline a received trade offer

```bash
curl -s "https://api.steampowered.com/IEconService/DeclineTradeOffer/v1/" \
  -X POST \
  -d "key=$STEAM_API_KEY" \
  -d "tradeofferid=$TRADE_OFFER_ID"
```

### Get trade history

```bash
curl -s "https://api.steampowered.com/IEconService/GetTradeHistory/v1/?key=$STEAM_API_KEY&max_trades=10&get_descriptions=1&language=english&include_failed=0" \
  | jq '.response.trades'
```

### Trade offer states reference

| Value | State | Description |
|-------|-------|-------------|
| 1 | Invalid | Invalid or unknown state |
| 2 | Active | Sent, neither party has acted yet |
| 3 | Accepted | Items were exchanged |
| 4 | Countered | Recipient made a counter offer |
| 5 | Expired | Not accepted before the deadline |
| 6 | Canceled | Sender canceled the offer |
| 7 | Declined | Recipient declined the offer |
| 8 | InvalidItems | Items in the offer are no longer available |
| 9 | CreatedNeedsConfirmation | Awaiting mobile/email confirmation before sending |
| 10 | CanceledBySecondFactor | Canceled via email/mobile confirmation |
| 11 | InEscrow | On hold; items removed from both inventories, will deliver automatically |

### Trade offer notes

- **Mobile confirmation**: Most trade offers require Steam Mobile Authenticator confirmation. The send response will indicate `needs_mobile_confirmation: true` if so.
- **Trade holds**: Accounts without Steam Guard Mobile Authenticator enabled for 7+ days will have a 15-day trade hold on all trades.
- **Partner's inventory**: To see what the partner has available to trade, fetch their inventory the same way as yours (using their SteamID64 instead of `$STEAM_ID`). Their inventory must be public or you must be friends.
- **The `partner` field**: The send endpoint expects the full SteamID64 in the `partner` POST parameter. The trade URL's `partner` query parameter is the 32-bit account ID.
- **Cookie expiry**: The `sessionid` and `steamLoginSecure` cookies expire when your Steam session ends. Refresh them from your browser when they stop working.
