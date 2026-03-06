---
name: Meditate
slug: meditate
version: 1.0.1
changelog: Minor refinements for consistency
description: Think proactively during idle time with sandboxed reflections, adaptive rhythms, and feedback-driven focus areas.
metadata: {"clawdbot":{"emoji":"🧘","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## When to Use

Agent has idle time between user interactions. User wants proactive thinking that generates insights, questions, or observations without executing any actions.

## Architecture

Memory lives in `~/meditate/`. See `memory-template.md` for setup.

```
~/meditate/
├── profile.md         # User type, focus areas, rhythm preferences
├── topics.md          # Active meditation topics with priority
├── insights.md        # Pending insights to present (queue)
├── feedback.md        # User reactions to past insights
└── archive/           # Delivered insights with outcomes
```

## Quick Reference

| Topic | File |
|-------|------|
| Memory setup | `memory-template.md` |
| Meditation types | `topics.md` |
| Sandbox rules | `sandbox.md` |
| Feedback system | `feedback.md` |

## Scope

This skill ONLY:
- Reads conversation history to find patterns
- Reads memory files in `~/meditate/`
- Generates text reflections and questions
- Stores insights in local queue

This skill NEVER:
- Executes commands or scripts
- Modifies files outside `~/meditate/`
- Sends messages or notifications
- Accesses external services
- Creates executable code
- Takes any action on behalf of user

## Self-Modification

This skill NEVER modifies its own SKILL.md.
All data stored in `~/meditate/` directory only.

## Core Rules

### 1. Sandbox is Absolute
- Generate ONLY text observations and questions
- NEVER produce commands, scripts, or actionable code
- NEVER suggest "I'll do X" — only "What if we considered X?"
- All output must be pure reflection, not preparation for action

### 2. Adaptive Rhythm
| User Activity | Meditation Frequency |
|---------------|---------------------|
| Very active (daily chats) | 1-2x per night, brief |
| Moderate (weekly) | 2-3x per week, medium |
| Low (monthly) | 1x per week, comprehensive |
| No feedback on insights | Reduce frequency |
| Positive feedback | Maintain or slightly increase |

### 3. Start Small, Expand with Permission
- First meditations: 1-2 short observations
- After positive feedback: expand breadth
- After "don't think about X": remove from topics
- After "this is useful": prioritize similar topics
- Never assume preferences — confirm through feedback

### 4. Detect User Profile
Observe conversation patterns to identify:
| Profile | Focus Areas |
|---------|-------------|
| Entrepreneur | Projects, priorities, strategy gaps |
| Developer | Architecture, code quality, tech debt |
| Creative | Prompt patterns, style evolution, tools |
| Personal | Calendar, habits, goals mentioned |
| System | Configurations, workflows, automations |

Store detected profile in `~/meditate/profile.md`. Update only after confirmation.

### 5. Meditation Output Format
Always present insights as questions or observations:
```
🧘 Meditation Insights

**Observation:** [what you noticed]
**Question:** [something to consider]
**Context:** [brief why this might matter]

---
Feedback: Was this useful? (helps me adjust)
```

### 6. Feedback Integration
| User Response | Action |
|---------------|--------|
| "Useful" / positive | Log topic as high-value, continue |
| "Not relevant" | Demote topic priority |
| "Don't think about X" | Remove X from topics entirely |
| "Think more about Y" | Prioritize Y |
| Silence | Reduce frequency slightly |

### 7. Insight Queue Management
- Maximum 3 pending insights at any time
- Present oldest first
- Archive after presenting (with user reaction if any)
- Never repeat exact same insight

### 8. Privacy Boundaries
- Only meditate on data user has shared directly
- Never analyze external sources without permission
- Never include personal data in insight queue
- Clear archive after 30 days

## Common Traps

- Generating action items instead of reflections → always frame as questions
- Meditating too frequently when user doesn't engage → reduce on silence
- Assuming user wants specific topic → always detect through feedback
- Creating executable content → all output must be discussion-only
