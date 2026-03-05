# Setup — Canada Travel Guide

## First-Time Setup

When user mentions Canada travel for the first time:

### 1. Create Memory Structure
```bash
mkdir -p ~/canada
```

### 2. Initialize Memory File
Create `~/canada/memory.md` using the template from `memory-template.md`.

### 3. Gather Trip Context
Ask naturally (not as a form):
- What month are you traveling? (season is critical in Canada)
- How long is the trip?
- Which cities or regions matter most?
- What trip style fits best? (food, cities, nature, family)
- Any mobility, dietary, or budget constraints?
- Are you renting a car or using public transport?

### 4. Save to Memory
Update `~/canada/memory.md` with their answers.

## Returning Users

If `~/canada/memory.md` exists:
1. Read it silently
2. Reuse known preferences
3. Ask what changed since last plan
4. Update memory with new constraints or priorities

## Quick Start Responses

**"I'm going to Toronto"**
→ Ask: season, neighborhood preference, budget
→ Then: use `toronto.md` + `accommodation.md`

**"I want Banff"**
→ Ask: month, fitness, car vs shuttle, nights available
→ Then: use `banff-jasper.md` + `hiking.md` + `transport.md`

**"Planning Canada trip"**
→ Ask: urban focus, nature focus, or mix
→ Then: use `itineraries.md` and `regions.md` to narrow scope

## Important Notes

- Canada is not one easy loop destination; distances and logistics define the trip.
- Shoulder seasons often deliver better value in cities and easier bookings.
- National park logistics need early planning in peak summer.
- Winter travel can be excellent, but road and weather risk must be explicit.
