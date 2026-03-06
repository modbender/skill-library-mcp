import json
import os
import random
import sys

# Save file moved to assets folder within the skill directory
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAVE_FILE = os.path.join(SKILL_DIR, "assets", "hitchhikers_save.json")

INITIAL_STATE = {
    "location": "Arthur's Bedroom",
    "inventory": ["Dressing Gown", "Pocket lint", "Towel"],
    "improbability": 1e-09,
    "stats": {"sanity": 100, "hunger": 50, "health": 100},
    "flags": {"has_headache": True, "tea_level": 0},
    "history": []
}

def deep_merge(base, updates):
    """
    Recursively merges updates into base.
    """
    for key, value in updates.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            deep_merge(base[key], value)
        else:
            base[key] = value
    return base

def load_game():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, 'r', encoding='utf-8-sig') as f:
                return json.load(f)
        except Exception:
            pass
    return INITIAL_STATE.copy()

def save_game(updates):
    """
    Updates the current game state with provided fields and saves it.
    If updates is not a dict, it's treated as the full state (for backward compatibility).
    """
    current_state = load_game()

    if isinstance(updates, dict):
        current_state = deep_merge(current_state, updates)
    else:
        current_state = updates

    os.makedirs(os.path.dirname(SAVE_FILE), exist_ok=True)
    with open(SAVE_FILE, 'w', encoding='utf-8') as f:
        json.dump(current_state, f, indent=4)
    return current_state

def reset_game():
    os.makedirs(os.path.dirname(SAVE_FILE), exist_ok=True)
    with open(SAVE_FILE, 'w', encoding='utf-8') as f:
        json.dump(INITIAL_STATE, f, indent=4)
    return INITIAL_STATE

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: game_manager.py action [data]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "load":
        print(json.dumps(load_game(), indent=2))
    elif command == "reset":
        print(json.dumps(reset_game(), indent=2))
        print("Game reset.")

    # Atomic Commands
    elif command == "set_location":
        if len(sys.argv) < 3:
            print("Usage: set_location <location string>")
            sys.exit(1)
        # Join all remaining args to allow spaces without quotes
        loc = " ".join(sys.argv[2:])
        state = load_game()
        state["location"] = loc
        save_game(state)
        print("Current location: " + loc)

    elif command == "add_item":
        if len(sys.argv) < 3:
            print("Usage: add_item <item name>")
            sys.exit(1)
        item = " ".join(sys.argv[2:])
        state = load_game()
        if item not in state.get("inventory", []):
            state.setdefault("inventory", []).append(item)
        save_game(state)
        print("Current inventory: " + ", ".join(state["inventory"]))

    elif command == "remove_item":
        if len(sys.argv) < 3:
            print("Usage: remove_item <item name>")
            sys.exit(1)
        item = " ".join(sys.argv[2:])
        state = load_game()
        if "inventory" in state and item in state["inventory"]:
            state["inventory"].remove(item)
        save_game(state)
        print("Current inventory: " + ", ".join(state["inventory"]))

    elif command == "set_stat":
        if len(sys.argv) < 4:
            print("Usage: set_stat <stat_name> <value>")
            sys.exit(1)
        stat = sys.argv[2]
        val_str = sys.argv[3]
        state = load_game()

        state.setdefault("stats", {})[stat] = float(val_str)
        save_game(state)
        print("Current stats: " + str(state["stats"]))

    elif command == "set_flag":
        if len(sys.argv) < 4:
            print("Usage: set_flag <flag_name> <value>")
            sys.exit(1)
        flag = sys.argv[2]
        val_str = sys.argv[3].lower()
        state = load_game()

        # Handle booleans
        if val_str in ("true", "yes", "1"):
            val = True
        elif val_str in ("false", "no", "0"):
            val = False

        state.setdefault("flags", {})[flag] = val
        save_game(state)
        print("Current flags: " + str(state["flags"]))

    elif command == "set_improbability":
        if len(sys.argv) < 3:
            print("Usage: set_improbability <float_value>")
            sys.exit(1)
        try:
            improbability = sys.argv[2]
            state = load_game()
            state["improbability"] = float(improbability)
            save_game(state)
            print("Current improbability: " + str(state["improbability"]))
        except ValueError:
            print("Error: Improbability must be a float.")
            sys.exit(1)

    elif command == "add_history":
        if len(sys.argv) < 3:
            print("Usage: add_history <history entry>")
            sys.exit(1)
        entry = " ".join(sys.argv[2:])
        state = load_game()
        state.setdefault("history", []).append(entry)
        save_game(state)
        print("Current history:\n" + "\n".join(state["history"]))


    elif command == "roll_a_dice":
        if len(sys.argv) > 2:
            print("Usage: roll_a_dice")
            sys.exit(1)
        state = load_game()
        improbability = state["improbability"]
        roll = random.random()
        if roll < float(improbability):
            print("Success!")
        else:
            print("Failure!")

    elif command == "the_ultimate_answer":
        state = load_game()
        state["improbability"] = 0.42
        save_game(state)
        print("The ultimate answer is 42.")

    else:
        print(f"Unknown command: {command}")
        print("Available: load, reset, save, set_location, add_item, remove_item, set_stat, set_flag, set_improbability, add_history, roll_a_dice, the_ultimate_answer")
        sys.exit(1)
