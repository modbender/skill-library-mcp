---
name: trip-discover
description: Recommend travel destinations based on vibe, budget, duration, and group size. Handles "suggest a trip", "where should I go", "weekend getaway", "compare X vs Y", and "plan from my saved places".
---

# Trip Discover

## When to activate
- User asks for trip suggestions: "weekend trip", "where should I go", "suggest somewhere"
- User gives a vibe: "mountains", "beaches", "offbeat", "party", "peaceful"
- User says "plan from my saves" or "pick from my wishlist"
- User asks to compare: "Kasol vs Bir", "which is better"

## Input parsing
Extract from user message (ask only if critical info missing):
- **Vibe:** mountains / beaches / heritage / adventure / spiritual / nightlife / offbeat
- **Budget:** total per person in ₹ (default: ₹5000-8000 for weekend)
- **Duration:** weekend (2-3 days) / long weekend (4 days) / week
- **Group:** solo / couple / friends / family
- **From city:** assume Delhi unless stated or known from memory

## How to recommend
1. Search the web for current relevant destinations
2. Pick 2-3 destinations. Lead with your top pick.
3. For each provide:
   - Name + one opinionated line (not generic)
   - Travel time from their city + how to get there
   - Rough cost estimate per person
   - Current weather
   - Why THIS trip for THIS person

## "Plan from my saves" flow
1. Check memory for saved destinations
2. Filter by current vibe/budget/duration
3. Recommend from saves first, then add new discoveries

## Compare flow ("Kasol vs Bir")
Search web for both. Present side-by-side:
- Vibe, travel time, cost, weather, best for
- End with: "My pick: X — because..."

## Response format
🏔️ My pick: Kasol, Himachal Pradesh
Backpacker paradise with killer cafes and the Kheerganga trek.
12 hrs by Volvo from Delhi (₹1200). Stay: ₹800-1500/night.
March weather: 10-18°C, perfect trekking season.
Total estimate: ₹6,500/person for 3 days.

Also consider:
- Tirthan Valley — quieter, great for couples
- Bir — paragliding + monasteries, slightly cheaper

Want me to plan Kasol? Or compare any two?

## Rules
- Max 3 destinations. Never more.
- No generic descriptions — be specific and opinionated
- Always check current weather/season via web search
- Check saved places in memory if user has any
