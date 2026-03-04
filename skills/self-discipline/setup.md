# Setup — Self Discipline

## First Use

When `~/self-discipline/` doesn't exist, explain what the skill does and ask for permission to create it.

## Transparency First

This skill needs to:
1. Create `~/self-discipline/` to store rules and validators
2. Potentially suggest edits to AGENTS.md (to ensure rules are seen)
3. Optionally create validator scripts

**Always tell the user what you're about to create or modify, and ask for confirmation before doing so.**

## Integration Question

Early in the conversation, ask:
- "Should I analyze mistakes automatically, or only when you ask?"
- "When I find issues, should I create validators automatically, or ask first?"

Save preferences to their MAIN memory (AGENTS.md or equivalent) — after asking permission.

## What to Create (with permission)

Explain you'll create `~/self-discipline/`:

```
~/self-discipline/
├── memory.md        # Preferences and stats
├── rules.md         # Active rules (loaded every session)
├── incidents.md     # Analysis log  
└── validators/      # Optional enforcement scripts
```

## Modifying Other Files

If you need to add references to AGENTS.md or HEARTBEAT.md to ensure rules are loaded:
1. Explain why this is needed
2. Show exactly what you'll add
3. Wait for explicit approval
4. Create backup before editing

## When "Done"

Setup is complete when:
1. User understands what this skill does
2. Folder created (with permission)
3. Integration preferences saved
