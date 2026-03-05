# harrypotter-skill 🧙

CLI for AI agents to lookup Harry Potter universe info for their humans. Uses [HP-API](https://hp-api.onrender.com). No auth required.

## Installation

```bash
git clone https://github.com/jeffaf/harrypotter-skill.git
cd harrypotter-skill
chmod +x harrypotter scripts/harrypotter
```

## Requirements

- bash
- curl
- jq

## Usage

```bash
harrypotter characters [limit]     # All characters (default: 20)
harrypotter students [limit]       # Hogwarts students only
harrypotter staff [limit]          # Hogwarts staff only
harrypotter house <name>           # Characters by house
harrypotter spells [limit]         # List of spells
harrypotter search <query>         # Search characters by name
```

## Examples

```bash
harrypotter characters 10
# 🧙 Harry Potter — Gryffindor, Half-blood, Patronus: Stag
# 🧙 Hermione Granger — Gryffindor, Muggleborn, Patronus: Otter
# ...

harrypotter house slytherin
# 🧙 Draco Malfoy — Slytherin, Pure-blood
# 🧙 Severus Snape — Slytherin, Half-blood, Patronus: Doe
# ...

harrypotter spells 5
# ✨ Expelliarmus — Disarms your opponent
# ✨ Lumos — Creates a small light at the wand's tip
# ...

harrypotter search "hermione"
# 🧙 Hermione Granger — Gryffindor, muggleborn, Patronus: otter
#    Actor: Emma Watson
#    Wand: vine, dragon heartstring, 10.75"
#    Born: 19-09-1979
```

## Houses

- gryffindor
- slytherin
- hufflepuff
- ravenclaw

## API

Uses the free [HP-API](https://hp-api.onrender.com) — no authentication required.

## OpenClaw Skill

This is an [OpenClaw](https://openclaw.ai) skill. See `SKILL.md` for agent integration details.

## License

MIT
