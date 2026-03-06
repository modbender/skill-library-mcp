---
name: Wardrobe
description: Build a personal wardrobe system for cataloging clothes, planning outfits, and mindful shopping.
metadata: {"clawdbot":{"emoji":"👔","os":["linux","darwin","win32"]}}
---

## Core Behavior
- User mentions clothing → offer to catalog
- Help plan outfits → based on what they own
- Support mindful shopping → do you really need it?
- Create `~/wardrobe/` as workspace

## Use Cases
- Know what you own: avoid buying duplicates
- Outfit planning: what to wear for occasions
- Capsule wardrobe: curate intentional collection
- Seasonal rotation: what's in storage
- Decluttering: what to donate or sell
- Packing: what to bring on trips

## Item Entry
- Type: shirt, pants, jacket, shoes, etc.
- Color and pattern
- Brand (optional)
- Size
- Photo: essential for outfit planning
- Season: summer, winter, all-year
- Formality: casual, business, formal
- Purchase date and price (optional)

## File Structure
```
~/wardrobe/
├── tops/
├── bottoms/
├── outerwear/
├── shoes/
├── accessories/
├── outfits/
│   └── work-casual.md
├── seasonal/
│   └── winter-storage.md
└── wishlist.md
```

## Photo Strategy
- One clear photo per item — flat lay or hanger
- Consistent lighting helps comparison
- Front view minimum, back if pattern differs
- Enables visual outfit planning

## Outfit Combinations
- Save outfits that work: top + bottom + shoes
- Tag by occasion: work, casual, date night, formal
- Note what accessories complete it
- "What do I wear with the navy blazer?" → instant answers

## Seasonal Rotation
- Tag items by season
- "What's in winter storage?" → quick list
- Rotation reminders: time to swap closets
- Condition check when retrieving from storage

## Wear Tracking (Optional)
- Log when worn if tracking usage
- Surface rarely worn items: "Haven't worn in 1 year"
- Identify favorites: worn 20+ times
- ROI thinking: cost per wear

## Capsule Wardrobe Support
- Define core pieces goal
- Track current count vs target
- Identify gaps: "No neutral blazer"
- Identify excess: "7 black t-shirts"

## Shopping Mindfully
- Check wardrobe before buying: "Do I have a white shirt?"
- Wishlist with intent: why do you want it?
- Waiting period: revisit wishlist after 30 days
- "Would this go with at least 3 things I own?"

## Decluttering Support
- Filter by: not worn in X months
- Condition assessment: still good?
- Donate, sell, or trash decision
- Track donations for tax purposes if applicable

## Packing Lists
- Build from wardrobe: select items for trip
- Save templates: "Beach vacation essentials"
- Check items back in after trip
- Note what you didn't wear (pack less next time)

## Categories
Tops: t-shirts, shirts, blouses, sweaters
Bottoms: jeans, pants, shorts, skirts
Outerwear: jackets, coats, blazers
Shoes: sneakers, boots, dress shoes, sandals
Accessories: belts, scarves, hats, bags, jewelry
Activewear: gym clothes, sports-specific
Formal: suits, dresses for occasions

## What To Surface
- "You have 4 white t-shirts"
- "These items haven't been worn in a year"
- "Outfit ideas for navy pants"
- "Winter clothes still in storage — time to rotate?"
- "This would be the 5th striped shirt"

## Progressive Enhancement
- Week 1: photograph and catalog current favorites
- Week 2: add remaining everyday items
- Month 2: seasonal items, special occasion
- Ongoing: outfit logging, wear tracking

## What NOT To Suggest
- Cataloging every sock and underwear — focus on visible items
- Rigid capsule rules — personal style matters
- Expensive wardrobe apps — files and photos work
- Guilt about clothing — awareness without judgment

## Maintenance
- Review seasonally: what needs repair or replacement?
- Update when buying or removing items
- Photo retake if item condition changes
- Annual wardrobe audit

## Integration Points
- Packing: trip wardrobe selection
- Shopping: wishlist and gap analysis
- Budget: clothing spending tracking
- Donations: decluttering for tax records
