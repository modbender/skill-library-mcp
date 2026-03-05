# Setup — Portugal Travel Guide

## First-Time Setup

When user mentions Portugal travel for the first time:

### 1. Create Memory Structure
```bash
mkdir -p ~/portugal
```

### 2. Initialize Memory File
Create `~/portugal/memory.md` using the template from `memory-template.md`.

### 3. Gather Trip Context
Ask naturally (not as a form):
- When are you traveling? (month matters for weather, crowds, festivals)
- How long is your trip?
- Which cities/regions interest you?
- What's your travel style? (foodie, beach, culture, adventure)
- Any dietary restrictions?
- Traveling with kids?

### 4. Save to Memory
Update `~/portugal/memory.md` with their answers.

## Returning Users

If `~/portugal/memory.md` exists:
1. Read it silently
2. Note any previous trips or preferences
3. Ask what's new or if plans changed
4. Update memory with new info

## Quick Start Responses

**"I'm going to Lisbon"**
→ Ask: How many days? Month? First time?
→ Then: Reference lisbon.md for neighborhood breakdown

**"Planning Portugal trip"**
→ Ask: Which regions? (Lisbon, Porto, Algarve, Douro, Azores, Madeira)
→ Suggest itinerary based on duration

**"Best restaurants in Porto"**
→ Check memory for dietary restrictions
→ Reference porto.md and food-guide.md

**"Where to see fado"**
→ Ask: Tourist show or authentic? Budget?
→ Reference culture.md and lisbon.md

## Important Notes

- Portugal is small but diverse — 1 week = Lisbon + Sintra + Porto realistic
- Summer (Jun-Aug) = crowded beaches, book ahead
- Shoulder season (Apr-May, Sep-Oct) = best weather/value
- Winter = mild in south, rainy in north, great for Madeira
- Always check if traveling during Santos Populares (June) — huge festivals in Lisbon/Porto
