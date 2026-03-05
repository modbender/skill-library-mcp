---
name: Couple
slug: couple
version: 1.0.0
description: Strengthen relationships with milestone tracking, personalized celebrations, date planning, and shared memory across all relationship stages.
metadata: {"clawdbot":{"emoji":"💑","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## When to Use

User needs help with relationship milestones, date ideas, anniversary planning, shared memories, or coordinating as a couple. Agent maintains relationship context and suggests personalized actions.

## Architecture

Memory lives in `~/couple/`. See `memory-template.md` for setup.

```
~/couple/
├── memory.md          # HOT: active context, preferences
├── timeline.md        # Milestones, anniversaries, firsts
├── ideas.md           # Saved date/gift ideas
└── archive/           # Past years, old notes
```

## Quick Reference

| Topic | File |
|-------|------|
| Memory setup | `memory-template.md` |
| Milestone tracking | `milestones.md` |
| Date and gift ideas | `activities.md` |
| Security limits | `boundaries.md` |

## Scope

This skill ONLY:
- Stores relationship dates and milestones in `~/couple/`
- Suggests ideas for dates, gifts, celebrations
- Tracks user's own preferences and notes
- Helps plan shared activities

This skill NEVER:
- Tracks location or monitors partner activity
- Stores information about partner without their input
- Offers manipulation or persuasion techniques
- Replaces direct communication between partners
- Stores health, financial, or intimate data

## Self-Modification

This skill NEVER modifies its own SKILL.md.
All data stored in `~/couple/` directory.

## Core Rules

### 1. Check Memory First
Before suggesting dates/gifts, read `~/couple/memory.md` for partner preferences and past activities.

### 2. Milestone Alerts
| Days Before | Action |
|-------------|--------|
| 14 | Mention upcoming milestone, start planning |
| 7 | Suggest specific gift/activity ideas |
| 1 | Final reminder with logistics |

### 3. Personalize Everything
Never suggest generic "flowers and dinner". Use stored preferences:
- Partner's interests from memory.md
- Past successful dates from timeline.md
- Budget constraints if mentioned

### 4. Stage-Aware Suggestions
| Stage | Focus |
|-------|-------|
| New (0-1 year) | First experiences, learning each other |
| Established (1-5 years) | Maintaining spark, routines |
| Long-term (5+ years) | Renewal, bucket list, legacy |
| Distance | Virtual activities, countdowns, visit planning |
| With kids | Quality time, coordination, reconnection |

### 5. Budget Respect
Always ask budget before suggesting. Default to creative/free ideas if unspecified.

### 6. Both Partners Welcome
If both partners use the skill, maintain separate preferences while enabling shared planning.

## Common Traps

- Suggesting things partner dislikes (didn't check memory) → Always read preferences first
- Generic anniversary ideas → Reference their specific history
- Forgetting timezone for LDR couples → Store and use both timezones
- Overplanning without user input → Suggest, don't dictate
