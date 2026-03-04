---
name: kroger
description: Search Kroger products and add items to a Kroger cart via the Kroger API. Use when a user asks to find groceries, add items to their Kroger cart, look up Kroger store locations, or manage a Kroger shopping list. Supports product search, cart management, and store lookup by zip code.
---

# Kroger

Search products, add to cart, and find store locations via the Kroger public API.

## Prerequisites

- Kroger developer account at https://developer.kroger.com
- Registered application with **Product** and **Cart** API access
- OAuth redirect URI configured in the Kroger app settings

## Environment Variables

Set these before using:

```bash
export KROGER_CLIENT_ID="your-client-id"
export KROGER_CLIENT_SECRET="your-client-secret"
```

Optional:
- `KROGER_TOKEN_FILE` — token storage path (default: `~/.kroger-tokens.json`)
- `KROGER_REDIRECT_URI` — OAuth callback URL (default: `http://localhost:8888/callback`)
- `KROGER_LOCATION_ID` — store ID for location-specific product availability

## Setup (One-Time)

### 1. Register a Kroger Developer App

1. Go to https://developer.kroger.com
2. Create an application
3. Enable **Product** and **Cart** scopes
4. Set redirect URI to `http://localhost:8888/callback`
5. Note Client ID and Client Secret

### 2. Authenticate

Run the auth flow — opens a browser for Kroger login:

```bash
scripts/kroger.sh auth
```

If the redirect URI isn't localhost (e.g., cloud-hosted), use the manual flow:
1. Open the `AUTH_URL` printed by `scripts/kroger.sh auth`
2. Log in at Kroger
3. Copy the redirected URL (even if the page errors)
4. Extract the `code` parameter and run:

```bash
scripts/kroger.sh exchange <code>
```

Tokens auto-refresh. Re-auth only needed if refresh token expires.

## Actions

### Search products

```bash
scripts/kroger.sh search "cannellini beans"
```

Returns up to 5 results with product IDs, descriptions, and brands.

### Add to cart

```bash
scripts/kroger.sh add <productId> [quantity]
```

Requires prior OAuth login. Quantity defaults to 1.

### Find nearby stores

```bash
scripts/kroger.sh locations <zipcode>
```

Returns up to 5 stores with location IDs. Set `KROGER_LOCATION_ID` to filter product search by store.

### Check auth status

```bash
scripts/kroger.sh token
```

## Workflow: Grocery List → Cart

Typical flow for adding a grocery list to Kroger:

1. Search each item: `scripts/kroger.sh search "<item>"`
2. Pick the best match from results
3. Add to cart: `scripts/kroger.sh add <productId> <qty>`
4. Repeat for all items

When adding many items, batch all searches first, then confirm selections with the user, then add all to cart.
