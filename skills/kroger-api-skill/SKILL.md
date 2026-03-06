---
name: Kroger/QFC API Skill
description: "Skill for searching Kroger/QFC products, managing cart, checking
  pickup availability, and creating pickup orders. Uses official Kroger API. QFC
  chain ID: 213."
---

# Kroger/QFC API Skill

## Overview
Skill for searching Kroger/QFC products, managing cart, checking pickup availability, and creating pickup orders.
Uses official Kroger API. QFC chain ID: 213.

## Setup
1. Sign up at [developer.kroger.com](https://developer.kroger.com), create app.
2. Add redirect URI e.g. http://localhost
3. Scopes: `product.compact locations.read fulfillment.readwrite orders.pickup.create`
4. Edit `state.json`: add `client_id`, `client_secret`, `chain_id`: \"213\"
5. OAuth:
   - `python3 scripts/client.py --state state.json oauth-url`
   - Visit URL, login, authorize.
   - Copy code from redirect (e.g. http://localhost?code=ABC123)
   - `python3 scripts/client.py --state state.json oauth-exchange ABC123`

## Usage (via exec)
Run from workspace root:

### Search products
```
python3 kroger-api.skill/scripts/client.py search \"milk\" --chain-id 213 --limit 5
```
Output: JSON products with `id` (UPC), `attributes.description`, `attributes.brand` etc.

### Find locations
```
python3 kroger-api.skill/scripts/client.py locations 98101 --chain-id 213
```
Output: locations with `id`, `attributes.address.addressLine1` etc.

### Cart (local)
```
python3 kroger-api.skill/scripts/client.py cart-add 0001111101001 2  # UPC qty
python3 kroger-api.skill/scripts/client.py cart-get
python3 kroger-api.skill/scripts/client.py cart-clear
```

### Check availability
```
python3 kroger-api.skill/scripts/client.py availability LOC123 --items '[{&quot;upc&quot;:&quot;UPC&quot;,&quot;quantity&quot;:1}]'
```

### Create order
```
python3 kroger-api.skill/scripts/client.py order-create LOC123 \&quot;2026-02-14T10:00:00Z\&quot; --items '[{&quot;upc&quot;:&quot;UPC&quot;,&quot;quantity&quot;:1}]'
```

### Grocery list integration
Create `grocery-list.txt`:
```
milk
bread
eggs
```
```
python3 kroger-api.skill/scripts/client.py grocery --zip 98101
```
Lists items & locations. Agent: for each item search, pick UPC (e.g. first result), add_to_cart, then availability, order.

### Agent Workflow Example
1. User: &quot;Add milk and eggs to Kroger cart&quot;
2. Search &quot;milk&quot;, pick UPC1, cart-add
3. Search &quot;eggs&quot;, pick UPC2, cart-add
4. User: &quot;Find QFC near 98101&quot; → locations
5. Set location-set LOC
6. cart-get → items
7. availability → pick slot
8. order-create with slot time.

## State
`state.json`: tokens, cart, location_id.

## Notes
- Endpoints based on Kroger API docs. Verify at developer.kroger.com/reference
- UPC from products.id
- Pickup datetime: ISO 8601 UTC
- Errors: check API response
- Token auto-refreshes.

Package as kroger-api.skill/
