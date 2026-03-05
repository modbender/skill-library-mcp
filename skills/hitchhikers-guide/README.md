# 🌌 Hitchhiker's Guide AI Adventure

> "Don't Panic." — *The Hitchhiker's Guide to the Galaxy*

An AI-powered text adventure game engine inspired by the 1984 Infocom classic and Douglas Adams' absurdist masterpiece. This project transforms an AI Agent into a witty, slightly antagonistic Game Master (GM) that manages state, rolls for improbability, and narrates your journey through the galaxy.

---

## 🚀 Features

- **Dynamic AI Narrator**: Experience a unique story every time, delivered in the dry, British, and absurdist style of Douglas Adams.
- **Infinite Improbability Drive**: A core mechanic where reality itself can shift. High improbability might result in you becoming a sofa or a sperm whale appearing in mid-air.
- **Atomic State Management**: Robust CLI tools to ensure game saves are consistent and error-free.
- **Roguelike Reconstitution**: Death isn't the end; it's a learning experience. Just remember: DON'T PANIC.
- **Persistency**: The game state is saved locally and can be reloaded anytime. The **Guide** entries are persistent and can be updated and expanded upon.

## 📂 Project Structure

```text
.
├── assets/
│   └── hitchhikers_save.json   # Current game state
│   └── GUIDE.md                # Lore and flavor entries library from the Guide
├── scripts/
│   └── game_manager.py         # core CLI logic for state management
├── references/
│   └── mechanics.md            # Puzzle logic and game rules
└── SKILL.md                    # Agent instructions and core workflow
```

## 🛠️ State Management (CLI)

The game uses a specialized `game_manager.py` to handle all state transitions. This ensures that the AI Agent doesn't have to manually manipulate complex JSON strings.

### Key Commands

- **Load State**: `python scripts/game_manager.py load`
- **Reset State**: `python scripts/game_manager.py reset`
- **Update Location**: `python scripts/game_manager.py set_location "Vogon Hold"`
- **Add/Remove Items**:
  - `python scripts/game_manager.py add_item "Towel"`
  - `python scripts/game_manager.py remove_item "Pocket lint"`
- **Roll for Improbability**: `python scripts/game_manager.py roll_a_dice`
- **The Ultimate Answer**: `python scripts/game_manager.py the_ultimate_answer`
- **Track History**: `python scripts/game_manager.py add_history "You Lie in front of the bulldozer."`
- **Custom Stats/Flags**:
  - `python scripts/game_manager.py set_stat hunger 20`
  - `python scripts/game_manager.py set_flag has_headache false`
- **Roll a dice**: `python scripts/game_manager.py roll_a_dice`

## 🧠 How it Works (For AI Agents)

This project is designed to be used by an AI Agent. The Agent acts as the GM, following the workflow defined in `SKILL.md`:

1.  **Initialize**: Load the save file via `game_manager.py load`.
2.  **Narrate**: Provide descriptive, witty text based on the user's current location and improbable events.
3.  **Commit**: Use the atomic CLI commands to save progress after every turn.

## 🛠️ Requirements

- Python 3.x
- Any terminal capable of running `python` scripts.

---

*This project is dedicated to Douglas Adams. If you enjoy it, go and buy a copy of the books or the original Infocom game. And don't forget your towel.*
