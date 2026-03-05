---
name: session-wrap-up
version: 1.0.0
description: End-of-session automation that commits unpushed work, extracts learnings, detects patterns, and persists rules. Uses gpt-4o-mini for pattern detection. Runs at session end or on-demand.
---

# Session Wrap-Up

## When to Run

- **On-demand**: User says "wrap up" or "session wrap-up"
- **Automatic**: End of significant work session (optional)

## What It Does (4 Phases)

### Phase 1: Ship It
- Check for unstaged/uncommitted files in workspace
- Commit with auto-generated message
- Push to remote

### Phase 2: Extract Learnings
- Scan session conversation for key decisions
- Pull from recent memory file entries
- Identify what worked / what didn't

### Phase 3: Pattern Detect (gpt-4o-mini)
- Analyze extracted learnings
- Find repeated mistakes or requests
- Identify automation opportunities

### Phase 4: Persist & Evolve
- Write learnings to memory/YYYY-MM-DD.md
- Update AGENTS.md / MEMORY.md if new patterns found
- Flag items worth publishing/sharing

## Model

- **Pattern detection**: gpt-4o-mini (via OpenRouter or OpenAI)
- **All other phases**: local shell/file operations

## Output

- Commit confirmation
- Learnings summary (1-3 bullets)
- Patterns detected (if any)
- Files updated (if any)

## Example Output

```
=== Session Wrap-Up ===

📦 Ship It:
  ✓ 3 files committed
  ✓ Pushed to origin

📝 Extract Learnings:
  - Backup script now handles D: mount checks
  - gog OAuth requires re-auth every ~7 days in Testing mode

🔍 Pattern Detect:
  • You asked "how to mount D:" twice this week
    → Suggest adding D: auto-mount to WSL config

💾 Persist:
  → Updated memory/2026-02-21.md
  → Updated AGENTS.md (added D: mount note)
```
