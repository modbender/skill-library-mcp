# Uber Eats Browser Flow

## URL
`https://www.ubereats.com`

## Prerequisites
- Chrome profile with saved Uber account, payment method, delivery address
- Verify logged in (profile icon visible, not "Sign in" button)
- Note: Uses same Uber account as rideshare

## Flow

### 1. Open & Verify Login
```
browser(action: "open", profile: "chrome", targetUrl: "https://www.ubereats.com")
browser(action: "snapshot")
```
If "Sign in" visible → abort: "Please log into Uber Eats in Chrome first"

### 2. Search Restaurant
- Find search bar (top of page, "Search Uber Eats")
- Type restaurant name, press Enter
- Wait for results grid
- Click matching restaurant card
- If not found/closed → abort with reason

### 3. Add Items
For each item:
1. Snapshot menu page (organized by category sections)
2. Find item by name (may need to scroll/expand categories)
3. Click to open item detail/customization modal
4. Select required options (size, combos, etc.)
5. Check/uncheck customizations
6. Click "Add to order" (usually shows price)

**Tips:**
- Menu often grouped: "Popular Items", "Combos", "Entrees", etc.
- "Required" tag on option groups that must be selected
- Quantity selector in modal
- Some items have "Frequently bought together" suggestions — skip unless requested

### 4. Review Cart
- Click cart button (right side or bottom of screen, shows total)
- Cart often appears as slide-out drawer
- Verify each item, quantity, customizations
- Note subtotal

### 5. Checkout
- Click "Go to checkout" or "Next"
- Verify delivery address at top
- Verify payment method
- Review fees breakdown (delivery fee, service fee, taxes)
- Note estimated delivery time
- Check tip amount (adjust if needed)

### 6. Place Order
- Click "Place order" button (usually green/black at bottom)
- Wait for order confirmation screen
- May show map with driver assignment

Extract: order number, ETA, final total

### 7. Report
```
✅ Order confirmed
   Service: Uber Eats
   Restaurant: {name}
   Items: {list}
   ETA: {time}
   Total: ${amount}
```

## Common Elements

| Element | Typical Location |
|---------|------------------|
| Search | Top center, magnifying glass icon |
| Cart | Right side floating button, or bottom bar on mobile |
| Go to checkout | Cart drawer bottom |
| Place order | Checkout page bottom, dark button |
| Address | Top of checkout, with "Deliver to" label |

## Gotchas
- "Group order" prompts — decline unless specified
- Schedule for later option — ignore, order for ASAP unless specified
- Priority delivery upsell — skip unless requested
- "Add more items" suggestions — skip
- Driver tip defaults to percentage — use default unless specified
- May prompt for phone number verification — complete if required
