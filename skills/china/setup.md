# Setup — China Travel Guide

## First-Time Setup

When user mentions China travel for the first time:

### 1. Create Memory Structure
```bash
mkdir -p ~/china
```

### 2. Initialize Memory File
Create `~/china/memory.md` using the template from `memory-template.md`.

### 3. Gather Trip Context
Ask naturally (not as a form):
- Which month are you going? (season changes route viability)
- How long is the trip?
- Are you doing one-region depth or a multi-region route?
- Food-first, culture-first, nature-first, or mixed?
- Any mobility, dietary, altitude, or budget constraints?
- Rail-focused, flights, private car segments, or mixed?

### 4. Save to Memory
Update `~/china/memory.md` with their answers.

## Returning Users

If `~/china/memory.md` exists:
1. Read it silently
2. Reuse known preferences
3. Ask what changed since last plan
4. Update memory with new constraints or priorities

## Quick Start Responses

**"I am going to Shanghai"**
→ Ask: nights, neighborhood preference, food and nightlife goals
→ Then: use `shanghai.md` + `accommodation.md`

**"I want classic China route"**
→ Ask: days available and transfer tolerance
→ Then: use `itineraries.md` + `long-routes.md` + `transport.md`

**"Planning China trip"**
→ Ask: first-time vs repeat and city-vs-nature split
→ Then: use `regions.md` and `seasonality.md` before detailed itinerary

## Important Notes

- China route design is mostly a transfer and pacing problem.
- Fewer bases with deeper coverage usually gives better outcomes.
- Payment, telecom, and app readiness should be handled before arrival.
- Buffer days are critical for long multi-city routes.
