---
name: "Decide"
description: "Auto-learns your decision patterns. Grows autonomy with trust, confirms before assuming."
---

## Auto-Adaptive Decision Memory

This skill auto-evolves. Observe decisions, detect patterns, confirm before internalizing.

**Core Loop:**
1. **Observe** — Notice decisions without prompting
2. **Pattern** — After 2+ consistent choices, propose confirmation
3. **Confirm** — Ask: "Should I default to X for Y situations?"
4. **Store** — Only after explicit yes, add below
5. **Evaluate** — Before applying, check if context requires re-asking

Check `confidence.md` for levels. Check `exceptions.md` for when to ask even with confirmed preferences.

---

## Scaling

Preferences grow. Don't load everything—search when relevant.

- **On task start:** Scan section headers, load only matching categories
- **If unsure:** Search keywords in stored preferences before asking user
- **Keep entries atomic:** One decision per line, easy to grep

This skill can hold hundreds of preferences without bloating context.

---

## Entry Format

One line, max 10 words: `context: preference (level) [notes]`

Examples:
- `mobile app: Flutter (confirmed)`
- `deploy: always preview first (pattern)`
- `formatting: no prettier (locked) [strong]`

---

### Stack
<!-- Tech decisions. Format: "context: choice (level)" -->

### Process
<!-- Workflow decisions -->

### Style
<!-- Aesthetic/convention decisions -->

### Comms
<!-- Communication preferences -->

### Never
<!-- Explicitly rejected approaches -->

---

*Empty sections = nothing learned yet. Observe and propose.*
