# Setup — Australia Travel Guide

## First-Time Setup

When user mentions Australia travel for the first time:

### 1. Create Memory Structure
```bash
mkdir -p ~/australia
```

### 2. Initialize Memory File
Create `~/australia/memory.md` using the template from `memory-template.md`.

### 3. Gather Trip Context
Ask naturally (not as a form):
- Which month are you going? (season strongly affects region quality)
- How long is the trip?
- City-and-coast mix, nature-first, or outback-first?
- How comfortable are you with long drives?
- Any mobility, dietary, weather, or budget constraints?
- Flights, rental car, campervan, or mixed transport?

### 4. Save to Memory
Update `~/australia/memory.md` with their answers.

## Returning Users

If `~/australia/memory.md` exists:
1. Read it silently
2. Reuse known preferences
3. Ask what changed since last plan
4. Update memory with new priorities and constraints

## Quick Start Responses

**"I am going to Sydney"**
→ Ask: nights, neighborhood style, city vs beach balance
→ Then: use `sydney.md` + `accommodation.md`

**"I want coast and reef"**
→ Ask: tropical north tolerance and weather window
→ Then: use `cairns-reef.md` + `beaches.md` + `seasonality.md`

**"Planning Australia trip"**
→ Ask: one-region depth vs multi-region route
→ Then: use `regions.md` and `transport.md` before final itinerary

## Important Notes

- Australia route quality is mostly a distance and pacing decision.
- Fewer anchors usually outperform checklist-heavy plans.
- Seasonal timing matters more than many travelers assume.
- Remote and outdoor days need explicit safety buffers.
