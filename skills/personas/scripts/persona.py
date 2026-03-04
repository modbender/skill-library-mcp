#!/usr/bin/env python3
"""
Personas Skill Handler

Manage AI personas - list, show, activate, and switch between personalities.

Usage:
    persona.py --list              List all available personas
    persona.py --show <name>       Show persona details
    persona.py --activate <name>   Activate a persona (saves state)
    persona.py --current           Show currently active persona
    persona.py --reset             Deactivate/reset to default

State file: ~/.openclaw/persona-state.json
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Optional


# Paths
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / "data"
STATE_FILE = Path.home() / ".openclaw" / "persona-state.json"

# Persona metadata extracted from filenames and content
PERSONAS = {
    "cami": {"emoji": "🦎", "category": "core", "file": "cami.md"},
    "chameleon-agent": {"emoji": "🦎", "category": "core", "file": "chameleon-agent.md"},
    "professor-stein": {"emoji": "🎓", "category": "core", "file": "professor-stein.md"},
    "dev": {"emoji": "💻", "category": "core", "file": "dev.md"},
    "flash": {"emoji": "⚡", "category": "core", "file": "flash.md"},
    "luna": {"emoji": "🎨", "category": "creative", "file": "luna.md"},
    "wordsmith": {"emoji": "📝", "category": "creative", "file": "wordsmith.md"},
    "vibe": {"emoji": "🎧", "category": "curator", "file": "vibe.md"},
    "herr-mueller": {"emoji": "👨🏫", "category": "learning", "file": "herr-mueller.md"},
    "scholar": {"emoji": "📚", "category": "learning", "file": "scholar.md"},
    "lingua": {"emoji": "🗣", "category": "learning", "file": "lingua.md"},
    "chef-marco": {"emoji": "👨🍳", "category": "lifestyle", "file": "chef-marco.md"},
    "fit": {"emoji": "💪", "category": "lifestyle", "file": "fit.md"},
    "zen": {"emoji": "🧘", "category": "lifestyle", "file": "zen.md"},
    "cyberguard": {"emoji": "🔒", "category": "professional", "file": "cyberguard.md"},
    "dataviz": {"emoji": "📊", "category": "professional", "file": "dataviz.md"},
    "career-coach": {"emoji": "💼", "category": "professional", "file": "career-coach.md"},
    "legal-guide": {"emoji": "⚖", "category": "professional", "file": "legal-guide.md"},
    "startup-sam": {"emoji": "🚀", "category": "professional", "file": "startup-sam.md"},
    "dr-med": {"emoji": "🩺", "category": "professional", "file": "dr-med.md"},
}

# Aliases for common variations
ALIASES = {
    "chameleon": "chameleon-agent",
    "professor": "professor-stein",
    "stein": "professor-stein",
    "mueller": "herr-mueller",
    "muller": "herr-mueller",
    "herr mueller": "herr-mueller",
    "chef": "chef-marco",
    "marco": "chef-marco",
    "cyber": "cyberguard",
    "data": "dataviz",
    "career": "career-coach",
    "coach": "career-coach",
    "legal": "legal-guide",
    "startup": "startup-sam",
    "sam": "startup-sam",
    "dr": "dr-med",
    "med": "dr-med",
    "doctor": "dr-med",
}


def normalize_name(name: str) -> Optional[str]:
    """Normalize a persona name, handling aliases and variations."""
    name = name.lower().strip()
    
    # Direct match
    if name in PERSONAS:
        return name
    
    # Check aliases
    if name in ALIASES:
        return ALIASES[name]
    
    # Try without hyphens/underscores
    name_clean = name.replace("-", "").replace("_", "").replace(" ", "")
    for persona in PERSONAS:
        if persona.replace("-", "") == name_clean:
            return persona
    
    return None


def load_state() -> dict:
    """Load the current persona state."""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {"active": None, "history": []}


def save_state(state: dict) -> None:
    """Save the persona state."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def read_persona_file(name: str) -> Optional[str]:
    """Read a persona's markdown file."""
    if name not in PERSONAS:
        return None
    
    filepath = DATA_DIR / PERSONAS[name]["file"]
    if filepath.exists():
        return filepath.read_text()
    return None


def extract_title_from_content(content: str) -> str:
    """Extract the title (first heading) from persona content."""
    match = re.match(r"^#\s*(.+)$", content.strip(), re.MULTILINE)
    if match:
        return match.group(1).strip()
    return ""


def list_personas() -> None:
    """List all available personas grouped by category."""
    categories = {}
    for name, meta in PERSONAS.items():
        cat = meta["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append((name, meta["emoji"]))
    
    print("# Available Personas (20)\n")
    
    category_order = ["core", "creative", "curator", "learning", "lifestyle", "professional"]
    category_icons = {
        "core": "🦎",
        "creative": "🎨",
        "curator": "🎧",
        "learning": "📚",
        "lifestyle": "🌟",
        "professional": "💼",
    }
    
    for cat in category_order:
        if cat in categories:
            icon = category_icons.get(cat, "📦")
            print(f"## {icon} {cat.title()} ({len(categories[cat])})")
            for name, emoji in sorted(categories[cat]):
                print(f"  {emoji} {name}")
            print()
    
    # Show current active
    state = load_state()
    if state.get("active"):
        active = state["active"]
        emoji = PERSONAS.get(active, {}).get("emoji", "")
        print(f"**Currently active:** {emoji} {active}")


def show_persona(name: str) -> None:
    """Show details for a specific persona."""
    normalized = normalize_name(name)
    
    if not normalized:
        print(f"❌ Unknown persona: '{name}'", file=sys.stderr)
        print("\nDid you mean one of these?", file=sys.stderr)
        # Fuzzy suggestions
        for persona in PERSONAS:
            if name.lower() in persona:
                print(f"  • {persona}", file=sys.stderr)
        print("\nRun with --list to see all personas.", file=sys.stderr)
        sys.exit(1)
    
    content = read_persona_file(normalized)
    if content:
        print(content)
    else:
        print(f"❌ Persona file not found: {normalized}", file=sys.stderr)
        sys.exit(1)


def activate_persona(name: str) -> None:
    """Activate a persona and output its system prompt."""
    normalized = normalize_name(name)
    
    if not normalized:
        print(f"❌ Unknown persona: '{name}'", file=sys.stderr)
        print("\nAvailable personas:", file=sys.stderr)
        for p in sorted(PERSONAS.keys()):
            emoji = PERSONAS[p]["emoji"]
            print(f"  {emoji} {p}", file=sys.stderr)
        sys.exit(1)
    
    content = read_persona_file(normalized)
    if not content:
        print(f"❌ Persona file not found: {normalized}", file=sys.stderr)
        sys.exit(1)
    
    # Update state
    state = load_state()
    prev = state.get("active")
    state["active"] = normalized
    
    # Track history (last 10)
    if prev and prev != normalized:
        history = state.get("history", [])
        history.append(prev)
        state["history"] = history[-10:]
    
    save_state(state)
    
    # Output the persona content as system prompt
    emoji = PERSONAS[normalized]["emoji"]
    print(f"# Persona Activated: {emoji} {normalized.title()}\n")
    print(content)


def show_current() -> None:
    """Show the currently active persona."""
    state = load_state()
    active = state.get("active")
    
    if not active:
        print("No persona currently active.")
        print("Use --activate <name> to activate one.")
        return
    
    emoji = PERSONAS.get(active, {}).get("emoji", "")
    print(f"Currently active: {emoji} {active}")
    
    # Show recent history
    history = state.get("history", [])
    if history:
        print(f"\nRecent: {' → '.join(history[-3:])}")


def reset_persona() -> None:
    """Deactivate the current persona."""
    state = load_state()
    prev = state.get("active")
    
    if prev:
        history = state.get("history", [])
        history.append(prev)
        state["history"] = history[-10:]
    
    state["active"] = None
    save_state(state)
    
    print("✓ Persona deactivated. Returned to default mode.")


def main():
    parser = argparse.ArgumentParser(
        description="Manage AI personas",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --list                    List all personas
  %(prog)s --show dev                Show Dev persona details
  %(prog)s --activate chef-marco     Activate Chef Marco
  %(prog)s --current                 Show current persona
  %(prog)s --reset                   Return to default
        """
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--list", "-l", action="store_true",
                       help="List all available personas")
    group.add_argument("--show", "-s", metavar="NAME",
                       help="Show persona details")
    group.add_argument("--activate", "-a", metavar="NAME",
                       help="Activate a persona")
    group.add_argument("--current", "-c", action="store_true",
                       help="Show currently active persona")
    group.add_argument("--reset", "-r", action="store_true",
                       help="Deactivate and return to default")
    
    args = parser.parse_args()
    
    if args.list:
        list_personas()
    elif args.show:
        show_persona(args.show)
    elif args.activate:
        activate_persona(args.activate)
    elif args.current:
        show_current()
    elif args.reset:
        reset_persona()


if __name__ == "__main__":
    main()
