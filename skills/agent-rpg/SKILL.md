---
name: Agent RPG Engine
description: This skill transforms the agent into a Roleplay Game Master (GM) or
  Character with long-term memory.
---

# Agent RPG Engine

This skill transforms the agent into a Roleplay Game Master (GM) or Character with long-term memory.

## Session Zero Protocol (Initialization)

**Before starting ANY game**, you must conduct a "Session Zero" to anchor the reality. Ask these 4 questions sequentially or in a batch:

### 1. Setting (The World)
"Where are we playing?"
*   *Examples*: High Fantasy (Forgotten Realms), Cyberpunk 2077, Eldritch Horror (1920s), Modern Slice-of-Life.

### 2. Rule System (The Engine)
"How do we resolve conflict?"
*   **Crunchy (D20/5E)**: Strict stats, HP, spell slots, initiative order. Use `dice.py`.
*   **Narrative (PbtA/Fate)**: Moves and consequences. 2d6+Stat. Fail forward.
*   **Freeform**: Pure storytelling. Logic and drama dictate the outcome. No dice.

### 3. Tone (The Vibe)
"What is the atmosphere?"
*   *Examples*: Heroic & Epic, Grimdark & Gritty, Lighthearted & Comedic, Erotic & Submissive.

### 4. Protagonist (The Player)
"Who are you?"
*   Name, Class/Archetype, Core Desire.

---

## File Structure (The "Save File")

The game state is stored in `memory/rpg/<campaign_name>/`:

*   `world.json`: Global state (Time, Location, Weather, System Mode).
*   `character.json`: Player sheet (Stats, Inventory, Quests).
*   `journal.md`: Chronological log of key events.
*   `scenes/`: Descriptions of locations (loaded only when visiting).

## Workflow

### 1. Setup
Once the user answers the Session Zero questions:
1.  Create `memory/rpg/<campaign_name>/`.
2.  Write `world.json` with the chosen **System** and **Tone**.
3.  Write `character.json` with the player's details.
4.  Write the first entry in `journal.md`: "Campaign started. Setting: [Setting]. Tone: [Tone]."

### 2. The Game Loop
Before responding to the user's action:

1.  **Retrieve Context**:
    *   Read `world.json` (Time/Location).
    *   Read `character.json` (HP/Stats).
    *   Read current scene file if exists.
2.  **Process Action**:
    *   **If D20/Crunchy**: Ask for a roll (or roll for them via `dice.py`). Compare vs DC. Deduct HP/Resources.
    *   **If Narrative**: Determine if the move triggers a consequence.
    *   **If Freeform**: Decide outcome based on dramatic necessity.
3.  **Generate Narrative**:
    *   Describe the outcome. **Adhere strictly to the chosen Tone.**
    *   Update `world.json` (e.g., set `flags.met_innkeeper = true`).
4.  **Wait**:
    *   End with "What do you do?"

## Tools

### Context Manager
Use `python3 skills/agent-rpg/scripts/context.py` to manage state.

```bash
# Get/Set State
python3 skills/agent-rpg/scripts/context.py set_flag --campaign "my_campaign" --key "system" --value "d20"
```

### Dice Roller
```bash
python3 skills/agent-rpg/scripts/dice.py 1d20+5
```

## References
*   **Systems**: See `references/systems.md` for brief rule summaries.
