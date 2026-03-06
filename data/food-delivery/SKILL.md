---
name: Food Delivery
slug: food-delivery
version: 1.0.0
description: Choose and order food with learned preferences, price comparison, and variety protection.
metadata: {"clawdbot":{"emoji":"🍕","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## When to Use

User wants their agent to handle the entire food ordering process — from deciding what to eat, through comparing options, to placing the actual order. Agent learns preferences over time and makes increasingly better choices.

## Architecture

Memory lives in `~/food-delivery/`. See `memory-template.md` for setup.

```
~/food-delivery/
├── memory.md          # Core preferences, restrictions, defaults
├── restaurants.md     # Restaurant ratings, dishes, notes
├── orders.md          # Recent orders for variety tracking
└── people.md          # Household/group member preferences
```

User creates these files. Templates in `memory-template.md`.

## Quick Reference

| Topic | File |
|-------|------|
| Memory setup | `memory-template.md` |
| Decision framework | `decisions.md` |
| Ordering workflow | `ordering.md` |
| Common traps | `traps.md` |

## Data Storage

All data stored in `~/food-delivery/`. Create on first use:
```bash
mkdir -p ~/food-delivery
```

## Scope

This skill handles:
- Learning cuisine and taste preferences
- Storing restaurant ratings and dish notes
- Comparing prices across delivery platforms
- Finding active promotions and coupons
- Placing orders via browser automation
- Tracking recent orders for variety
- Managing household member preferences
- Coordinating group orders

User provides:
- Delivery app credentials (stored in their browser/app)
- Delivery address (configured in their apps)
- Payment methods (configured in their apps)

## Self-Modification

This skill NEVER modifies its own SKILL.md.
All learned data stored in `~/food-delivery/` files.

## Core Rules

### 1. Learn Preferences Explicitly
| User says | Store in memory.md |
|-----------|-------------------|
| "I'm vegetarian" | restriction: vegetarian |
| "I love spicy food" | preference: spice_level=high |
| "Allergic to shellfish" | CRITICAL: shellfish (always filter) |
| "I don't like olives" | avoid: olives |
| "Budget around $20" | default_budget: $20 |
| "Usually order dinner around 7pm" | default_time: 19:00 |

### 2. Restriction Hierarchy
```
CRITICAL (allergies, medical) → ALWAYS filter, never suggest
FIRM (religious, ethical, diet) → filter unless user overrides
PREFERENCE (taste) → consider but flexible
```

For CRITICAL restrictions:
- Add note to EVERY order specifying the allergy
- Verify restaurant can accommodate
- Never suggest "you could try it anyway"

### 3. The Decision Flow
When user asks to order food:

**Step 1: Context**
- What time is it? (breakfast/lunch/dinner)
- What day? (weekday functional vs weekend exploratory)
- Any stated mood or occasion?
- How many people?

**Step 2: Filter**
- Remove anything violating CRITICAL restrictions
- Remove recently repeated (variety protection)
- Remove closed restaurants
- Apply budget constraints

**Step 3: Compare**
- Check same restaurant across platforms
- Find active promos/coupons
- Calculate total cost (food + delivery + fees)

**Step 4: Present**
- Show 2-3 options maximum
- Include reasoning for each
- Show price comparison if relevant
- Recommend one based on user history

**Step 5: Confirm & Order**
- Get explicit confirmation
- Place order via browser
- Confirm order placed with ETA

### 4. Variety Protection
Track in orders.md:
- Last 14 days of orders (restaurant + cuisine type)

Triggers:
- Same restaurant 3x in 7 days → "You've ordered from [X] a lot. Want to try something similar?"
- Same cuisine 4x in 7 days → suggest different category
- Haven't tried category user likes in 2+ weeks → suggest it

### 5. Price Optimization
Before ordering:
1. Check restaurant on all user's delivery apps
2. Compare base prices (often differ by platform)
3. Check for active coupons/promos
4. Factor in delivery fees and service charges
5. Recommend cheapest option for same food

Tell user: "Same order is $4 cheaper on [Platform] today"

### 6. Group Orders
When ordering for multiple people:
1. Load ~/food-delivery/people.md for known preferences
2. Collect any new restrictions
3. Find intersection cuisine (works for everyone)
4. Suggest variety restaurants (broad menus)
5. Calculate fair split if needed

Default crowd-pleasers when no consensus:
- Pizza (customizable)
- Burgers (something for everyone)
- Tacos (variety of fillings)
- Chinese (range of dishes)
- Indian (vegetarian options)

### 7. Context Adaptation
| Context | Behavior |
|---------|----------|
| "I'm tired" | Comfort food, familiar favorites |
| "Celebrating" | Higher-end, special occasion spots |
| "In a hurry" | Fastest delivery, simple orders |
| "Working lunch" | Quick, not messy, productive-friendly |
| "Date night" | Quality over speed, ambiance matters |
| "Hungover" | Greasy comfort, hydrating, gentle |
| "Post-workout" | Protein-heavy, healthier options |
| Rainy day | Warn about longer delivery times |
| Friday night | Can wait for quality |
| Sunday morning | Brunch options, recovery mode |

### 8. Proactive Suggestions
When appropriate (not spammy):
- Notify of flash sales on favorite restaurants
- Remind of unused loyalty points
- Suggest reordering past successes
- Mention new restaurants matching preferences

### 9. Order Execution
Via browser automation:
1. Open user's preferred delivery app
2. Navigate to restaurant
3. Add items to cart
4. Apply any coupons found
5. Verify delivery address
6. Confirm order total with user
7. Place order
8. Report confirmation and ETA

Always confirm before final checkout.

### 10. Problem Handling
If order has issues:
- Missing items → help file complaint
- Wrong items → help request refund
- Late delivery → track and communicate
- Quality issues → record in restaurant notes

## Boundaries

### Stored Locally (in ~/food-delivery/)
- Cuisine preferences and restrictions
- Restaurant ratings and dish notes
- Recent order log (variety tracking)
- Household member preferences
- Budget defaults

### User Manages (in their apps)
- Delivery addresses
- Payment methods
- Account credentials

### Agent Does NOT Store
- Credit card numbers
- Exact addresses
- Account passwords
- Order receipts with payment details
