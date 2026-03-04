# Grubhub Browser Flow

## URL
`https://www.grubhub.com`

## Prerequisites
- Chrome profile with saved Grubhub login, payment method, delivery address
- Verify logged in (account name/icon visible, not "Sign in")

## Flow

### 1. Open & Verify Login
```
browser(action: "open", profile: "chrome", targetUrl: "https://www.grubhub.com")
browser(action: "snapshot")
```
If "Sign in" visible → abort: "Please log into Grubhub in Chrome first"

### 2. Search Restaurant
- Find search bar ("Food, groceries, drinks, etc.")
- Type restaurant name, press Enter
- Wait for results list
- Click matching restaurant
- If not found/closed → abort with reason

### 3. Add Items
For each item:
1. Snapshot menu page (sections by category)
2. Find item by name — Grubhub shows item + price + description
3. Click to open customization modal
4. Select required choices (size, options)
5. Check/uncheck add-ons and extras
6. Adjust quantity if needed
7. Click "Add to bag"

**Tips:**
- Menu organized by: "Most Popular", "Appetizers", "Entrees", etc.
- Required options marked with asterisk or "Required"
- "Special instructions" text box at bottom of modal
- Item price updates as options selected

### 4. Review Cart
- Click bag icon (top-right, shows item count and total)
- Cart slides out from right
- Verify each item name, quantity, options
- Check subtotal

### 5. Checkout
- Click "Continue to checkout"
- Verify delivery address (top of checkout)
- Verify payment method (saved card)
- Review breakdown: subtotal, delivery fee, tax, tip
- Default tip usually preset — adjust if needed
- Note estimated delivery time

### 6. Place Order
- Click "Place your order" (orange button at bottom)
- Wait for confirmation page
- Shows order number and tracking info

Extract: order number, ETA, final total

### 7. Report
```
✅ Order confirmed
   Service: Grubhub
   Restaurant: {name}
   Items: {list}
   ETA: {time}
   Total: ${amount}
```

## Common Elements

| Element | Typical Location |
|---------|------------------|
| Search | Top center, with location dropdown |
| Bag/Cart | Top right, bag icon with count |
| Continue to checkout | Cart drawer bottom, orange button |
| Place your order | Checkout page bottom, orange button |
| Delivery address | Top of checkout page |

## Gotchas
- Grubhub+ membership prompts — dismiss
- "Add utensils" checkbox — leave default
- Donation prompts — skip unless specified
- "Your order qualifies for..." promos — ignore unless requested
- Tip defaults to percentage — use default unless specified
- May show "Fees & estimated tax" collapsed — no action needed
- "Schedule for later" toggle — keep on ASAP unless specified
