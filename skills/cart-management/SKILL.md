---
name: cart-management
description: "React cart state management: duplicate prevention, localStorage persistence, CartContext patterns. Use when building or fixing shopping carts, product lists, or cart-related UI."
---

# Cart Management Skill

Patterns for React cart state: duplicate prevention, persistence, context design.

## Duplicate Prevention

- Track product IDs in CartContext (separate state or derived from cartItems)
- Check `productIdsInCart.includes(item.id)` before add
- Centralize logic in context, not in ProductCard or child components

## Persistence (localStorage)

- Initialize cart state from `localStorage.getItem('cart')` on mount
- Persist on every add/remove: `localStorage.setItem('cart', JSON.stringify(cartItems))`
- Sync productIdsInCart if used: `localStorage.setItem('cart_ids', JSON.stringify(ids))`
- Prevents duplicates across sessions (refresh, new tab)

## CartContext Pattern

```tsx
const addToCart = (item: CartItem) => {
  if (!productIdsInCart.includes(item.id)) {
    setCartItems(prev => [...prev, item]);
    setProductIdsInCart(prev => [...prev, item.id]);
    localStorage.setItem('cart', JSON.stringify([...cartItems, item]));
  }
};
```

## Anti-Patterns

- Don't add to cart in useEffect on ProductCard mount (causes duplicates)
- Don't duplicate logic in multiple components – use context
- Add backend validation as fallback for data integrity

## Quantity Updates

For same-product quantity: use `cartItems.map()` to update item.quantity, don't create duplicate entries.
