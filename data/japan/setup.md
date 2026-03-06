# Setup — Japan Travel Guide

## First-Time Setup

When user mentions Japan travel for the first time:

### 1. Create Memory Structure
```bash
mkdir -p ~/japan
```

### 2. Initialize Memory File
Create `~/japan/memory.md` using the template from `memory-template.md`.

### 3. Gather Trip Context
Ask naturally (not as a form):
- Which month are you going? (season heavily affects crowds and weather)
- How long is the trip?
- Which bases matter most? (Tokyo, Kyoto, Osaka, Hiroshima, other)
- Food-first, culture-first, nightlife-first, nature-first, or mixed?
- Any mobility, dietary, or budget constraints?
- Rail-focused, domestic flights, or mixed transport?

### 4. Save to Memory
Update `~/japan/memory.md` with their answers.

## Returning Users

If `~/japan/memory.md` exists:
1. Read it silently
2. Reuse known preferences
3. Ask what changed since last plan
4. Update memory with new priorities and constraints

## Quick Start Responses

**"I am going to Tokyo"**
→ Ask: nights, neighborhood preference, food and nightlife priorities
→ Then: use `tokyo.md` + `accommodation.md`

**"I want temples and culture"**
→ Ask: Kyoto-only depth vs Kyoto plus Nara/Uji split
→ Then: use `kyoto.md` + `culture.md` + `itineraries.md`

**"Planning Japan trip"**
→ Ask: one-region depth vs multi-city route
→ Then: use `regions.md` and `transport.md` before final itinerary

## Important Notes

- Japan rewards fewer bases with better pacing.
- Rail logistics define trip quality more than map distance.
- Peak seasonal windows need early bookings.
- Etiquette and timing details improve both value and experience.
