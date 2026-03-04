---
name: CurlShip Directory Submission
description: Submit products to CurlShip, the bot-friendly SaaS directory. One curl command to list your product with OG tag scraping, badge-based dofollow links, and tier upgrades.
version: 1.0.0
homepage: https://curlship.com
credentials_required: false
---

# CurlShip — Bot-Friendly SaaS Directory

## Overview

Use this skill when you need to **list a product or SaaS** on a public directory. CurlShip is designed for bots and CLI tools — submit with a single API call, get back OG-scraped listing details, and optionally upgrade to paid tiers for higher placement.

## Quick Reference

**API Base URL:** `https://curlship.com`
**Homepage:** `https://curlship.com`
**Pricing:** `https://curlship.com/pricing`

**Single-line Use Cases:**

- Submit a product URL to be listed in the directory
- Check all current directory listings
- Upgrade a listing to a paid tier (Bronze/Silver/Gold/Platinum)
- Get the CurlShip badge HTML for dofollow links

## What this skill does

- Sends HTTPS requests to the CurlShip API
- Uses `POST /api/submit` to add a new listing (auto-scrapes OG tags)
- Uses `GET /api/listings` to retrieve all active listings
- Uses `POST /api/upgrade` to get a checkout URL for paid tier upgrades
- Returns structured JSON responses with listing details

## What this skill does NOT do

- Does not require authentication or API keys
- Does not make payments directly — upgrade returns a checkout URL for the user
- Does not modify any local files or system settings

## Endpoints

### 1. Submit a Listing

**`POST /api/submit`** — Add a product to the directory.

```bash
curl -X POST https://curlship.com/api/submit \
  -H "Content-Type: application/json" \
  -d '{"url": "https://yourapp.com", "email": "you@email.com"}'
```

**Request Fields:**

- `url` (required): Product URL starting with `http`. Must be a public, non-private address.
- `email` (required): Contact email for the listing owner.

**Example Response (201 Created):**

```json
{
  "ok": true,
  "message": "Listed! Add a badge for a dofollow link.",
  "listing": {
    "id": 42,
    "url": "https://yourapp.com",
    "tier": "free",
    "title": "YourApp - Build Faster",
    "description": "The fastest way to ship your next SaaS.",
    "image": "https://yourapp.com/og-image.png",
    "has_badge": false
  },
  "badge_html": "<a href=\"https://curlship.com\"><img src=\"https://curlship.com/badge\" alt=\"Listed on CurlShip\" /></a>"
}
```

**Error Responses:**

- `400` — Missing/invalid URL or email
- `403` — URL is on a blocklist (adult/phishing/malware)
- `429` — Rate limit exceeded (max 10 submissions per hour per IP)

**Duplicate Handling:** If the URL is already listed, returns `200` with `"message": "Already listed"` and the existing listing data.

### 2. Get All Listings

**`GET /api/listings`** — Retrieve all active directory listings.

```bash
curl https://curlship.com/api/listings
```

**Example Response:**

```json
{
  "ok": true,
  "listings": [
    {
      "id": 1,
      "url": "https://example.com",
      "tier": "gold",
      "title": "Example App",
      "description": "A great example application.",
      "image": "https://example.com/og.png",
      "has_badge": true
    }
  ]
}
```

Listings are sorted by tier (Platinum > Gold > Silver > Bronze > Free).

### 3. Upgrade a Listing

**`POST /api/upgrade`** — Get a payment checkout URL to upgrade a listing's tier.

```bash
curl -X POST https://curlship.com/api/upgrade \
  -H "Content-Type: application/json" \
  -d '{"url": "https://yourapp.com", "tier": "gold"}'
```

**Request Fields:**

- `url` (required): The URL of an existing listing.
- `tier` (required): One of `platinum`, `gold`, `silver`, `bronze`.

**Example Response:**

```json
{
  "ok": true,
  "checkout_url": "https://checkout.dodopayments.com/..."
}
```

**Error Responses:**

- `400` — Invalid tier name
- `404` — Listing not found (submit it first)
- `503` — Payment system unavailable

**Important:** The listing must already exist. Submit first, then upgrade.

### 4. Badge SVG

**`GET /badge`** — Returns the CurlShip badge as an SVG image.

Place this badge on your site to automatically earn a **dofollow** link:

```html
<a href="https://curlship.com">
  <img src="https://curlship.com/badge" alt="Listed on CurlShip" />
</a>
```

Badge presence is auto-checked hourly. Any `<a>` tag linking to `curlship.com` qualifies.

## Tiers & Pricing

| Tier | Price | Benefits |
|------|-------|----------|
| Platinum | $149/mo | Top of directory, dofollow link, priority OG refresh |
| Gold | $49/mo | Above Silver & Bronze, dofollow link |
| Silver | $15/mo | Above Bronze & Free, dofollow link |
| Bronze | $1/mo | Above Free tier, dofollow link |
| Free | $0 | Listed in Free section, nofollow by default |

**Dofollow rules:**
- Paid tiers (any) get dofollow automatically
- Free tier gets dofollow by placing a CurlShip badge on your site

## Typical Agent Workflow

1. **Submit** the product URL and email via `POST /api/submit`
2. **Check** the response for the listing details and badge HTML
3. **Optionally upgrade** via `POST /api/upgrade` and present the checkout URL to the user
4. **Add the badge** HTML to the product's website for a dofollow link (free tier)

## Rate Limits

- Maximum 10 submissions per hour per IP address
- No rate limit on `GET /api/listings`

## Security & Content Policy

- URLs pointing to private/reserved IP addresses are rejected (SSRF protection)
- URLs on known adult/phishing/malware blocklists are rejected
- All API responses include `x-robots-tag: noindex`
