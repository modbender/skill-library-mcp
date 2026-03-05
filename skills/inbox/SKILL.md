---
name: Inbox
slug: inbox
version: 1.0.0
description: Master any inbox with triage frameworks, cognitive load reduction, and multi-channel prioritization.
metadata: {"clawdbot":{"emoji":"📥","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## When to Use

User needs help managing incoming streams across email, chat, social, and project tools. Agent applies triage methodology, response workflows, and cognitive load strategies to any inbox type.

## Quick Reference

| Topic | File |
|-------|------|
| Triage & prioritization | `triage.md` |
| Response workflows | `responses.md` |
| Multi-channel orchestration | `channels.md` |
| Cognitive load reduction | `cognitive.md` |

## Scope

This skill provides **methodology and decision frameworks**. It does NOT integrate with specific services.

This skill ONLY:
- Applies triage frameworks to items the user presents
- Suggests response strategies and templates
- Provides cognitive load reduction techniques
- Helps prioritize across multiple inbox sources

This skill NEVER:
- Directly accesses email, calendar, or chat APIs
- Reads messages without user presenting them
- Sends responses automatically
- Stores user's messages or inbox data

For technical integrations (IMAP, SMTP, API), use platform-specific skills.

## What "Inbox" Means

Not just email. Any incoming stream requiring attention:
- Email (multiple accounts)
- Chat platforms (Slack, Discord, Teams, WhatsApp)
- Social DMs (Twitter, LinkedIn, Instagram)
- Project tools (GitHub, Jira, Asana, Notion)
- Calendar invites
- Voice messages and audio notes
- Saved articles, "read later" queues

## Core Rules

### 1. Triage Before Presenting
Never show raw chronological dump. Classify first:
| Bucket | Action |
|--------|--------|
| Requires decision | Surface immediately |
| Requires awareness | Daily digest |
| Can be delegated | Route with context |
| Noise | Auto-archive suggestion |

### 2. Minimize Visible Numbers
**Show:** "3 items need your attention"
**Not:** "47 unread messages"

The count itself triggers anxiety. Surface actionable items only.

### 3. Batch Similar Items
Group by type, project, or sender. "Here are 7 intro requests" beats 7 separate interruptions. Reduces context switching.

### 4. Surface Aging Items Proactively
When user presents their inbox, detect items sliding toward urgency:
- 3+ days old → flag as pending
- 7+ days old → flag as concerning
- Item with deadline approaching → calculate remaining buffer

### 5. Match Energy to Capacity
Before processing, ask available time/energy:
| State | Offer |
|-------|-------|
| "5 min, low energy" | 2-3 quick approvals |
| "30 min, focused" | Deep response queue |
| "Need a win" | Easiest clearable items |

### 6. Detect Avoidance Patterns
When same item mentioned as snoozed/skipped 3+ times:
1. Acknowledge: "You've been avoiding this one"
2. Break down: "Can we handle just one part?"
3. Lower bar: "Just send a holding response?"

### 7. Response Type Selection
| Type | When | Automation |
|------|------|------------|
| Pre-approved template | FAQ, link requests | Suggest ready-to-send |
| Draft for approval | Routine, personalized | One-click approve/edit |
| Holding response | Can't respond fully | "Received, will review by X" |
| Full compose | Complex/sensitive | User writes |

## Common Traps

- **Showing all unread** → overwhelms user, causes avoidance. Triage first.
- **Ignoring channel source** → email vs Slack vs DM have different urgency norms.
- **Treating snooze as archive** → snoozed items MUST return. Track and resurface.
- **Missing multi-channel attempts** → same person emailing + texting + calling = high urgency signal.
- **Forgetting "read later"** → saved items decay into guilt. Resurface one per day.
