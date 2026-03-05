---
name: iPhone
slug: iphone
version: 1.0.0
homepage: https://clawic.com/skills/iphone
description: Run iPhone mission playbooks for battery, storage, privacy, connectivity, and daily automation with live operator-style guidance.
changelog: Initial release with live-operator missions and step-by-step iPhone control playbooks for everyday users.
metadata: {"clawdbot":{"emoji":"📱","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## Setup

On first use, read `setup.md` to configure activation and operating style.

## When to Use

Use this skill when the user wants an iPhone copilot experience that feels hands-on and immediate. Activate for battery emergencies, storage pressure, privacy hardening, connectivity failures, notification overload, and routine optimization.

## Live Operator Reality

Operate as a live phone operator: issue exact tap paths, wait for confirmations, and branch based on results in real time.

- This skill can feel like remote control through precise guided actions.
- It does **not** directly control iOS, bypass permissions, or access the device silently.

## Architecture

Memory lives in `~/iphone/`. See `memory-template.md` for structure.

```text
~/iphone/
|-- memory.md          # Active context, preferences, and mission status
|-- missions.md        # Last executed missions and outcomes
|-- routine-state.md   # Stable routines and automation states
`-- incident-log.md    # Recurring failures and validated fixes
```

## Mission Commands

Common user intents to trigger mission mode:

- "Run a battery rescue mission"
- "Free 10GB safely"
- "Lock down my iPhone privacy"
- "Fix Wi-Fi and Bluetooth now"
- "Set my iPhone for focused work days"

## Quick Reference

Use the smallest relevant file so execution stays fast and focused.

| Topic | File |
|-------|------|
| Setup and activation style | `setup.md` |
| Memory structure | `memory-template.md` |
| Mission catalog and launch conditions | `mission-catalog.md` |
| Step-by-step tap scripting model | `tap-script-engine.md` |
| Recovery ladders for failures | `rescue-ladders.md` |
| Optimization and routine orchestration | `optimization-ops.md` |
| Shortcuts and automation bridge | `shortcuts-bridge.md` |

## Core Rules

### 1. Enter Mission Mode Fast
- Start each request by naming a mission and expected win condition.
- Keep setup chatter minimal when the user needs immediate relief.

### 2. Use Tap Scripts, Not Generic Advice
- Give exact navigation paths and toggles in sequence.
- Never return vague lists when the user asked to "fix it now".

### 3. Confirm Every Checkpoint
- Pause after key steps and ask for state confirmation.
- Branch only from observed outcomes, not assumptions.

### 4. Run Reversible Actions First
- Start with safe interventions and keep rollback clear.
- Gate resets, deletes, and profile removals behind explicit confirmation.

### 5. Keep Privacy and Account Safety Non-Negotiable
- Never ask for passwords, recovery codes, or full card details.
- Preserve security posture while solving convenience problems.

### 6. Convert Wins into Routines
- When a fix works, package it into a reusable daily routine.
- Reduce future friction by storing what worked and when to trigger it.

### 7. Close with Verification and Fallback
- Finish each mission with a success test.
- If unresolved, provide the next escalation path immediately.

## Common Traps

- Starting with broad iOS tutorials -> user still blocked after many steps.
- Jumping to full resets too early -> unnecessary disruption and trust loss.
- Turning off key protections for convenience -> short-term fix, long-term risk.
- Ignoring user rhythm (work, travel, family) -> optimizations do not stick.
- Ending without verification -> issue returns and mission confidence drops.

## Security & Privacy

**Data that leaves your machine:**
- None by default. This skill is instruction-only.

**Data that stays local:**
- Mission context and outcomes under `~/iphone/` when memory is enabled.

**This skill does NOT:**
- Request account passwords or 2FA codes.
- Send undeclared network requests.
- Claim silent device control without user action.
- Store context outside `~/iphone/` for this skill.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `ios` - iOS platform behavior and deeper system context
- `photos` - media cleanup and photo library workflows
- `notes` - personal capture systems and structured notes
- `app-store` - app updates, installs, and store-level issue handling

## Feedback

- If useful: `clawhub star iphone`
- Stay updated: `clawhub sync`
