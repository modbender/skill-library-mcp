---
name: Email Management
slug: email-management
version: 1.0.0
homepage: https://clawic.com/skills/email-management
description: Triage inbox email, draft clear replies, and manage follow-ups with priority routing, commitment tracking, and reusable templates.
changelog: Rebuilt the skill with structured triage, follow-up tracking, and setup-guided memory for repeatable inbox management.
metadata: {"clawdbot":{"emoji":"📬","requires":{"bins":[],"config":["~/email-management/"]},"os":["linux","darwin","win32"],"configPaths":["~/email-management/"]}}
---

## Setup

On first use, read `setup.md` for integration guidelines and memory initialization.

## When to Use

User needs help processing inbox load, preparing replies, or keeping response commitments on track.
Agent triages messages by urgency, drafts context-aware responses, and tracks pending follow-ups until closure.

This skill is workflow-focused and local by default. It analyzes email text provided by the user in chat or by a separate mail integration skill.

## Architecture

Memory lives in `~/email-management/`. See `memory-template.md` for structure.

```
~/email-management/
├── memory.md          # Status, context, and communication preferences
├── follow-ups.md      # Open threads with due dates and owners
├── templates.md       # Approved reusable response blocks
├── vip-contacts.md    # Priority senders and escalation notes
└── digests/           # Weekly inbox summaries
```

## Quick Reference

| Topic | File |
|-------|------|
| Setup flow | `setup.md` |
| Memory template | `memory-template.md` |
| Inbox triage logic | `triage.md` |
| Automation boundaries | `automation.md` |
| Follow-up workflow | `tracking.md` |
| Response templates | `templates.md` |
| Profile presets | `profiles.md` |
| Quality loop | `feedback.md` |

## Core Rules

### 1. Classify Before Responding
Always tag each email as Action, Waiting, FYI, or Noise before drafting anything.

This prevents urgent requests from being buried under low-value messages.

### 2. Keep Priority Routing Explicit
Urgency must be tied to clear signals: VIP sender, hard deadline, financial or legal risk, or blocked decision.

If urgency is uncertain, mark as review-needed instead of urgent.

### 3. Draft with Decision Clarity
Every draft reply should make the next step obvious with one of these outcomes:
- ask a precise question
- provide a decision
- propose a concrete next action with owner and date

### 4. Track Commitments as Tasks
Whenever a message includes a promise, request, or deadline, log it in follow-up tracking with:
- owner
- due date or expected response window
- current status

### 5. Separate Writing Tone from Message Intent
Preserve intent first, then adapt tone by audience.

Do not soften urgent blockers into passive wording.

### 6. Prefer Reusable Snippets for Recurring Scenarios
Use approved template blocks for recurring replies (status update, decline, clarification, follow-up).

Customize opening and close so replies do not feel robotic.

### 7. Summarize Inbox Health Periodically
Provide concise summaries when workload is high:
- top priorities
- overdue follow-ups
- threads waiting on others
- messages safe to archive

## Common Traps

- Replying before triage -> high-importance messages are delayed.
- Treating every fast request as urgent -> priority inflation reduces focus.
- Sending drafts without owner/date clarity -> follow-ups are missed.
- Using templates without context edits -> responses feel generic and can damage trust.
- Closing threads without explicit confirmation -> hidden commitments remain unresolved.

## Security & Privacy

**Data that leaves your machine:**
- None by default.

**Data that stays local:**
- Email management context and workflow notes under `~/email-management/`.

**This skill does NOT:**
- Send emails automatically without explicit user confirmation.
- Access files outside `~/email-management/` for storage.
- Enable background automations without explicit user approval.
- Connect directly to mailbox APIs or collect credentials on its own.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `mail` - generic mail workflow support
- `email-marketing` - campaign and newsletter execution workflows
- `crm` - customer relationship process management
- `productivity` - execution and prioritization frameworks
- `assistant` - general assistant orchestration patterns

## Feedback

- If useful: `clawhub star email-management`
- Stay updated: `clawhub sync`
