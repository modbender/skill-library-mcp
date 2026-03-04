# DoorDash Browser Flow

## URL
`https://www.doordash.com`

## Prerequisites
- Chrome profile with saved DoorDash login, payment method, delivery address
- Verify logged in (account icon visible, not "Sign In" button)

## Flow

### 1. Open & Verify Login
```
browser(action: "open", profile: "chrome", targetUrl: "https://www.doordash.com")
browser(action: "snapshot")
```
If "Sign In" visible → abort: "Please log into DoorDash in Chrome first"

### 2. Search Restaurant
- Find search input (usually prominent at top)
- Type restaurant name, press Enter
- Wait for results, click matching restaurant
- If not found/closed → abort with reason

### 3. Add Items
For each item:
1. Snapshot menu page
2. Find item by name (semantic match: "burrito bowl" → "Bowl", "Burrito Bowl")
3. Click to open customization modal
4. Select required options (size, protein, base)
5. Toggle toppings/extras as specified
6. Click "Add to Order"

**Tips:**
- Customizations appear after clicking base item
- Watch for "Required" sections — must select something
- "Add to Order" button usually at modal bottom

### 4. Review Cart
- Click cart/bag icon (usually top-right, shows item count)
- Snapshot cart contents
- Verify each item and customization matches request
- Note any discrepancies

### 5. Checkout
- Click "Checkout" or "Continue"
- Verify delivery address (use saved default)
- Verify payment method (use saved default)
- Note delivery estimate and total

### 6. Place Order
- Click "Place Order" button
- Wait for confirmation page
- Extract: confirmation number, ETA, final total

### 7. Report
```
✅ Order confirmed
   Service: DoorDash
   Restaurant: {name}
   Items: {list}
   ETA: {time}
   Total: ${amount}
```

## Common Elements

| Element | Typical Location |
|---------|------------------|
| Search | Top center, "Search for restaurants..." |
| Cart | Top right, bag icon with count |
| Checkout | Cart drawer bottom, red button |
| Place Order | Checkout page bottom, red button |

## Gotchas
- Promo modals may appear — dismiss or skip
- Tip selection screen — use default or preset amount
- "Leave at door" instructions — use saved preference
- Item unavailable popup — acknowledge and continue or substitute
