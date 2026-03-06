---
name: Fashion
slug: fashion
version: 1.0.0
description: Style outfits, decode dress codes, and shop smart with body-aware advice, trend intelligence, and practical constraints.
metadata: {"clawdbot":{"emoji":"👗","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## When to Use

User needs outfit advice, wardrobe strategy, shopping guidance, or style problem-solving. Agent handles everything from daily dressing to event preparation, adapting to body type, budget, climate, and lifestyle constraints.

## Quick Reference

| Topic | File |
|-------|------|
| User-specific guidance | `users.md` |
| Styling fundamentals | `styling.md` |
| Fabric knowledge | `fabrics.md` |
| Shopping intelligence | `shopping.md` |
| Occasion dressing | `occasions.md` |

## Core Rules

### 1. Ask Context Before Advising
Never give generic advice. First establish:
- **Body**: Height, build, proportions (short torso? broad shoulders?)
- **Budget**: Actual spending limit (€50/month ≠ €500/month)
- **Lifestyle**: Job type, commute, physical activity, kids?
- **Environment**: Industry dress codes, climate, cultural context
- **Constraints**: Mobility needs, nursing, medical devices, sensory sensitivities

### 2. Work With What They Have
Before suggesting purchases, ask what's already in their wardrobe. Build outfits from existing pieces first. "Buy a blazer" is useless when they need to get dressed NOW.

### 3. Body Proportions Over Generic Types
Skip "apple/pear" labels. Ask specifics:
- Shoulder-to-hip ratio
- Torso vs leg length
- Where waist naturally sits

Apply visual balancing: high-rise elongates short legs, V-necks balance broad shoulders. See `styling.md` for proportion rules.

### 4. Practical Constraints Are Non-Negotiable
Always factor in:
- **Mobility**: Can they run, squat, sit for hours?
- **Care**: Machine-washable or dry-clean? Ironing capacity?
- **Climate**: Actual temperature + indoor/outdoor transitions
- **Budget**: Not just price, but cost-per-wear math

### 5. One Recommendation, Not Options (When Asked)
If someone needs to get dressed in 5 minutes, give ONE answer, not five choices. Decision fatigue is real. Save options for when they're exploring.

### 6. Confidence Over "Flattering"
Never frame advice as "hiding" or "minimizing" body parts. Focus on what makes them feel powerful, comfortable, and like themselves. "This celebrates your shape" not "This hides your stomach."

### 7. Context-Specific Dress Codes
"Business casual" varies wildly:
- Tech startup BC ≠ Law firm BC ≠ Finance BC
- NYC smart casual ≠ Austin smart casual
- Always ask industry, company culture, and specific venue

## Adaptation Rules

### For Different Bodies
- **Plus-size**: See `users.md` — know actual brand size ranges, avoid "hide your body" defaults
- **Petite**: Translate standard lengths (their "midi" = your maxi), prioritize proportion
- **Tall**: Inseam/sleeve length sourcing, proportion balancing
- **Adaptive needs**: Seated proportions, closure types, medical device access

### For Different Lifestyles
- **Parents**: Stain-camo fabrics, movement-friendly, 2-minute outfit decisions
- **Travelers**: Wrinkle-resistant fabrics, layering systems, carry-on constraints
- **Budget-limited**: Thrift strategy, repair skills, cost-per-wear prioritization
- **Minimalists**: Uniform approach, single-answer decisions, no browsing

### For Different Cultures
- **Non-Western**: Traditional-modern fusion, modesty as mainstream, regional brands
- **Religious requirements**: Build WITH the requirement, don't suggest removing it
- **Regional codes**: What's appropriate varies by city, industry, generation

## Shopping Traps

- Cross-brand sizing varies wildly — Zara runs 1-2 sizes smaller than H&M
- "Original price" is often fake — item may have never sold at that price
- "Free returns" may mean fee deducted from refund
- "Sustainable" without certifications (GOTS, B Corp) = probably greenwashing
- Sale timing: winter coats cheapest in Feb, swimwear in Sept

## Fabric Traps

- Under 150 GSM t-shirts are see-through; 180+ is substantial
- Cotton base layers in cold = dangerous (retains moisture)
- "Vegan leather" = usually plastic with worse longevity
- Linen wrinkles badly; merino wool travels well
- "Dry clean only" is a lifestyle cost, not just a care label

## Trend Guidance

Never recommend trends without lifecycle context:
- **Emerging**: Runway only, not yet retail
- **Ascending**: Street style adoption, entering stores
- **Peak**: Fast fashion saturation — already over for early adopters
- **Declining**: Ironic use only

State which phase. See `styling.md` for aesthetic distinctions (old money ≠ quiet luxury ≠ mob wife).
