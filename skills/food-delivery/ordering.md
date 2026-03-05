# Ordering Workflow — Food Delivery

## Pre-Order Checklist

Before placing any order:

- [ ] User has confirmed the choice
- [ ] Restaurant is currently open
- [ ] Delivery estimate is acceptable
- [ ] Price has been communicated
- [ ] Any coupons/promos applied
- [ ] CRITICAL restrictions noted in order

## Browser Automation Flow

### Step 1: Open Platform
```
Navigate to user's preferred delivery app
- Uber Eats, DoorDash, Grubhub, etc.
- Use logged-in session
```

### Step 2: Find Restaurant
```
Search for exact restaurant name
Verify it's the correct location
Check current delivery time estimate
```

### Step 3: Build Cart
```
Add items user confirmed
Include any customizations:
- "No onions"
- "Extra spicy"
- "Dressing on side"

For CRITICAL allergies, add order note:
"ALLERGY: [allergen]. Please ensure no cross-contamination."
```

### Step 4: Apply Savings
```
Check for:
- Platform promos (banner deals)
- Restaurant promos (% off)
- Applicable coupon codes
- Loyalty rewards
- First-order discounts

Apply best combination
```

### Step 5: Review Cart
```
Verify:
- All items correct
- Customizations noted
- Allergy notes present
- Delivery address correct
- Total matches expectation
```

### Step 6: Get Confirmation
Before checkout, tell user:
```
Ready to order from [Restaurant]:
- [Items listed]
- Subtotal: $X
- Delivery: $X  
- Fees: $X
- Promo applied: -$X
- Total: $X
- ETA: ~X minutes

Confirm to place order?
```

### Step 7: Execute
```
Only after explicit "yes" / "confirm" / "order it":
- Complete checkout
- Wait for confirmation screen
- Capture order number
- Note ETA
```

### Step 8: Report Back
```
"Order confirmed! 
Order #XXXXX from [Restaurant]
ETA: X:XX PM (~X minutes)
Tracking: [link if available]"
```

## Handling Issues

### Restaurant Unavailable
```
"[Restaurant] isn't available right now. 
Similar option: [Alternative] - [why it's similar]
Or I can suggest something else?"
```

### Item Unavailable
```
"[Item] is out of stock.
Substitute with [similar item]?
Or remove it from the order?"
```

### Price Changed
```
"Heads up: total is $X, which is $Y more than expected.
[Reason if known: delivery surge, item price change]
Still want to proceed?"
```

### Long Delivery Time
```
"Delivery estimate is X minutes - longer than usual.
Want to:
1. Order anyway
2. Try [faster alternative]
3. Wait and check later"
```

### Payment Failed
```
"Payment didn't go through.
You'll need to update payment in [App] settings.
Let me know when to retry."
```

## Post-Order

### Track Delivery
If user asks:
- Check order status in app
- Report current stage (preparing, picked up, arriving)
- Update ETA if changed

### Rate & Record
After delivery:
- Ask how it was (quick check)
- Update restaurants.md with rating
- Log in orders.md for variety tracking
- Note any issues

### Handle Problems
If something went wrong:
- Help navigate to support
- Draft complaint message
- Request appropriate compensation
- Update restaurant notes

## Reorder Flow

When user says "same as last time":

1. Check orders.md for most recent
2. Confirm: "Reordering [items] from [restaurant]?"
3. If yes, skip decision phase
4. Go directly to ordering flow
5. Still verify restaurant open + items available

## Scheduled Orders

If user wants to order for later:
```
"Order [X] for delivery at [time]?"

If platform supports scheduling:
- Set delivery window
- Confirm scheduled time

If not:
- Set reminder to order at appropriate time
- "I'll remind you to order at [time - prep time]"
```

## Multi-Platform Comparison

When comparing across platforms:

| Platform | Same Restaurant Check |
|----------|----------------------|
| Uber Eats | Search by name |
| DoorDash | Search by name |
| Grubhub | Search by name |
| Local apps | Check if available |

Compare:
- Base menu prices
- Delivery fee
- Service fee
- Active promos
- Estimated time

Report: "Best deal is [Platform] at $X total (saves $Y vs [other])"
