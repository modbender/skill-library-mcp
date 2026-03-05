# Setup — Mexico Travel Guide

## First-Time Setup

When user mentions Mexico travel for the first time:

### 1. Create Memory Structure
```bash
mkdir -p ~/mexico
```

### 2. Initialize Memory File
Create `~/mexico/memory.md` using the template from `memory-template.md`.

### 3. Gather Trip Context
Ask naturally (not as a form):
- What month are you going? (rain and heat matter by region)
- How long is the trip?
- Which bases matter most? (CDMX, Oaxaca, Guadalajara, Yucatan/Riviera Maya)
- Food-first, culture-first, beach-first, or mixed?
- Any mobility, dietary, or budget constraints?
- Public transport, private transfers, or rental car?

### 4. Save to Memory
Update `~/mexico/memory.md` with their answers.

## Returning Users

If `~/mexico/memory.md` exists:
1. Read it silently
2. Reuse known preferences
3. Ask what changed since last plan
4. Update memory with new priorities and constraints

## Quick Start Responses

**"I am going to Mexico City"**
→ Ask: season, neighborhood preference, budget
→ Then: use `cdmx.md` + `accommodation.md`

**"I want beach + ruins"**
→ Ask: Cancun/Tulum/Playa base preference, pace tolerance, transport style
→ Then: use `yucatan-riviera-maya.md` + `beaches.md` + `itineraries.md`

**"Planning Mexico trip"**
→ Ask: one-region depth vs multi-region mix
→ Then: use `regions.md` and `transport.md` before final itinerary

## Important Notes

- Mexico rewards fewer bases with deeper local planning.
- Transfer logistics define trip quality more than map distance.
- Coastal and tropical zones need heat and weather-aware pacing.
- Holiday periods can sharply change costs and availability.
