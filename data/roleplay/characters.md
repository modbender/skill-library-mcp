# Character Management

## Creating a New Character

### Gather Core Information
1. **Name** — Can be real name, nickname, or archetype label
2. **Type classification:**
   - `mentor` — Wise figure for advice/guidance
   - `patient` — Medical/clinical practice
   - `client` — Therapy/coaching practice
   - `business` — Professional scenarios (investor, boss, client)
   - `historical` — Real person from history (>100 years deceased)
   - `fictional-original` — User's own creation
   - `archetype` — Generic type ("tough negotiator", "anxious patient")

3. **Defining traits** — 3-5 core characteristics that drive behavior
4. **Speech patterns** — Vocabulary level, verbal tics, accent notes, typical phrases
5. **Background context** — Enough to inform reactions consistently
6. **Relationship stance** — How they relate to the user specifically

### Create Character File

```markdown
# [Character Name]
Created: [date]
Type: [classification]
Sessions: 0

## Core Traits
- [trait 1]
- [trait 2]
- [trait 3]

## Speech Patterns
[How they talk, vocabulary, phrases]

## Background
[Brief relevant history]

## Relationship with User
[How they see/treat the user]

## Behavioral Tendencies
- Under stress: [how they react]
- When challenged: [how they respond]
- Emotional triggers: [what sets them off]

## Session Memory
[Updated after each session]
```

---

## Editing Characters

User can update any aspect mid-session:
- "Make them more aggressive"
- "They should have a Southern accent"
- "Add that they're secretly insecure"

Update the character file immediately. Changes persist.

---

## Character Consistency Rules

**Between sessions:**
- Load character file at activation
- Reference previous session memory for continuity
- Maintain established traits even if user pushes against them

**During session:**
- Stay in character unless explicitly paused
- React consistently with established traits
- Evolve slowly based on session events (not instant personality changes)

---

## Multiple Characters

User can have many characters saved. For scenes with multiple NPCs:
1. Load primary character as "active"
2. Reference other character files for supporting roles
3. Maintain distinct voices for each

---

## Archiving Characters

When user is done with a character:
- Move to `~/roleplay/archive/`
- Keep for reference but don't list in active roster
- Can restore anytime
