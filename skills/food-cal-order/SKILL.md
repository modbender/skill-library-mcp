---
name: food-cal-order
description: Order food delivery via browser automation, triggered by calendar events. Supports two modes — Direct (specific service + restaurant) and Discovery (criteria-based search across all services). Services include DoorDash, Uber Eats, Grubhub. Use when a calendar event matches food ordering patterns. Spawns sub-agents for browser control.
---

# Food Calendar Order

Place food delivery orders via browser automation, triggered by calendar events.

## Security & Prerequisites

> **Read before using this skill.**

- **Chrome profile access:** This skill opens your local Chrome profile, which contains your saved logins, payment methods, and delivery addresses. Sub-agents will interact with these directly.
- **Real charges:** Confirming an order will charge your saved payment method. There is no sandbox — this is a live transaction.
- **Trusted trigger source:** Only calendar events you created yourself should trigger this skill. Events created or modified by others (shared calendars, external invites) may not reflect your intent. Verify event origin before proceeding.
- **Mandatory confirmation:** A pre-checkout summary will be presented before any order is placed. You must explicitly confirm with "yes" — any other response aborts the order.

## Modes

### Direct Mode
Specific service and restaurant provided.

```
Title: "DoorDash: Chipotle"
Description: "burrito bowl, chicken, guac"
```

### Discovery Mode
Criteria-based; searches all services to find best match.

```
Title: "Thai food, high ratings, under $30, food for 2"
Description: "no shellfish, prefer noodles"
```

## Calendar Event Parsing

**Always read both the title AND description** of the calendar event.

> **Trust warning:** Only process events that appear to have been created by the calendar owner. If an event was recently modified by an external party (e.g., a shared calendar attendee or external invite), note this explicitly in the pre-confirmation summary so the user can assess before confirming.

### Title → Mode + Target

| Pattern | Mode |
|---------|------|
| `{Service}: {Restaurant}` | Direct |
| Cuisine/criteria only | Discovery |

### Description → Order Details + Constraints

The description carries two kinds of info:

1. **Order details** — what to order (items, quantity, servings)
2. **Constraints** — things that MUST be honored, safety-critical

Parse the description and extract:

| Field | Examples | Priority |
|-------|----------|----------|
| `items` | "burrito bowl, chicken, guac" | Order details |
| `servings` | "food for 2", "feeds 4" | Order details |
| `allergies` | "nut allergy", "allergic to shellfish" | **CRITICAL — never violate** |
| `dietary` | "vegetarian", "halal", "gluten-free", "no pork" | **CRITICAL — never violate** |
| `preferences` | "prefer noodles", "extra spicy", "no onions" | Best-effort |
| `budget` | "under $30", "keep it cheap" | Constraint |
| `delivery_notes` | "gate code 1234", "leave at door" | Pass to checkout |
| `special_requests` | "birthday cake candle", "extra napkins" | Best-effort |

**Allergy/dietary constraints are non-negotiable.** If unsure whether an item is safe, skip it and pick a clearly safe alternative. When in doubt, err on the side of caution — wrong food is annoying, an allergic reaction is dangerous.

### Parsing Example

```
Title: "DoorDash: Chipotle"
Description: "2 burrito bowls (chicken), guac on the side. Nut allergy. Gate code: 5521"
```

Extracted:
- **items:** 2x burrito bowl (chicken), guacamole (side)
- **allergies:** nuts
- **delivery_notes:** gate code 5521

```
Title: "Thai food, high ratings, under $30, food for 2"
Description: "no shellfish, prefer noodles, gluten-free if possible, leave at door"
```

Extracted:
- **servings:** 2
- **budget:** $30
- **allergies:** shellfish
- **dietary:** gluten-free (best-effort — "if possible")
- **preferences:** noodles
- **delivery_notes:** leave at door

## Supported Services

- **DoorDash** — prefix `DoorDash:`, url `doordash.com`
- **Uber Eats** — prefix `UberEats:` or `Uber Eats:`, url `ubereats.com`
- **Grubhub** — prefix `Grubhub:`, url `grubhub.com`

## Direct Mode Execution

Spawn a single sub-agent with inline instructions:

```
sessions_spawn(
  task: """
Order food delivery via browser automation.

SERVICE: {service}
RESTAURANT: {restaurant}
ITEMS: {items}
ALLERGIES: {allergies or "none"}
DIETARY: {dietary or "none"}
PREFERENCES: {preferences or "none"}
DELIVERY_NOTES: {delivery_notes or "none"}
ADDRESS: {address or "use saved default"}

⚠️ ALLERGY/DIETARY RULES:
- NEVER add items containing allergens listed above
- When customizing items, REMOVE ingredients that conflict (e.g., "no peanuts")
- If an item cannot be made safe → skip it, note why in report
- Check item descriptions and ingredient lists on the menu

BROWSER STEPS:
1. Open {service_url} using Chrome profile (NOTE: this profile contains your saved logins,
   payment methods, and delivery addresses — a real charge will be made on confirmation)
2. Verify logged in (account icon visible, not "Sign In")
   - If not logged in → ABORT, report "Please log into {service} in Chrome first"
3. Search for "{restaurant}" using search bar
4. Click matching restaurant from results
   - If not found or closed → ABORT, report reason
5. For each item in ITEMS:
   - Find item on menu (use semantic matching)
   - Check description for allergen conflicts before adding
   - Click to open customization modal
   - Select required options (size, protein, etc.)
   - Apply customizations as specified
   - Apply allergy-related modifications (remove conflicting ingredients)
   - Apply PREFERENCES if customization options exist
   - Click "Add to cart/bag/order"
6. Open cart and verify:
   - Contents match ITEMS
   - No allergen conflicts in final order
   - Note any substitutions or issues
7. Proceed to checkout
   - Confirm delivery address (use saved default)
   - Add DELIVERY_NOTES if supported (special instructions field)
   - Confirm payment method (use saved default)
   - Note delivery ETA and total

7b. PAUSE — present order summary to user and request explicit confirmation:
    "Ready to place order:
     • Restaurant: {restaurant} via {service}
     • Items: {items}
     • Total: ${amount}
     • Delivery to: {address}
     • ETA: {eta}
     Confirm? (yes / no / cancel)"

    WAIT for user response.
    - "yes" → proceed to step 8
    - anything else → ABORT, do NOT place order

8. Click "Place Order"
9. Wait for confirmation, capture order number and ETA

REPORT FORMAT:
✅ Order confirmed: {restaurant} via {service}, ETA {time}, total ${amount}
   Allergy accommodations: {what was modified or "N/A"}
— OR —
❌ Failed: {reason}

Do NOT checkout if cart doesn't match requested items.
Do NOT checkout if allergen safety cannot be confirmed.
""",
  label: "food-order-{service}"
)
```

## Discovery Mode Execution

### Phase 1: Recon (parallel)

Spawn sub-agents for ALL services simultaneously:

```
sessions_spawn(
  task: """
Search for restaurants on {service}. RECON ONLY — do NOT order.

CRITERIA:
- Cuisine: {cuisine}
- Budget: {budget}
- Rating: {rating_preference}
- Servings: {servings}
- Allergies: {allergies or "none"}
- Dietary: {dietary or "none"}
- Preferences: {preferences}

⚠️ ALLERGY/DIETARY RULES:
- Only recommend restaurants where allergen-safe options clearly exist
- Flag any restaurant where the menu is ambiguous about allergens
- When noting menu highlights, confirm dishes are safe given stated allergies/dietary

BROWSER STEPS:
1. Open {service_url} using Chrome profile (NOTE: this profile contains your saved logins,
   payment methods, and delivery addresses — a real charge will be made on confirmation)
2. Verify logged in
3. Search for "{cuisine}" or "{cuisine} food"
4. Apply filters if available (rating, price level, delivery time)
5. For top 3 restaurants:
   - Note: name, rating (stars + review count), price level ($/$$/$$$)
   - Note: delivery time estimate, delivery fee
   - Click into restaurant, scan menu for items matching cuisine
   - Note 2-3 standout dishes and typical entree price
   - Check if menu items list ingredients or allergen info
   - Flag any allergen concerns for highlighted dishes

RETURN FORMAT:
## {service} Results

### 1. {Restaurant Name}
- Rating: {stars} ({count} reviews)
- Price: {$/$$/$$S} (~${X}/person)
- Delivery: {time} min, ${fee} fee
- Menu highlights: {dishes matching criteria}
- Allergen safety: {safe / caution / unclear} — {notes}
- Fits constraints: {yes/no + notes}

### 2. ...
### 3. ...

**Best match:** {pick} because {reason}
""",
  label: "food-recon-{service}"
)
```

### Phase 2: Decision

After all recon sub-agents return, aggregate and compare:

| Service | Restaurant | Rating | $/person | ETA | Fits Constraints |
|---------|------------|--------|----------|-----|------------------|
| ... | ... | ... | ... | ... | ... |

**Select winner based on:**
1. **Allergen safety first** — eliminate any restaurant where safety is "unclear" or "caution" unless no safe options exist
2. Must fit cuisine and dietary constraints
3. Must be achievable within budget (leave 25% for fees/tip)
4. Prefer higher rating
5. Prefer faster delivery
6. Menu fits stated preferences

**Decide on order:** Based on servings and preferences, plan a good meal:
- For 2: typically 1 appetizer + 2 entrees, or 2-3 shareable plates
- Stay within budget
- **Never include items that conflict with allergies/dietary constraints**
- Lean into preferences ("prefer noodles" → include noodle dish)
- If allergy info is ambiguous for an item, pick a clearly safe alternative

### Phase 3: Order

Spawn order sub-agent for winning service (use Direct Mode task prompt above, with decided items).

## State Tracking

Track in `memory/food-order-state.json`:

```json
{
  "ordered": {
    "{calendar_event_id}": {
      "at": "2026-02-06T19:00:00",
      "mode": "discovery",
      "criteria": "Thai food, high ratings, under $30, food for 2",
      "constraints": {
        "allergies": ["shellfish"],
        "dietary": ["gluten-free"],
        "delivery_notes": "leave at door"
      },
      "service": "doordash",
      "restaurant": "Thai Basil",
      "items": ["spring rolls", "pad thai (no shrimp)", "green curry"],
      "status": "confirmed",
      "eta": "7:35 PM",
      "total": 28.47
    }
  }
}
```

Prune entries older than 24h on each check.

## Error Handling

| Error | Action |
|-------|--------|
| Not logged in | Abort, notify user to log in via Chrome |
| Restaurant closed | Direct: abort. Discovery: use next-best from recon |
| No matches found | Notify user, suggest broadening criteria |
| Over budget | Pick cheaper option or reduce order, note adjustment |
| Item unavailable | Closest substitute, note in confirmation |
| Allergen conflict | **Never order the item.** Pick safe alternative or skip. Flag in report |
| Allergen info unclear | Skip item, pick clearly safe alternative. Note uncertainty in report |

## Reference Files

Service-specific gotchas and UI element locations in `references/`:
- [doordash.md](references/doordash.md)
- [ubereats.md](references/ubereats.md)
- [grubhub.md](references/grubhub.md)

These document service quirks (promo modals, tip screens, etc.). Key steps are inlined in task prompts above for sub-agent self-sufficiency.
