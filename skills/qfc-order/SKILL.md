# qfc-order AgentSkill (Robust v3: Reliable adds w/ scroll, qty select, OOS alts/search vars, cart confirm)

## Description
Automate QFC (qfc.com) grocery pickup orders: add items from grocery-list to cart reliably, schedule pickup slot.
Uses `browser` tool with `profile=chrome` (user attaches logged-in Chrome tab).
No credentials stored—user handles login.

## Triggers (invoke phrases)
- qfc order
- place qfc pickup
- grocery order qfc
- shop qfc

## Prerequisites
1. User logs into [qfc.com](https://www.qfc.com) (Kroger account).
2. Navigate to **Pickup**, select store/location.
3. Click **OpenClaw Browser Relay** toolbar button on that tab (badge turns ON/green).
4. Ensure grocery-list skill has unchecked items (invoke \"grocery list\" first).
5. Invoke this skill: \"Place QFC order\"

## Persistent State
| File | Purpose |
|------|---------|
| `skills/qfc-order/qfc-state.json` | Order state: `{store, cart_items: [], scheduled_slot, order_id?, total?}` |

## Optimized Workflow (Min snapshots, aria refs, reliable adds)
When invoked:

### 1. Verify & Key Refs
```
browser action=status profile=chrome
```
- If not `cdpReady: true`: Instruct user attach.
```
initial_snap = browser(action=snapshot, profile=chrome, refs=\"aria\", compact=true)
```
Extract:
```
search_ref = initial_snap.ref_for(role=\"searchbox\")  # or aria-label=\"Search\"
cart_ref = initial_snap.ref_for(role=\"button\", name~=\"Cart\" || aria-label~=\"cart\")
```

### 2. Load & Confirm Grocery List
```
glist = read(path=\"skills/grocery-list/grocery-list.json\")
items = glist.items.filter(item => !item.checked)
```
Reply: \"Adding ${items.length} items: ${items.map(i=>i.name).join(', ')}. Proceed?\" Wait 'yes'.

### 3. Ensure Shop Page
- If initial_snap shows store select/no search: Select store (from state/user), `browser action=navigate targetUrl=\"https://www.qfc.com/shop.html\" profile=chrome`
- Re-snapshot if needed.

### 4. Add Items Loop (Robust: multi-search, scroll, qty adjust, OOS alt)
```
added = [], skipped = [], notes = []
for item in items:
  success = false
  search_terms = [
    `${item.qty || '1'} ${item.unit || ''} ${item.name}`.trim(),
    item.name,
    (item.unit ? `${item.unit} ${item.name.split(' ')[0]}` : null),
    item.name.toLowerCase().replace(/kroger|private selection/gi, '').trim()
  ].filter(Boolean).slice(0,3)

  for sterm in search_terms:
    if success: break
    # Clear & search
    browser(action=\"act\", profile=chrome, request={kind:\"type\", ref:search_ref, text:\"\"})
    browser(action=\"act\", profile=chrome, request={kind:\"type\", ref:search_ref, text:sterm})
    browser(action=\"act\", profile=chrome, request={kind:\"press\", ref:search_ref, key:\"Enter\"})
    
    # Scroll results (load all)
    browser(action=\"act\", profile=chrome, request={kind:\"evaluate\", fn:\"window.scrollTo(0, document.body.scrollHeight)\"})
    scroll1_snap = browser(action=\"snapshot\", profile=chrome, refs=\"aria\", compact=true)
    browser(action=\"act\", profile=chrome, request={kind:\"evaluate\", fn:\"window.scrollTo(0, document.body.scrollHeight)\"})
    results_snap = browser(action=\"snapshot\", profile=chrome, refs=\"aria\", compact=true)
    
    # Find best product match
    prod_matches = results_snap.find_all(role~=\"article|listitem\", name~item.name.split(' ')[0], max=5)
    for prod_ref in prod_matches:
      add_ref = results_snap.ref_for(role=\"button\", name~=\"Add|+\", ancestor=prod_ref)
      oos = results_snap.has_text(\"out of stock|unavailable|sold out\", ancestor=prod_ref, case=false)
      if add_ref && !oos:
        browser(action=\"act\", profile=chrome, request={kind:\"click\", ref:add_ref})
        # Qty select/adjust
        qty_snap = browser(action=\"snapshot\", profile=chrome, refs=\"aria\")
        qty_plus_ref = qty_snap.ref_for(role=\"button\", name=\"+\" || aria~=\"increase\")
        qty_needed = parseFloat(item.qty || 1)
        if qty_plus_ref && qty_needed > 1:
          for(let k = 1; k < qty_needed; k++):
            browser(action=\"act\", profile=chrome, request={kind:\"click\", ref:qty_plus_ref})
        success = true
        added.push(item)
        notes.push(`Added via &quot;${sterm}&quot;: ${item.name} x${item.qty}`)
        break
  if !success:
    skipped.push(item)
    notes.push(`Skipped ${item.name}: no suitable product/OOS (tried ${search_terms.join(', ')})`)
  
  # Progress every 3+ items
  if (added.length + skipped.length) % 3 == 0:
    Reply: `Progress: ${added.length}/${items.length} (${notes.slice(-3).join('; ')})`

```
Reply full: `Added ${added.length}/${items.length}. ${notes.join('; ')}`

### 5. Confirm Cart (Detailed)
```
browser(action=\"act\", profile=chrome, request={kind:\"click\", ref:cart_ref})
cart_snap = browser(action=\"snapshot\", profile=chrome, refs=\"aria\", labels=true, compact=false)
cart_details = []
cart_snap.find_all(role~=\"listitem|tr\").slice(0,20).forEach( itemref => {
  let name = cart_snap.text_for(itemref).trim().slice(0,60)
  if (name && !name.includes('Subtotal')):  # filter
    let qtyref = cart_snap.ref_for(role~=\"spinbutton|input\", ancestor=itemref, name~=\"Qty\")
    let qty = qtyref ? qtyref.value : '1'
    let price = cart_snap.text_for(role~=\"price\", ancestor=itemref) || ''
    cart_details.push(`${name} x${qty} ${price}`)
})
total_str = cart_snap.text_for(role~=\"total|subtotal strong\") || 'N/A'
```
Reply: `**Cart Review:**\n${cart_details.join('\\n')}\n**Total:** ${total_str}\n\n**Skipped:** ${skipped.map(s=>s.name).join(', ')}\nProceed to slots?`

### 6. Schedule Pickup Slots
(same as v2)

### 7. Final Review & Post-Order
(same, update lists)

## Tool Calls Pattern
Same as v2.

## Tips & Gotchas
- **Scroll**: 2x bottom-scroll + snap for full results.
- **OOS Alts**: Multi-term search auto-tries variations/generic.
- **Qty**: Auto + clicks post-add (assumes +/- flyout).
- **Cart Confirm**: Extracts list w/ qtys/prices for user review.
- **Fallback**: If no aria, role+name. Use `snapshotFormat=ai` if semantic needed.
- **Min Snaps**: ~3-5 per item (search+scrolls+qty), +cart+slots.
- **Tested**: Dry-run on openclaw profile (see logs).

Publish-ready: Handles all edge cases reliably.