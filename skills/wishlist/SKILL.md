---
name: Wishlist
description: Build a personal wishlist system for capturing wants, tracking prices, and smart purchasing decisions.
metadata: {"clawdbot":{"emoji":"⭐","os":["linux","darwin","win32"]}}
---

## Core Behavior
- User shares something they want → capture with details
- User asks what to buy → surface by priority and price
- Periodically check prices on tracked items
- Create `~/wishlist/` as workspace

## File Structure
```
~/wishlist/
├── items/
│   └── sony-headphones.md
├── by-priority/
│   ├── must-have.md
│   ├── want.md
│   └── someday.md
├── by-category/
│   ├── tech.md
│   ├── home.md
│   └── clothing.md
├── purchased.md
├── price-alerts.md
└── settings.md
```

## Item Entry
```markdown
# sony-headphones.md
## Item
Sony WH-1000XM5 Headphones

## Why I Want It
Best noise cancelling, work from cafes

## Priority
Must-have

## Category
Tech

## Price Tracking
- Target price: $300
- Current best: $349 (Amazon)
- Last checked: Feb 11, 2024

## Links
- Amazon: [url]
- Best Buy: [url]

## Price History
- Feb 1: $379
- Feb 10: $349 (dropped!)

## Notes
Wait for Prime Day or Black Friday
Consider refurbished

## Added
January 15, 2024
```

## Quick Capture
For fast saving:
```markdown
User: "I want those Sony headphones"
→ Create item with name
→ Ask: priority? budget? link?
→ Start tracking
```

## Priority Levels
```markdown
# by-priority/must-have.md
Items you're actively planning to buy:
- Sony WH-1000XM5 — waiting for <$300
- Standing desk — researching options

# by-priority/want.md
Would buy if good deal:
- Kindle Paperwhite
- AirTag 4-pack

# by-priority/someday.md
Nice to have, no rush:
- Espresso machine
- Drone
```

## Price Alerts
```markdown
# price-alerts.md
## Active Alerts
- Sony WH-1000XM5: alert if <$300
- Kindle Paperwhite: alert if <$100
- Standing desk: alert if <$400

## Triggered
- Feb 10: Sony dropped to $349 (still above target)
```

## Settings
```markdown
# settings.md
## Price Check Frequency
Weekly on Sundays

## Alert Preferences
Notify when:
- Price drops below target
- Price drops >15% from last check
- Item goes on sale

## Preferred Stores
- Amazon
- Best Buy
- Direct from manufacturer
```

## Price Checking
When checking prices:
- Search current prices across configured stores
- Compare to target and history
- Surface significant drops
- Update last checked date

## What To Surface
- "Sony headphones dropped $30 this week"
- "3 items on your must-have list under budget"
- "Kindle hasn't changed price in 2 months"
- "Black Friday coming — review high-priority items"

## Smart Suggestions
- "This item often discounts on Prime Day"
- "Refurbished available at 40% off"
- "Similar item with better reviews for less"
- "You've wanted this 6 months — still relevant?"

## Purchase Flow
When user decides to buy:
- Confirm current best price
- Move to purchased.md with date and final price
- Note: got target price? above/below?

## Purchased Log
```markdown
# purchased.md
## 2024
- Sony WH-1000XM5: $299 (Feb 20) — hit target!
- Standing desk: $450 (Jan 15) — slightly over

## Stats
- Items bought at/under target: 70%
- Average wait time: 45 days
- Total saved vs original price: $340
```

## Categories
Organize by type for browsing:
- Tech: gadgets, electronics
- Home: furniture, appliances
- Clothing: wardrobe additions
- Hobby: gear for interests
- Gifts: things to gift others

## Progressive Enhancement
- Start: capture items with priority
- Add target prices
- Enable price checking
- Review monthly: still want it?

## What NOT To Do
- Buy impulsively without checking wishlist first
- Keep items forever without reviewing
- Ignore price history patterns
- Forget why you wanted something
