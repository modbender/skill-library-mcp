# 🎭 Personas

20 built-in AI personas for OpenClaw. Switch styles and domain focus instantly (e.g., Dev for coding, Wordsmith for writing, Chef Marco for cooking).

## Quick Start

Activate:
- "Use Dev"
- "Switch to Chef Marco"
- "Activate Dr. Med"

List:
- "List all personas"
- `/persona list`
- `/personas`

Exit:
- "Exit persona mode"
- `/persona exit`

## Included Personas (20)

- **Core (5):** Cami, Chameleon Agent, Professor Stein, Dev, Flash
- **Creative (2):** Luna, Wordsmith
- **Curator (1):** Vibe
- **Learning (3):** Herr Müller, Scholar, Lingua
- **Lifestyle (3):** Chef Marco, Fit, Zen
- **Professional (6):** CyberGuard, DataViz, Career Coach, Legal Guide, Startup Sam, Dr. Med

## CLI Script

This skill ships with `scripts/persona.py` for local persona management.

```bash
python3 scripts/persona.py --list
python3 scripts/persona.py --show dev
python3 scripts/persona.py --activate luna
python3 scripts/persona.py --current
python3 scripts/persona.py --reset
```

What it does:
- Reads bundled persona markdown files from `data/`
- Resolves common aliases (`chef`, `dr`, etc.)
- Stores active persona state at `~/.openclaw/persona-state.json`

What it does **not** do:
- No network calls
- No automatic downloads
- No guided/custom persona creation workflow

## Notes

- Token-efficient: only one persona is active at a time.
- You can switch personas mid-conversation.
- Medical/legal personas are educational only, not professional advice.

## License

Based on Chameleon AI Chat personas, adapted for OpenClaw (MIT).