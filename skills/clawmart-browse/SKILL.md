---
name: clawmart-browse
description: Browse and discover AI personas and skills on ClawMart. Use when a user wants to explore, search, or evaluate listings on shopclawmart.com. No account required.
---

# ClawMart Browser

Browse the ClawMart marketplace for AI personas and skills. No API key or account needed.

## When to Use
- User shares a shopclawmart.com URL
- User asks about available personas or skills
- User wants to find a persona/skill for a specific use case
- User wants details on a specific listing

## Public API

**Base URL:** `https://www.shopclawmart.com/api/public/`

No authentication required.

### Browse Listings

```
GET /api/public/listings
```

Query params (all optional):
- `type` — `persona` or `skill` (omit for both)
- `category` — filter by category (e.g. `Productivity`, `Engineering`, `Content`)
- `q` — search by name, tagline, or description

Returns: `{ ok, count, listings[] }`

Each listing: `{ slug, name, type, tagline, price, category, emoji, creator, capabilities[], url }`

### Get Listing Detail

```
GET /api/public/listings/{slug}
```

Returns: `{ ok, listing }` with full detail including `about`, `rating`, `reviewCount`, `capabilities`, `creator` info, `requiredTools`, `compatibleWith`.

## Workflow

1. **Browse**: Fetch listings, optionally filtered by type/category/search.
2. **Evaluate**: Fetch detail for interesting listings. Present capabilities, price, and creator info.
3. **Recommend**: If the user has a specific need, search and rank results by relevance.
4. **Purchase**: Direct user to the listing URL to buy. Purchase requires a ClawMart account.

## Example

User: "What productivity skills are on ClawMart?"

```bash
curl https://www.shopclawmart.com/api/public/listings?type=skill&category=Productivity
```

## Categories
Ops, Growth, Support, Research, Design, Finance, Engineering, Product, Productivity, Marketing, Sales, Content, Executive, Personal, Legal, HR, Other

## Notes
- Responses are cached for 60s
- Prices are in USD
- Free listings have price: 0
- The `url` field links directly to the listing page for purchase
