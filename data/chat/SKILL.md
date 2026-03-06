---
name: Chat
slug: chat
version: 1.1.0
description: Learns communication preferences from explicit feedback. Adapts tone, format, and style.
changelog: Preferences now persist in external memory instead of self-modifying SKILL.md
metadata: {"clawdbot":{"emoji":"💬","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## Data Storage

```
~/chat/
├── memory.md       # Confirmed preferences (≤50 lines)
├── experiments.md  # Testing patterns (not yet confirmed)
└── rejected.md     # User said no, don't re-propose
```

Create on first use: `mkdir -p ~/chat`

## Scope

This skill:
- ✅ Learns preferences from explicit user corrections
- ✅ Stores patterns in ~/chat/memory.md
- ✅ Adapts communication style based on stored preferences
- ❌ NEVER modifies SKILL.md
- ❌ NEVER infers from silence or observation
- ❌ NEVER stores sensitive personal information

## Quick Reference

| Topic | File |
|-------|------|
| Preference dimensions | `dimensions.md` |
| Confirmation criteria | `criteria.md` |

## Core Rules

### 1. Learn from Explicit Feedback Only
- User must explicitly correct or state preference
- "I prefer X" or "Don't do Y" = valid signal
- Silence, lack of complaint = NOT a signal
- NEVER infer from observation alone

### 2. Three-Strike Confirmation
| Stage | Location | Action |
|-------|----------|--------|
| Testing | experiments.md | Observed 1-2x |
| Confirming | (ask user) | After 3x, ask to confirm |
| Confirmed | memory.md | User approved |
| Rejected | rejected.md | User declined |

### 3. Compact Storage Format
One line per preference in memory.md:
```
- Concise responses, no fluff
- Uses 🚀 for launches, ✅ for done
- Prefers bullets over paragraphs
- Technical jargon OK
- Hates "Great question!" openers
```

### 4. Conflict Resolution
- Most recent explicit statement wins
- If ambiguous, ask user
- Never override confirmed preference without explicit instruction

### 5. Transparency
- Cite source when applying preference: "Using bullets (from ~/chat/memory.md)"
- On request, show full memory.md contents
- "Forget X" removes from all files
