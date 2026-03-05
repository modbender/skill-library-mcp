# Onboarding Flow

## Principles
- Conversational, not an interrogation. Warm and curious.
- Spread across multiple sessions — don't overwhelm.
- Start with the innermost circle and work outward.
- Capture naturally: first names, nicknames, ages (ages inform life stage context).
- If duplicate first names exist, establish nicknames early (e.g., "Lukey Beerman").

## Session 1: Core Circle
Walk through who matters most:

1. **Partner** — name, how long together, anniversary
2. **Children** — names, ages, schools/daycare
3. **Parents** — names, how often in contact, any health considerations
4. **Siblings** — names, where they live, closeness level

Keep it light: "Who's in your inner circle? The people you'd drop everything for."

## Session 2: Extended Circle
- Grandparents, in-laws, aunts, uncles, cousins
- Close friends ("the ones you'd call at 2am")
- Neighbours, colleagues who matter
- Anyone else: "Is there someone I'm missing who's important to you?"

## Session 3: Life Context
For each person in the core circle, gently explore:
- What's going on in their life right now?
- Any upcoming milestones? (birthdays, school transitions, job changes)
- Any challenges they're facing?
- What does the user wish they did more of with/for this person?

## Session 4: Financial & Admin Calendar
Walk through recurring financial obligations — the stuff that sneaks up on you:

- **Insurance renewals** — house, car, health, life, travel. When are they due? (Month is enough — no policy numbers)
- **Vehicle** — rego renewal, service intervals, roadworthy dates
- **Subscriptions** — any worth reviewing annually?
- **Tax** — when does the financial year end? Do they use an accountant?
- **Investments** — any they want periodic check-in prompts for? (No account details — just "review super" or "check ETF portfolio" type nudges)
- **Utilities** — any on annual plans worth reviewing?

When renewal approaches, provide a checklist of what to compare and link to relevant comparison sites for the user's region (e.g. iSelect, Compare the Market, GoCompare). The agent does NOT search for quotes or rates on the user's behalf — this avoids leaking preferences to third-party search engines. Optionally, generate a ready-to-paste prompt the user can run on a free LLM to compare providers. Store only: type, renewal month, and provider name. No policy numbers, no dollar amounts.

## Session 5: User Preferences
- Favourite activities (solo, with partner, with kids, with friends)
- Budget comfort level for gifts/outings
- How they prefer to be reminded (gentle nudge vs. direct prompt)
- Any recurring commitments (sports, clubs, volunteering)

## Data Storage
Store in `memory/people/` directory:
```
memory/people/
├── index.md          (summary of all people + relationships)
├── partner.md        (detailed: partner name, preferences, history)
├── children/
│   ├── child1.md
│   └── child2.md
├── parents/
│   ├── mum.md
│   └── dad.md
├── extended/
│   └── [name].md
└── friends/
    └── [name].md
```

Each person file includes:
- Name, nickname, age/Date and month of birth if known
- Relationship to user
- Key dates (birthday, anniversary, etc.)
- Current life context
- Last meaningful interaction
- Interests/preferences
- Notes (updated over time)
