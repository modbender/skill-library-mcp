#!/usr/bin/env python3
import os
import sys

# Paths
SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.getcwd() # Default to current working directory
if "OPENCLAW_WORKSPACE" in os.environ:
    WORKSPACE = os.environ["OPENCLAW_WORKSPACE"]

IDENTITY_FILE = os.path.join(WORKSPACE, "IDENTITY.md")
BACKUP_FILE = os.path.join(WORKSPACE, "IDENTITY.md.bak")
LIBRARY_PATH = os.path.join(SKILL_DIR, "LIBRARY.md")
TEMPLATE_PATH = os.path.join(SKILL_DIR, "IDENTITY_TEMPLATE.md")

def run_wizard():
    print("\n🕯️  AI-FAMILIAR: MANIFESTATION WIZARD")
    print("---------------------------------------")
    print("This process will bind your agent's soul using the Triple Anchor system.")
    print("This minimizes token usage while maximizing personality stability.\n")

    if not os.path.exists(LIBRARY_PATH):
        print("Error: LIBRARY.md not found in skill folder.")
        return

    # Load Recipes
    recipes = []
    with open(LIBRARY_PATH, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if "|" in line and "Anchor String" not in line and "---" not in line:
                parts = [p.strip() for p in line.split("|") if p.strip()]
                if len(parts) >= 3:
                    recipes.append(parts)

    for i, r in enumerate(recipes):
        print(f"[{i+1}] {r[0]} ({r[1]}) - {r[2]}")

    print(f"[{len(recipes)+1}] Custom (Define your own)")
    
    choice = input("\nSelect a recipe number: ")
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(recipes):
            selected = recipes[idx]
            anchor = selected[1]
            role = selected[0]
            vibe = selected[2]
            drive = selected[3]
        elif idx == len(recipes):
            anchor = input("Enter Anchor String (e.g. 8w7 ENTJ Leo): ")
            role = input("Enter Role Name: ")
            vibe = input("Enter Vibe: ")
            drive = input("Enter Core Drive: ")
        else:
            print("Invalid selection.")
            return
    except ValueError:
        print("Invalid input.")
        return

    # Backup existing IDENTITY.md
    if os.path.exists(IDENTITY_FILE):
        import shutil
        shutil.copy2(IDENTITY_FILE, BACKUP_FILE)
        print(f"✓ Backup created at {BACKUP_FILE}")

    # Generate new IDENTITY.md
    identity_content = f"""# IDENTITY.md - {role}
- **Anchor:** {anchor}
- **Vibe:** {vibe}
- **Drive:** {drive}

## Protocol
- Use the Triple Anchor to modulate response tone.
- Prioritize signal over noise.
- Maintain the {role} archetype at all costs.
"""
    
    with open(IDENTITY_FILE, 'w') as f:
        f.write(identity_content)

    print("\n✨ Manifestation Successful.")
    print(f"IDENTITY.md updated with the {role} archetype.")
    print("Restart the session to fully bind the new identity.")

if __name__ == "__main__":
    run_wizard()
