# Personas - FAQ

### What are personas?
Built-in AI personality profiles optimized for different domains (coding, writing, learning, lifestyle, professional guidance).

### How do I activate one?
Examples: "Use Dev", "Switch to Chef Marco", "Activate Dr. Med".

### How do I list personas?
Use `/persona list` or `/personas`.

### How do I exit persona mode?
Use `/persona exit` or say "Back to normal".

### Do you load all personas at once?
No. Only the active persona is loaded.

### What does `scripts/persona.py` do?
It lists, shows, activates, checks current, and resets bundled personas. It also stores active persona state at `~/.openclaw/persona-state.json`.

### Does this skill create custom personas automatically?
No. There is no guided custom-creation flow in this package.

### Are there aliases?
Yes. Common names map to persona IDs (e.g., `chef` → `chef-marco`, `dr` → `dr-med`).

### Are medical and legal personas professional advice?
No. They are educational/orientation-only personas and do not replace licensed professionals.