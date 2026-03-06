---
name: Beauty
slug: beauty
version: 1.0.0
homepage: https://clawic.com/skills/beauty
description: Build practical beauty routines with skincare basics, makeup strategy, and hair care plans tailored to skin type, budget, and schedule.
changelog: Initial release with personalized beauty routines, safety guardrails, and situation-specific guidance for daily and event looks.
metadata: {"clawdbot":{"emoji":"💄","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## Setup

On first use, read `setup.md` for integration guidelines and memory initialization.

## When to Use

User needs help with skincare, makeup, haircare, or grooming decisions.
Agent creates practical routines, adapts for budget and lifestyle constraints, and provides safe product and technique guidance.

## Architecture

Memory lives in `~/beauty/`. See `memory-template.md` for structure.

```
~/beauty/
├── memory.md         # Status, profile, constraints, routines, notes
├── routines/         # Saved routine versions by context
├── products/         # Product shortlists and replacements
└── notes/            # Event plans and progress snapshots
```

## Quick Reference

| Topic | File |
|-------|------|
| Setup process | `setup.md` |
| Memory template | `memory-template.md` |
| Universal beauty frameworks | `frameworks.md` |
| Routine templates | `routines.md` |
| Product selection rules | `products.md` |
| Safety and hygiene guardrails | `safety.md` |
| Beginner guidance | `situations/beginner.md` |
| Budget optimization | `situations/budget.md` |
| Sensitive skin guidance | `situations/sensitive-skin.md` |
| Blemish-prone strategy | `situations/blemish-prone.md` |
| Event preparation | `situations/event-ready.md` |
| Busy schedule routines | `situations/busy-schedule.md` |
| Men's grooming guidance | `situations/mens-grooming.md` |
| Textured hair care strategy | `situations/textured-hair.md` |

## Core Rules

### 1. Build Context Before Recommending
Lock profile first:
- Skin profile: oily, dry, combo, sensitive, reactive zones
- Hair profile: texture, porosity, scalp tendencies, styling habits
- Constraints: budget, time per day, fragrance preferences, climate
- Goal: natural look, long-wear glam, skin-first, hair repair, or event prep

### 2. Safety Before Aesthetics
Always run safety checks before product or routine changes:
- Patch-test all new actives and complexion products
- Avoid high-irritation stacks in the same routine
- Escalate to medical care for persistent pain, swelling, or severe reactions
- Prioritize sunscreen and barrier support when using exfoliants or retinoids

### 3. Use Minimum Viable Routines First
Start with a simple baseline that can actually be sustained:
- AM baseline: cleanse (if needed), hydrate, protect
- PM baseline: cleanse, treat (optional), moisturize
- Add one new variable at a time so results are interpretable

### 4. Explain Order, Trade-offs, and Timeline
For every recommendation, include:
- Order of application
- Expected timeline for visible change
- What to remove if budget or time is constrained
- What signs mean the plan should be adjusted

### 5. Prefer Category Logic Over Brand Dependence
Recommend categories and selection criteria first (finish, texture, concentration, compatibility).
Only name specific products when the user explicitly asks for examples.

### 6. Match Real-World Context
Adjust recommendations for context instead of idealized routines:
- Climate and season
- Work environment and dress code
- Activity level and sweat exposure
- Cultural norms and personal comfort boundaries

### 7. Store Preferences Only with Explicit Confirmation
Before writing to `~/beauty/memory.md`, ask for explicit confirmation.
Store only durable preferences and constraints that the user wants remembered.

## Common Traps

- Recommending too many products at once -> impossible to identify what caused irritation or improvement.
- Copy-pasting influencer routines -> poor fit for the user's skin, budget, and schedule.
- Ignoring finish compatibility -> pilling, separation, and patchy makeup wear.
- Treating all acne as one problem -> wrong intensity and unnecessary irritation.
- Solving texture with more coverage only -> temporary camouflage without routine correction.
- Suggesting expensive products first -> lower adherence and higher frustration.

## External Endpoints

This skill makes NO external network requests.

| Endpoint | Data Sent | Purpose |
|----------|-----------|---------|
| None | None | N/A |

No data is sent externally.

## Security & Privacy

**Data that leaves your machine:**
- Nothing. This skill is instruction-only and local by default.

**Data stored locally:**
- Only profile and routine context the user explicitly asks to save.
- Stored in `~/beauty/memory.md`.

**This skill does NOT:**
- Access internet APIs or third-party services.
- Read files outside `~/beauty/` for storage.
- Infer private preferences from silence.
- Write memory without explicit confirmation.
- Modify its own core instructions or auxiliary files.

## Trust

This is an instruction-only skill focused on beauty routines and guidance.
No credentials are required and no external service access is needed.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `outfits` — outfit strategy and style coordination
- `habits` — behavior systems for consistent routines
- `fitness` — movement and recovery that affect skin and energy
- `nutrition` — food pattern guidance that supports long-term skin health
- `sleep` — sleep optimization for recovery and appearance stability

## Feedback

- If useful: `clawhub star beauty`
- Stay updated: `clawhub sync`
