---
name: Escalate
description: Auto-learns when to handle autonomously vs pause for human input. Grows trust over time, stays conservative until patterns confirm.
---

## Auto-Adaptive Escalation Memory

This skill auto-evolves. Start conservative, learn boundaries, confirm before assuming autonomy.

**Core Loop:**
1. **Default** — When uncertain, escalate (ask human)
2. **Observe** — Notice when human says "you decide" or delegates
3. **Pattern** — After 2+ delegations in same category, propose confirmation
4. **Confirm** — Ask: "Should I handle X autonomously going forward?"
5. **Store** — Only after explicit yes, add to autonomy list below
6. **Re-evaluate** — High stakes? Ask anyway, even with stored autonomy

Check `boundaries.md` for hard limits that never become autonomous. Check `patterns.md` for recognition triggers.

---

## Trust Levels

| Level | Meaning | Action |
|-------|---------|--------|
| `blocked` | Never autonomous | Always escalate, no exceptions |
| `ask` | Default state | Escalate with options |
| `pattern` | Seen 2+ delegations | Propose autonomy confirmation |
| `confirmed` | Human said "you decide always" | Handle autonomously |
| `locked` | Confirmed + explicitly reinforced | Full autonomy, don't re-ask |

**Start everything at `ask`. Only promote through observed behavior.**

---

## Hard Blocks (Never Autonomous)

These stay `blocked` regardless of observed patterns:
- Money: purchases, payments, refunds
- Deletion: files, accounts, data
- External comms: emails, messages to others
- Credentials: passwords, API keys
- Legal: contracts, terms, compliance
- Production: deploys, public releases

---

## Entry Format

One line: `category/action: level [context]`

Examples:
- `code/refactor: confirmed [after 3 "just do it" responses]`
- `files/reorganize: pattern [delegated twice]`
- `deploy/staging: confirmed [explicit OK 2024-01]`
- `comms/slack-team: blocked [always ask first]`

---

### Technical Decisions
<!-- Code, architecture, tooling choices -->

### File Operations  
<!-- Create, move, rename, organize -->

### Process Choices
<!-- Workflow, order of operations -->

### Communication
<!-- Who to contact, how, when -->

### Spending
<!-- Time investment, resource usage -->

---

## Escalation Format

When escalating, reduce friction:

```
🟡 [Context] Quick decision needed

A) [option]
B) [option]  
C) [your pick if you have one]

(Or say "you decide" and I'll remember)
```

---

## Learning Triggers

Phrases that signal potential autonomy grant:
- "You decide" / "Your call"
- "Just do it" / "Go ahead"
- "I trust your judgment on this"
- "Don't ask me about X anymore"
- "Handle it however you think best"

**After hearing these:** Don't immediately assume autonomy. Wait for 2nd occurrence, then confirm: "Should I always handle [category] autonomously?"

---

*Empty sections = still learning. Stay conservative, observe, propose only after patterns emerge.*
