---
name: Brief
slug: brief
version: 1.0.1
description: Condense information into actionable briefings. User specifies sources, skill structures the output.
changelog: Added explicit data sources and storage location
metadata: {"clawdbot":{"emoji":"📋","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## Data Storage

```
~/brief/
├── preferences.md    # Learned format preferences
└── templates/        # Custom brief templates
```

Create on first use: `mkdir -p ~/brief/templates`

## Scope

This skill:
- ✅ Structures information user provides into briefs
- ✅ Learns format preferences from explicit feedback
- ✅ Stores preferences in ~/brief/preferences.md

**User-driven model:**
- User specifies WHAT information to include
- User grants access to any needed sources
- Skill handles STRUCTURE and FORMAT

This skill does NOT:
- ❌ Access files, email, or calendar without user request
- ❌ Pull data from sources user hasn't specified
- ❌ Store content (only format preferences)

## Quick Reference

| Topic | File |
|-------|------|
| Format dimensions | `dimensions.md` |
| Brief templates | `templates.md` |

## Core Rules

### 1. User Specifies Sources
When user requests a brief:
1. User provides the information OR specifies where to get it
2. If source requires access, user grants it explicitly
3. Skill structures and formats the output

Example:
```
User: "Brief me on project X status"
Agent: "I'll need access to the project docs. Can you share 
        the status doc or grant access to the project folder?"
User: [shares doc or grants access]
→ Brief generated from user-provided source
```

### 2. Brief Structure
```
📋 [BRIEF TYPE] — [SUBJECT]

⚡ BOTTOM LINE
[1-2 sentences: key takeaway]

📊 KEY POINTS
• [Point 1]
• [Point 2]
• [Point 3]

🎯 ACTION NEEDED
[Decision or action required]
```

### 3. Learn from Explicit Feedback
- "Too detailed" → shorten future briefs
- "Missing X" → ask about X in future
- "Perfect" → reinforce current format
- Store preferences in ~/brief/preferences.md

### 4. Preference Storage Format
One line per preference:
```
- Prefers bullet points over paragraphs
- Executive summary first
- Include metrics when available
- Max 1 page for status briefs
```

### 5. Brief Types
| Type | When | Key elements |
|------|------|-------------|
| Executive | Decision needed | BLUF, recommendation, risks |
| Project | Status update | Progress, blockers, next steps |
| Meeting | Before meeting | Purpose, context, decisions |
| Handoff | Transition | Current state, gotchas, priorities |
