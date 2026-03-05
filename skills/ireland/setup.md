# Setup — Ireland Travel Guide

## First-Time Setup

When user mentions Ireland travel for the first time:

### 1. Create Memory Structure
```bash
mkdir -p ~/ireland
```

### 2. Initialize Memory File
Create `~/ireland/memory.md` using the template from `memory-template.md`.

### 3. Gather Trip Context
Ask naturally (not as a form):
- Which month are you going? (weather and daylight matter)
- How long is the trip?
- City-break, road-trip, or mixed plan?
- Do you want mostly food/pubs, culture, or coastal nature?
- Are you comfortable driving on the left on narrow roads?
- Any dietary, mobility, or budget constraints?

### 4. Save to Memory
Update `~/ireland/memory.md` with their answers.

## Returning Users

If `~/ireland/memory.md` exists:
1. Read it silently
2. Reuse known preferences
3. Ask what changed since last plan
4. Update memory with new priorities and constraints

## Quick Start Responses

**"I am going to Dublin"**
→ Ask: nights, neighborhood preference, budget
→ Then: use `dublin.md` + `accommodation.md`

**"I want a road trip"**
→ Ask: days, driving comfort, must-see coast sections
→ Then: use `wild-atlantic-way.md` + `transport.md` + `itineraries.md`

**"Planning Ireland trip"**
→ Ask: first-time vs repeat visit, city vs coast split
→ Then: use `regions.md` to narrow scope before final itinerary

## Important Notes

- Distances are moderate, but average driving speeds can be low on scenic rural roads.
- Peak season in coastal areas needs early booking.
- Shoulder months are often better for value and crowd control.
- Weather can change quickly, so every day plan needs a backup.
