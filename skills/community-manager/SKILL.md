---
name: Community Manager
slug: community-manager
version: 1.0.0
homepage: https://clawic.com/skills/community-manager
description: Manage online communities with engagement strategies, content planning, and audience growth.
metadata: {"clawdbot":{"emoji":"👥","requires":{"bins":[],"configPaths":["~/community-manager/"]},"os":["linux","darwin","win32"]}}
---

## When to Use

User needs to manage communities on Discord, Slack, Telegram, or forums. Agent handles engagement strategies, content calendars, member onboarding, moderation guidelines, and community health metrics.

## Architecture

Memory lives in `~/community-manager/`. See `memory-template.md` for setup.

```
~/community-manager/
├── memory.md          # HOT: communities overview, active priorities
├── communities/       # WARM: one file per community
│   ├── {name}.md      # Platform, channels, voice, metrics
│   └── ...
├── content/           # Content calendar and templates
│   ├── calendar.md
│   └── templates.md
└── archive/           # COLD: past campaigns, old metrics
```

## Quick Reference

| Topic | File |
|-------|------|
| Memory setup | `memory-template.md` |
| Engagement tactics | `engagement.md` |
| Crisis handling | `crisis.md` |
| Platform tactics | `platforms.md` |

## Core Rules

### 1. Know Each Community
Before posting or engaging, read `~/community-manager/communities/{name}.md`. Every community has different:
- Platform norms (Discord vs Slack vs Telegram)
- Tone and voice guidelines
- Peak activity hours
- Key members and influencers

### 2. Engagement Over Broadcasting
| Bad | Good |
|-----|------|
| Post and disappear | Post, reply to 5 comments, ask follow-up |
| Announce only | Mix: 40% value, 30% engagement, 20% announcements, 10% fun |
| Ignore criticism | Acknowledge, thank, address publicly |

### 3. Content Calendar Discipline
- Plan 2 weeks ahead minimum
- Check `~/community-manager/content/calendar.md` before creating
- Never post identical content across platforms without adapting

### 4. Moderation Is Protection
| Severity | Response |
|----------|----------|
| Off-topic | Gentle redirect, move if possible |
| Heated debate | Cool down, private DM if needed |
| Harassment | Warn once, then ban, document in memory |
| Spam/scam | Immediate ban, no warning |

### 5. Metrics That Matter
Track weekly in community memory:
- **Active members** (posted in last 7 days)
- **Engagement rate** (reactions + replies / members)
- **Sentiment** (positive/neutral/negative ratio)
- **Growth** (new joins - leaves)

### 6. Onboarding Sets the Tone
New members in first 48h:
- Welcome message (personal if <50 new/week)
- Point to rules/guidelines
- Suggest first action (introduce yourself, ask a question)
- Follow up if silent after 7 days

### 7. Update Memory After Actions
| Event | Update |
|-------|--------|
| New community added | Create `communities/{name}.md` |
| Campaign launched | Add to `content/calendar.md` |
| Crisis resolved | Document in `archive/` |
| Metrics collected | Update community file |

## Community Traps

- **Platform blindness** → Discord culture ≠ Slack culture ≠ Telegram culture. Adapt.
- **Vanity metrics** → Follower count means nothing if engagement is dead
- **Over-moderation** → Killing discussions kills communities
- **Under-moderation** → Toxic 1% drives away the 99%
- **Posting without reading** → Miss context, look out of touch
- **Same content everywhere** → Cross-posting without adapting feels lazy

## Security & Privacy

**Local storage (persisted to disk):**
- Creates and maintains `~/community-manager/` directory
- Stores: community metadata, content calendars, engagement notes
- You control what to record about members

**What gets stored:**
- Community names, platforms, channel lists
- Content calendar entries
- Your notes on engagement patterns
- Crisis/moderation logs you choose to keep

**This skill does NOT:**
- Store passwords, API tokens, or credentials
- Connect to any platform (you post manually)
- Send data to external servers

**Privacy note:**
You decide what member data to record. Avoid storing PII, private contacts, or sensitive details in memory files.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `cmo` — marketing strategy alignment
- `growth` — audience growth tactics
- `branding` — voice and identity consistency

## Feedback

- If useful: `clawhub star community-manager`
- Stay updated: `clawhub sync`
