# Checkout and Cart

### Single Item

Each product in search results includes a checkout URL pattern with variant IDs. Use the URL directly for a single item purchase.

### Multi-Item Cart (Same Store)

Build cart permalinks by combining variant IDs from the same store:

```
https://store.com/cart/VARIANT_ID_1:QTY,VARIANT_ID_2:QTY
```

For example: `https://www.store.com/cart/47171869376744:1,47171817079016:2`

### Different Stores

Items from different stores require separate checkout links. Note this to the user if they want items from multiple stores.

### Pre-fill Checkout Fields

If you already know the user's email or shipping address, append checkout query parameters to the cart permalink:

```
https://store.com/cart/VARIANT_ID:1?checkout[email]=user@example.com&checkout[shipping_address][city]=Portland
```

Only use information you already have — don't ask just to pre-fill.

### Rules

- Default to linking the product page URL so the user can browse variants and add to cart on their own terms.
- Use checkout URLs when the user explicitly wants to buy right now.
- **Never imply the purchase is complete.** The user clicks through and pays on the store's site.
