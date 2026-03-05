---
name: csfloat
description: Queries csfloat.com for data on skins
homepage: https://docs.csfloat.com/#introduction
metadata: {"clawdbot":{"emoji":"𝒇","requires":{"bins":["jq"],"env":["CSFLOAT_API_KEY"]}}}
---


# CSFloat Skill

Query CSFloat skins data directly from Clawdbot.

## Setup

1. Get your API key: [https://csfloat.com/profile](https://csfloat.com/profile), under the Developer tab
2. Generate a key by pressing "New Key"
3. Set environment variables:
   ```bash
   export CSFLOAT_API_KEY="your-api-key"
   ```

## Usage

All commands use curl to hit the Trello REST API. Use the API key with the "Authorization: " header.

### Get all listings
```bash
curl -s "https://csfloat.com/api/v1/listings" --header "Authorization: $CSFLOAT_API_KEY" --header "Content-Type: application/json" | jq '.data.[] | { "id", "item", "price" }'
```

### Get specific listing
```bash
curl -s https://csfloat.com/api/v1/listings/$LISTING_ID --header "Authorization: $CSFLOAT_API_KEY" --header "Content-Type: application/json"
```

### Create a listing
```bash
curl -X POST "https://csfloat.com/api/v1/listings" \
-H "Authorization: $LISTING_ID; Content-Type: application/json" \
-d '{"asset_id": 21078095468, "type": "buy_now", "price": 8900, "description": "Just for show", "private": false}'
```

Creating a listing uses the following body parameters:

| Parameter | Default | Description | Optional |
|-------------|----------|--------------|-----------|
| type | buy_now | Either `buy_now` or `auction` | YES |
| asset_id | | The ID of the item to list | NO |
| price | | Either the `buy_now` price or the current bid or reserve price on an `auction` | NO (if `buy_now`) |
| max_offer_discount | Set in user profile | `buy_now` max discount for an offer. This will override the default set in your profile. | YES |
| `reserve_price` | | `auction` start price | NO (if `auction`) |
| duration_days | | `auction` duration in days. Can be: 1, 3, 5, 7, or 14 | NO (if `auction`) |
| description | | User defined description. Max characters of 180. | YES |
| private | false | If true, will hide listings from public searches | YES |

## Notes

- Asset ids are from Steam

