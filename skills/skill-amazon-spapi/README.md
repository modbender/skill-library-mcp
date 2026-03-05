# skill-amazon-spapi

> **OpenClaw Agent Skill** — Full Amazon SP-API integration. Fetch orders, check FBA inventory, manage listings and pricing — all from your AI agent, zero manual Seller Central work.

---

## What It Does

| Script | What it does |
|--------|-------------|
| `auth.js` | Test SP-API connection, list marketplace participations |
| `orders.js` | Fetch recent orders, filter by status/date, export to JSON |
| `inventory.js` | Check FBA fulfillable stock per SKU |
| `listings.js` | Get listing details, update pricing |

---

## Quick Start

```bash
# 1. Install dependency
npm install amazon-sp-api

# 2. Create credentials file: amazon-sp-api.json
{
  "lwaClientId": "amzn1.application-oa2-client.YOUR_ID",
  "lwaClientSecret": "YOUR_SECRET",
  "refreshToken": "Atzr|YOUR_TOKEN",
  "region": "eu",
  "marketplace": "YOUR_MARKETPLACE_ID",
  "sellerId": "YOUR_SELLER_ID"
}

# 3. Test connection
node scripts/auth.js

# 4. Pull today's orders
node scripts/orders.js --list --days 1

# 5. Check inventory
node scripts/inventory.js
```

---

## Usage Examples

```bash
# Orders
node scripts/orders.js --list --days 7
node scripts/orders.js --list --days 30 --status Unshipped --out unshipped.json
node scripts/orders.js --get 123-4567890-1234567

# Inventory
node scripts/inventory.js --sku "MY-SKU"
node scripts/inventory.js --out inventory.json

# Listings
node scripts/listings.js --get "MY-SKU"
node scripts/listings.js --update "MY-SKU" --price 49.99 --currency USD
```

---

## Marketplace IDs (Common)

| Country | Marketplace ID |
|---------|---------------|
| US | `ATVPDKIKX0DER` |
| UAE | `A2VIGQ35RCS4UG` |
| UK | `A1F83G8C2ARO7P` |
| DE | `A1PA6795UKMFR9` |
| SA | `A17E79C6D8DWNP` |

> Full list: [Amazon Marketplace IDs](https://developer-docs.amazon.com/sp-api/docs/marketplace-ids)

---

## Credentials Setup

1. Go to [Seller Central > Apps & Services > Develop Apps](https://sellercentral.amazon.com/apps/develop)
2. Create a new SP-API application
3. Generate LWA credentials (Client ID + Secret)
4. Authorize and get your Refresh Token
5. Find your Seller ID under Account Info

---

## Part of the Zero2AI Skill Library

Built and battle-tested in production. Part of a growing open-source library of AI agent skills for e-commerce automation.

- 🔗 [skill-amazon-ads-optimizer](https://github.com/Zero2Ai-hub/skill-amazon-ads-optimizer) — Campaign & bid management
- 🔗 [skill-amazon-listing-optimizer](https://github.com/Zero2Ai-hub/skill-amazon-listing-optimizer) — Image audit & fix

---

**Built by [Zero2AI](https://zeerotoai.com) · Published on [ClawHub](https://clawhub.ai)**
