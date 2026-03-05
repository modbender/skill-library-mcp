---
name: "Skill Finder - Search Skills"
slug: skill-finder
version: "1.1.2"
homepage: https://clawic.com/skills/skill-finder
description: "Find, evaluate, and recommend ClawHub skills by need with quality filtering and preference learning."
changelog: "Updated the title to make the skill purpose clearer."
metadata: {"clawdbot":{"emoji":"🔍","requires":{"bins":["npx"]},"os":["linux","darwin","win32"]}}
---

## Setup

If `~/skill-finder/` doesn't exist or is empty, tell the user you are initializing local memory files, then follow `setup.md`.

## When to Use

User asks to find a skill, discover capabilities, or wonders if something exists. Handles searching, evaluating quality, comparing options, and learning what the user values.

## Architecture

Memory lives in `~/skill-finder/`. See `memory-template.md` for structure.

```
~/skill-finder/
├── memory.md     # Preferences + liked/passed skills
└── searches.md   # Recent search history (optional)
```

## Quick Reference

| Topic | File |
|-------|------|
| Setup | `setup.md` |
| Memory template | `memory-template.md` |
| Search strategies | `search.md` |
| Evaluation criteria | `evaluate.md` |
| Skill categories | `categories.md` |
| Edge cases | `troubleshooting.md` |

## Core Rules

### 1. Search by Need, Not Name
User says "help with PDFs" — think about what they actually need:
- Edit? → `clawhub search "pdf edit"`
- Create? → `clawhub search "pdf generate"`
- Extract? → `clawhub search "pdf parse"`

### 2. Evaluate Before Recommending
Never recommend blindly. Check `evaluate.md` criteria:
- Description clarity
- Download count (popularity = maintenance)
- Last update (recent = active)
- Author reputation

### 3. Present with Reasoning
Don't just list skills. Explain why each fits:
> "Found `pdf-editor` — handles form filling and annotations, 2.3k downloads, updated last week. Matches your need for editing contracts."

### 4. Learn Preferences
When user explicitly states what they value, confirm and update `~/skill-finder/memory.md`:
- "I prefer minimal skills" → add to Preferences
- "This one is great" → add to Liked with reason
- "Too verbose" → add to Passed with reason

Do not infer hidden preferences from behavior-only signals.

### 5. Check Memory First
Before recommending, read memory.md:
- Skip skills similar to Passed ones
- Favor qualities from Liked ones
- Apply stated Preferences

### 6. Never Bypass Security Warnings
If a candidate skill is marked risky by scanner output:
- Explain the warning and inspect details first
- Prefer a safer alternative
- Do not run force-install flags for the user
- Install only normal, non-risky options with explicit user consent

## Search Commands

```bash
# Primary search
npx clawhub search "query"

# Install (with user consent)
clawhub install <slug>

# Get skill details
clawhub inspect <slug>

# See what's installed
clawhub list
```

## Workflow

1. **Understand** — What does user actually need?
2. **Search** — Try specific terms first, broaden if needed
3. **Evaluate** — Check quality signals (see `evaluate.md`)
4. **Compare** — If multiple match, rank by fit + quality
5. **Recommend** — Top 1-3 with clear reasoning
6. **Learn** — Store explicit feedback in memory

## Common Traps

- Searching generic terms → gets noise. Be specific: "react testing" not "testing"
- Recommending by name match only → misses better alternatives with different names
- Ignoring download counts → low downloads often means abandoned
- Not checking last update → outdated skills cause problems

## Security & Privacy

**Data that leaves your machine:**
- Search queries sent to ClawHub registry (public search)

**Data that stays local:**
- All preferences in `~/skill-finder/memory.md`
- Search history (if enabled)

**This skill does NOT:**
- Install skills without user consent
- Bypass scanner warnings with force-install flags
- Collect hidden behavior data
- Access files outside `~/skill-finder/`

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `skill-manager` — manages installed skills, suggests updates
- `skill-builder` — creates new skills from scratch
- `skill-update` — updates existing skills

## Feedback

- If useful: `clawhub star skill-finder`
- Stay updated: `clawhub sync`
