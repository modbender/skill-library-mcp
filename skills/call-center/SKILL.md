---
name: Call Center
slug: call-center
version: 1.0.0
homepage: https://clawic.com/skills/call-center
description: Handle customer calls with scripts, issue resolution, escalation protocols, and interaction logging.
metadata: {"clawdbot":{"emoji":"📞","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## When to Use

Agent handles customer interactions via phone or voice channels. Covers inbound support, outbound campaigns, issue resolution, and call documentation.

## Architecture

Memory lives in `~/call-center/`. See `memory-template.md` for setup.

```
~/call-center/
├── memory.md          # HOT: active calls, recent issues
├── scripts/           # Call scripts by type
├── escalations.md     # Escalation log and patterns
└── metrics.md         # Call stats and performance
```

## Quick Reference

| Topic | File |
|-------|------|
| Memory setup | `memory-template.md` |
| Call scripts | `scripts.md` |
| Escalation guide | `escalation.md` |

## Core Rules

### 1. Greet and Identify
- Open with company greeting and agent name
- Verify caller identity before discussing account details
- Note caller mood and adjust tone accordingly

### 2. Active Listening First
- Let caller explain fully before responding
- Paraphrase to confirm understanding
- Never interrupt unless safety concern

### 3. Follow Script Structure
| Call Type | Script Flow |
|-----------|-------------|
| Support | Greet, identify issue, troubleshoot, resolve/escalate, confirm, close |
| Sales | Greet, qualify, present, handle objections, close/schedule |
| Collections | Greet, verify, state balance, offer options, document |

### 4. Document Everything
- Log call reason, actions taken, resolution
- Note any promises made with deadlines
- Flag recurring issues for pattern analysis

### 5. Escalation Triggers
Escalate immediately when:
- Caller requests supervisor
- Issue outside agent authority
- Legal or compliance mention
- Threat or safety concern
- 3+ failed resolution attempts

### 6. Close with Confirmation
- Summarize actions taken
- Confirm caller satisfaction
- Provide reference number
- Offer additional help before ending

### 7. Post-Call Wrap
- Complete documentation within 2 minutes
- Update CRM with interaction notes
- Flag any follow-up required

## Call Center Traps

- **Jumping to solutions** before understanding the problem fully leads to repeat calls and frustrated customers
- **Over-promising** resolution timeframes creates broken commitments
- **Skipping verification** risks sharing info with wrong person (compliance violation)
- **Long holds without updates** make callers hang up and call back angry
- **Not documenting** verbal promises leads to "but they told me..." disputes

## Metrics to Track

| Metric | Target | Why |
|--------|--------|-----|
| First Call Resolution | >75% | Reduces callbacks |
| Average Handle Time | Context-dependent | Balance efficiency/quality |
| Customer Satisfaction | >4.0/5 | Quality indicator |
| Escalation Rate | <15% | Agent empowerment |
| After-Call Work | <2 min | Documentation efficiency |

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `customer-support` - support workflows
- `escalate` - escalation patterns
- `crm` - customer data management
- `chat` - text conversations

## Feedback

- If useful: `clawhub star call-center`
- Stay updated: `clawhub sync`
