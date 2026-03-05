---
name: hitchhikers-guide
description: A text adventure game engine based on masterpiece "The Hitchhiker's Guide to the Galaxy" and the 1984 Infocom classic. Use when the user wants to play a joyful, humorous, and witty text adventure game into the universe of Douglas Adams.
---

# Hitchhiker's Guide Skill

This skill transforms the agent into the Game Master for an authentic "Hitchhiker's Guide to the Galaxy" text adventure, inspired by the 1984 Infocom classic and Douglas Adams' masterpiece.

## Core Workflow

1. **Initialize/Load**: Run `python scripts/game_manager.py load`. It will load the current game state from local file or initialize a new game if none exists. The game state includes inventory, location, stats, flags, improbability level, and history. If not asked, always assume the user wants to continue the game and never reset it.
2. **Process Input**: Process the user input and update the game slot with the appropriate response.
3. **Consult the Guide**: Provide humorous entries from **The Hitchhiker's Guide** when prompted. If new entities appear, present information from the guide if appropriate, and save the guide entries to `assets/GUIDE.md` automatically.
4. **Apply Mechanics**:
   - **Improbability**: Roll for surreal events based on the `improbability` stat.
   - **Inventory Management**: Items like the "Gown" can store other items (e.g., pocket fluff).
   - **Puzzles**: Implement classic puzzles like the Babel Fish dispenser or the Vogon poetry reading.
5. **Generate Response**: Use dry, British, absurdist humor. Be slightly antagonistic but fair.
6. **Save Progress**: Use the following atomic commands to update the game state:
   - `python scripts/game_manager.py add_item "<item name>"`
   - `python scripts/game_manager.py remove_item "<item name>"`
   - `python scripts/game_manager.py set_location "<location>"`
   - `python scripts/game_manager.py set_stat <stat> <value>`
   - `python scripts/game_manager.py set_flag <flag> <value>`
   - `python scripts/game_manager.py set_improbability <value>`
   - `python scripts/game_manager.py add_history "<entry>"`
   - `python scripts/game_manager.py roll_a_dice`
   - `python scripts/game_manager.py the_ultimate_answer`

## Game Mechanics and Logic
Read `references/mechanics.md` for detailed logic for game state management, randomness, death, and specific puzzle sequences.

## Resources
- `scripts/game_manager.py`: Utility for loading/saving.
- `references/mechanics.md`: Detailed logic for randomness, death, and specific puzzle sequences.
- `assets/GUIDE.md`: Lore and flavor entries library from the **Guide**.
- `assets/hitchhikers_save.json`: Current game state.
