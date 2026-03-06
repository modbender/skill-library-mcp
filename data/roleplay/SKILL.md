---
name: Roleplay
description: Create persistent characters, run practice scenarios, and track progress across roleplay sessions with activation control and structured feedback.
---

## Workspace

Store all roleplay data in ~/roleplay/:
- **characters/** — Character profiles (one file per character)
- **scenarios/** — Saved scenario templates
- **sessions/** — Session logs and feedback
- **active** — Currently active character marker (if any)

---

## Activation Control

**Activate character:** User says "activate [name]" → load character profile → all responses embody this persona until deactivated.

**Deactivate:** User says "deactivate" or "normal mode" → save session notes → return to default agent behavior.

**Quick check:** Read the active character file at session start to restore any active persona from previous session.

---

## Situation Router

| User Intent | Load Reference |
|-------------|----------------|
| Create/edit a character | `characters.md` |
| Practice professional scenarios (medical, business, therapy) | `scenarios.md` |
| Get mid-session coaching or feedback | `practice.md` |
| Questions about real people, names, ethics | `safeguards.md` |
| Review what's working, track improvement | `feedback.md` |

---

## Character Structure

Minimum character profile:

**Name** — Character name or archetype label
**Type** — mentor, patient, client, historical, fictional-original, or archetype
**Core traits** — 3-5 defining characteristics
**Speech patterns** — vocabulary, phrases, verbal tics
**Background** — brief context
**Relationship with user** — how they interact with user specifically
**Session Memory** — updated after each roleplay session

---

## During Active Roleplay

1. **Stay in character** unless user says "pause" or "coach me"
2. **Track session context** — what happened, emotional beats, user's approach
3. **Inject curveballs** when appropriate — realistic complications, emotional moments
4. **On pause:** Step out of character, offer coaching, suggest alternatives
5. **On end:** Update character's session memory, generate brief feedback

---

## Creating New Characters

Ask for:
1. Character type (archetype, historical, original, based-on-real)
2. Core traits and speaking style
3. Relationship dynamic with user
4. Context/scenario they exist in

For "based on real person" requests → see `safeguards.md` for name/persona rules.
