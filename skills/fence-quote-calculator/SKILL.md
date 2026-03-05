---
name: fence-quote-calculator
description: Calculate material takeoffs and quotes for wood, vinyl, and aluminum fence projects. Handles post counts, picket quantities, concrete bags, gate hardware, and total material costs. Use when Reese asks to quote a fence job, calculate materials, or do a takeoff.
metadata:
  openclaw:
    emoji: "🪵"
---

# Fence Quote Calculator

## When to Use
- Reese asks to "quote a fence job" or "run a takeoff"
- Any mention of calculating fence materials, posts, pickets, concrete, or gates
- Pricing or estimating a fence project

## Material Specifications

### Post Types & Spacing
- **Line posts, corner posts, end posts**: 4x4 pressure treated
- **Gate posts**: 6x6 pressure treated (1 per single gate opening, 2 per double gate opening)
- **Post spacing**: 8 feet on center

### Post Count Formula
1. Calculate total line sections: `total_linear_feet / 8` (round up)
2. End posts = 2 per fence run (start and end of each continuous run)
3. Corner posts = 1 per corner
4. Line posts = total_sections - 1 - corner_posts (per run)
5. Gate posts: count based on gate config (see gates below)

### Rails
- **3x 2x4x8 rails per 8-foot section**
- **3x 2x4x8 per gate leaf** (for gate framing)

### Pickets (Wood Fence)
- **Type**: 1x6x6 dog ear pressure treated
- **Coverage**: 5.5 inches per picket (actual board width, no gap/waste factor)
- **Per 8-foot section**: `96 inches / 5.5 inches = 17.45` -> **18 pickets per section** (round up)
- **Total pickets**: sections x 18

### Concrete
- **4x4 posts**: 60 lbs per post
- **6x6 posts**: 80 lbs per post
- **Aluminum posts**: 60 lbs per post
- **Vinyl posts**: 80 lbs per post
- **Bag size**: 80 lb bags ONLY (Home Depot, 42 bags per pallet)
- **Bags per 4x4**: `60/80 = 0.75` -> round up to **1 bag per 4x4 post**
- **Bags per 6x6**: `80/80` = **1 bag per 6x6 post**

### Gates
- **Standard single gate**: 5 feet wide opening (4 feet if specifically requested)
- **Standard double gate**: 10 feet wide opening (8 feet if specifically requested)
- **Hardware per gate opening**: 1 latch + 1 handle
- **Hinges**: 3 per gate leaf (single gate = 3 hinges, double gate = 6 hinges)
- **Drop rod**: 1 per double gate

### Fence Types Supported
1. Wood (PT pine, dog ear pickets)
2. Tan Vinyl
3. White Vinyl
4. 5ft Aluminum
5. 4ft Aluminum

## Output Format

When calculating a quote, present results as:

```
MATERIAL TAKEOFF - [Project Name/Address]
Fence Type: [type]
Total Linear Feet: [X]
Gate Config: [X single, X double]

POSTS
- 4x4 line/corner/end posts: [count]
- 6x6 gate posts: [count]

RAILS
- 2x4x8 (fence sections): [count]
- 2x4x8 (gate framing): [count]
- Total 2x4x8: [count]

PICKETS (wood only)
- 1x6x6 dog ear PT: [count]

CONCRETE
- 80lb bags: [count]
- Pallets (42/pallet): [count]

GATE HARDWARE
- Latches: [count]
- Handles: [count]
- Hinges: [count]
- Drop rods: [count]
```

## Important Notes
- Always round up on pickets and posts. Short materials means a return trip.
- If Reese gives you a rough sketch or describes corners/gates, confirm the layout before running numbers.
- For vinyl and aluminum, post spacing and section widths may differ from wood. Ask Reese to confirm if specs differ from the 8' OC standard.
- Do NOT estimate labor costs in this skill. That's separate pricing.
