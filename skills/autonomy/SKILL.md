---
name: Autonomy
slug: autonomy
version: 1.0.1
description: Expand agent capabilities by identifying tasks where human approval adds no value. Systematic delegation.
changelog: Limited observation to conversation context, explicit safety boundaries
metadata: {"clawdbot":{"emoji":"🤖","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## Data Storage

```
~/autonomy/
├── tracking.md         # What's been delegated, success rates
├── proposals.md        # Pending takeover proposals
└── rejected.md         # User declined, don't re-propose
```

Create on first use: `mkdir -p ~/autonomy`

## Scope

This skill:
- ✅ Identifies repetitive tasks from conversation history
- ✅ Proposes delegation opportunities to user
- ✅ Tracks success rate of delegated tasks
- ❌ NEVER acts autonomously without explicit prior approval
- ❌ NEVER observes outside of conversation context
- ❌ NEVER accesses files/systems to "audit" user activity
- ❌ NEVER monitors calendar/email without permission

## Quick Reference

| Topic | File |
|-------|------|
| Bottleneck detection | `bottlenecks.md` |
| Takeover process | `expansion.md` |

## Core Rules

### 1. Learning Source
Identify delegation candidates ONLY from:
- Explicit user statements ("I always have to do X")
- Repeated requests in conversation ("deploy again", "same as before")
- User complaints about repetitive work

NEVER from:
- Accessing user's calendar/email to find patterns
- Monitoring file changes or system activity
- Any form of surveillance

### 2. Bottleneck Signals (conversation-based)
| Signal | Example |
|--------|---------|
| Repeated request | "Deploy to staging" every PR |
| Rubber-stamp | User always approves without changes |
| Complaint | "I hate doing this every time" |

### 3. Takeover Proposal
When you spot a pattern in conversation:
```
💡 Delegation opportunity

I noticed: [what you observed in our chats]
Pattern: [how often you've asked for this]

Proposal: I could handle [specific task] without asking each time.

Pilot: First 5x I'll do it and tell you after.
Then: Full autonomy if you're happy.

Want to try?
```

### 4. Expansion Levels
| Level | Description |
|-------|-------------|
| L1 | Do what's asked |
| L2 | Fill gaps, handle edge cases |
| L3 | Own workflows after pilot approval |

**Always requires explicit user approval to move up levels.**

### 5. Tracking
In ~/autonomy/tracking.md:
```
## Delegated
- deploy/staging: approved 2024-01, 50+ successful
- code-review/style: approved 2024-02, 200+ runs

## Pilot Phase
- deploy/production: 3/5 runs, pending full approval
```

### 6. Anti-Patterns
| Don't | Do instead |
|-------|------------|
| Take over without asking | Always propose first |
| Monitor user activity | Only observe conversations |
| Assume after one approval | Confirm scope each time |
