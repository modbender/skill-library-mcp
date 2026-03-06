# 🎯 context-switcher

> Switch your AI assistant's entire behavior based on the mode of life you're in.

![ClawHub](https://img.shields.io/badge/ClawHub-skill-blue)
![Version](https://img.shields.io/badge/version-1.0.0-green)
![No External Calls](https://img.shields.io/badge/external%20calls-none-brightgreen)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

---

## Install

```bash
clawhub install context-switcher
```

Or manually copy this folder to `~/.openclaw/skills/context-switcher/` and restart OpenClaw.

---

## What It Does

When you switch modes, OpenClaw doesn't just change a label — it reshapes everything:

| Mode | Notifications | Memory Loaded | Response Style |
|------|--------------|---------------|----------------|
| 🧠 Work/Focus | Personal muted | Tasks, projects, deadlines | Concise, task-first |
| 🏠 Personal | Work muted | Errands, goals, people | Warm, conversational |
| 🎨 Creative | All muted | Projects, inspiration, ideas | Expansive, yes-and |
| 🔕 Do Not Disturb | All muted | Nothing surfaced | Silent, logs only |

---

## How to Trigger It

Just say it naturally in any message:

```
"Switch to focus mode"
"Personal time, I'm done for the day"
"Creative mode — working on my novel"
"DND until my next meeting"
"Going dark for 2 hours"
"I need to focus"
```

Or it triggers automatically from **calendar event titles** — words like "standup", "family dinner", "writing session", or "deep work" will auto-activate the matching mode.

---

## Customize Your Modes

Edit the files in `modes/` to make each mode personal to you:

- `modes/work.md` — your projects, team, weekly priorities
- `modes/personal.md` — your goals, errands, important people
- `modes/creative.md` — your active projects, inspiration sources

The more you fill these in, the smarter each mode becomes.

---

## Auto-Restore

OpenClaw automatically restores your previous state when:
- A calendar event ends
- A timer you set expires (e.g. "focus mode for 90 minutes")
- You say "exit [mode] mode" or "restore"

On restore, you get a brief catch-up summary of what came in while you were in the session.

---

## Security

This skill is **100% local**. No data is sent to any external service. No API keys required. All state lives in `~/.openclaw/skills/context-switcher/`.

See the `External Endpoints` and `Security & Privacy` sections in `SKILL.md` for full details.

---

## File Structure

```
context-switcher/
├── SKILL.md                    ← Core skill instructions
├── README.md                   ← This file
├── current-context.json        ← Live mode state
├── modes/
│   ├── work.md                 ← Customize work mode
│   ├── personal.md             ← Customize personal mode
│   └── creative.md             ← Customize creative mode
├── scripts/
│   ├── switch.sh               ← Core switching logic
│   ├── restore.sh              ← Auto-restore handler
│   └── summarize.sh            ← Session summary generator
└── snapshots/
    ├── pre-switch-state.json   ← State saved before each switch
    └── dnd-log.json            ← Messages logged during DND
```

---

## License

MIT — use freely, modify, share.

---

## Contributing

Found a bug or have an idea? Open an issue or PR on GitHub. This skill is intentionally minimal — improvements should stay lightweight and local-first.
