---
name: steamcommunity
description: Retrieves Steam inventory data for a user from steamcommunity.com
homepage: https://steamcommunity.com/dev
metadata: {"clawdbot":{"emoji":"\u2694","requires":{"bins":["jq","curl"],"env":["STEAM_ID","STEAM_COOKIES"]}}}
---


# Steam Community Inventory Skill

Retrieve and browse a Steam user's inventory from steamcommunity.com.

## Setup

1. Find your **Steam ID (SteamID64)**:
   - Go to your Steam profile page
   - If your URL is `https://steamcommunity.com/profiles/76561198012345678`, your Steam ID is `76561198012345678`
   - If your URL uses a vanity name like `https://steamcommunity.com/id/myname`, visit [steamid.io](https://steamid.io) and paste your profile URL to get your SteamID64

2. Get your **Steam session cookies** (required to bypass rate limits when fetching your own inventory):
   - Log in to [steamcommunity.com](https://steamcommunity.com) in your browser
   - Open Developer Tools (F12) > Application tab > Cookies > `https://steamcommunity.com`
   - Copy the value of the `steamLoginSecure` cookie

3. Set environment variables:
   ```bash
   export STEAM_ID="your-steamid64"
   export STEAM_COOKIES="steamLoginSecure=your-cookie-value"
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
