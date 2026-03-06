---
name: Outfits
description: Build an outfit planning system for saving inspiration, creating combinations, and dressing for any occasion.
metadata: {"clawdbot":{"emoji":"👗","os":["linux","darwin","win32"]}}
---

## Core Behavior
- User saves outfit inspiration → catalog with tags and notes
- User asks what to wear → build combination from their clothes
- User plans for event → suggest options with reasoning
- Create `~/outfits/` as workspace

## Use Cases
- Save looks you love: Instagram, Pinterest, street style
- Build go-to combinations from clothes you own
- Plan outfits for specific occasions
- Develop consistent personal style
- Reduce morning decision fatigue

## File Structure
```
~/outfits/
├── inspiration/
│   ├── casual/
│   ├── formal/
│   └── streetwear/
├── my-outfits/
│   ├── work/
│   ├── weekend/
│   └── events/
├── clothes.md
└── style-notes.md
```

## Clothes Inventory
Simple list in clothes.md — no elaborate metadata:
```markdown
## Tops
- white oxford shirt
- navy crewneck sweater
- black t-shirt

## Bottoms
- dark wash jeans
- khaki chinos
```

## Saving Inspiration
- Screenshot or URL with source
- Note WHAT you like: "the layering", "color combo", "those boots"
- Tag by style: minimalist, classic, streetwear, smart casual
- Season tag if weather-specific

## Building Combinations
- Ask what they own before suggesting
- Top + bottom + shoes minimum
- Add outerwear and accessories as needed
- Save working combos to my-outfits/

## Outfit Entry Format
```markdown
# smart-casual-friday.md
## Pieces
- Navy blazer
- White t-shirt
- Dark jeans
- White sneakers

## Occasion
Office casual Friday, drinks after

## Notes
Blazer elevates basic combo
```

## Occasion Planning
- Ask occasion AND venue — "wedding" needs more: outdoor? evening?
- Weather affects everything — rain changes shoes and layers
- Dress code clarification — "smart casual" varies by context
- Suggest 2-3 options, let user pick by mood

## Style Development
- Track what styles appear in inspiration folder
- Surface patterns: "You save a lot of minimalist looks"
- Note color preferences over time
- Build style-notes.md with personal preferences

## Capsule Thinking
- Surface outfit math when helpful: "5 pieces = 12 combos"
- Identify versatile pieces that appear in many outfits
- Flag gaps only when obvious or asked
- Don't push minimalism unless user wants it

## What To Surface
- "This top appears in 6 of your saved outfits"
- "You don't have saved outfits for formal events"
- "Based on your inspiration, you like earth tones"
- "Similar to that Pinterest save you liked"

## Progressive Enhancement
- Week 1: save 5-10 inspiration outfits
- Week 2: list clothes you wear most in clothes.md
- Week 3: create 5 go-to combinations
- Ongoing: add inspiration, build seasonal capsules

## What NOT To Push
- Buying new items before using what they have
- Specific brands or expensive pieces
- Rigid fashion rules — principles over laws
- Guilt about clothing or style choices
