# Setup — France Travel Guide

## First-Time Setup

When user mentions France travel for the first time:

### 1. Create Memory Structure
```bash
mkdir -p ~/france
```

### 2. Initialize Memory File
Create `~/france/memory.md` using the template from `memory-template.md`.

### 3. Gather Trip Context
Ask naturally (not as a form):
- Which month are you going? (season changes crowds and pricing)
- How long is the trip?
- Which bases matter most? (Paris, Lyon, Provence, Riviera, other)
- Food-first, museums-first, coast-first, or mixed?
- Any mobility, dietary, or budget constraints?
- Rail-focused, rental car, or mixed transport?

### 4. Save to Memory
Update `~/france/memory.md` with their answers.

## Returning Users

If `~/france/memory.md` exists:
1. Read it silently
2. Reuse known preferences
3. Ask what changed since last plan
4. Update memory with new priorities and constraints

## Quick Start Responses

**"I am going to Paris"**
→ Ask: nights, neighborhood style, museum priorities, budget
→ Then: use `paris.md` + `accommodation.md`

**"I want Provence and coast"**
→ Ask: Marseille/Nice base split, pace tolerance, transport style
→ Then: use `marseille-provence.md` + `french-riviera.md` + `itineraries.md`

**"Planning France trip"**
→ Ask: one-region depth vs multi-region mix
→ Then: use `regions.md` and `transport.md` before final itinerary

## Important Notes

- France rewards fewer bases with deeper neighborhood planning.
- Rail is often best between major cities; car is selective by region.
- Reservation culture can define trip quality in food and museums.
- Peak summer and holidays can sharply change costs and availability.
