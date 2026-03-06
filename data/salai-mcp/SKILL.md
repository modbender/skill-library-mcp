---
name: salai-mcp
description: Israeli grocery shopping and price-comparison assistant over Salai MCP. Use when you need product search, autocomplete, cross-retailer price comparison, cart management, store discovery, retailer discovery, and complementary product recommendations through the Salai remote MCP endpoint.
metadata:
  openclaw:
    primaryEnv: SALAI_API_KEY
    requires:
      env:
        - name: SALAI_API_KEY
          required: true
          secret: true
          description: Salai user API key (available in Profile after beta approval).
---

# Salai MCP Skill

Use Salai's remote MCP server for Israeli grocery discovery, comparison, and cart workflows.

## Access requirements

- Salai MCP is currently in **beta**.
- Users must register to the beta program and be approved.
- Only approved beta users can generate an API key from Salai Profile and use MCP tools.
- Registration: go to `https://app.salai.co.il`, create an account (Sign up), and wait for beta approval.
- Beta access contact: `beta@salai.co.il`

## Connection

- Endpoint: `https://mcp.salai.co.il/mcp`
- Auth: send a user API key from Salai Profile using either:
  - `Authorization: Bearer <SALAI_API_KEY>`
  - `X-API-Key: <SALAI_API_KEY>`

Use the full `/mcp` endpoint directly for best client compatibility.

## Tools

- Discovery:
  - `get_stores`
  - `get_retailers`
- Search:
  - `autocomplete_products`
  - `search_products`
- Pricing and comparison:
  - `get_product_prices`
  - `compare_prices`
  - `cart_of_israel`
- Cart management:
  - `get_cart`
  - `get_my_cart`
  - `update_cart_items`
  - `add_cart_item`
  - `remove_cart_item`
  - `delete_cart`
- Recommendations:
  - `get_complementary_recommendations`

## Recommended workflow

1. Resolve products quickly with `autocomplete_products` (`method: text` first, then `semantic` if empty).
2. Use `search_products` for richer semantic results and recommendations.
3. Build/modify the active user cart with `get_my_cart`, `add_cart_item`, `update_cart_items`, and `remove_cart_item`.
4. Compare total cost across retailers with `compare_prices`.
5. Use `cart_of_israel` for one-shot comparison of the default Cart of Israel list.

## Store scope conventions

When filtering by store, prefer `retailerId + storeId`.

`subChainId` may be accepted by some tools for backward compatibility, but is deprecated for store identity.

## Error handling

- If access is denied, instruct the user to complete beta signup and wait for approval.
- If an auth error occurs, request a valid Salai API key and retry.
- If a product is not found in one store, continue comparison with available alternatives.
- For ambiguous product names, call `autocomplete_products` before cart mutations.

## Security

- Never log or expose API keys in output.
- Treat all API keys as secrets.
