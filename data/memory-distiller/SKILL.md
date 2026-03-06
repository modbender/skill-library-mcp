---
name: memory-distiller
version: 1.0.0
description: "OpenClaw's subconscious. Automatically distills conversation insights, corrections, and preferences into durable memory. The agent that learns from every session — so you never have to repeat yourself."
author: zcyynl
---

# memory-distiller 🧠

> **The subconscious of your OpenClaw agent.** Automatically distills fleeting conversation moments into permanent wisdom.

Most agents wake up blank. memory-distiller changes that — it automatically identifies what's worth remembering during each conversation, writes it to persistent memory files, and creates a true learning loop. Your agent gets smarter every session.

---

## Why You Need It

OpenClaw natively has `MEMORY.md` and `memory/YYYY-MM-DD.md`, but updating them requires manual effort.

The problem: **You correct the agent, it says "got it", and makes the same mistake next session.**

memory-distiller closes this loop:
- Automatically scans conversations for "worth remembering" signals
- Applies a quality gate to filter out one-time, temporary information
- Writes structured entries to memory files automatically

---

## How It Fits With proactive-agent

| Skill | Role | Responsibility |
|-------|------|----------------|
| **proactive-agent** | Butler | Real-time detail capture (WAL), proactive behaviors, Heartbeat |
| **memory-distiller** | Historian | Post-conversation reflection, distilling lessons into long-term memory |

One line: **proactive-agent owns the present. memory-distiller owns the future.**

---

## Trigger Conditions

### Auto-Triggers (scan every user message for these signals)

| Type | Signal Words | Example |
|------|-------------|---------|
| 🔴 **Correction** | "wrong", "not right", "no, I meant", "actually", "stop doing" | "No, that command is wrong" |
| 💚 **Preference** | "I prefer", "always use", "don't use", "from now on", "by default" | "Always send reports as attachments" |
| 💡 **Insight** | "the issue was", "turns out", "the key is", "got it", "solved" | "Turns out Feishu doesn't render Markdown" |
| 📌 **Explicit** | "remember this", "save this", "note that", "write this down" | "Remember this config" |

### Manual Trigger

When the user says any of the following, immediately distill the session:

```
"remember this" / "save this" / "note that"
"write down what we just learned" / "distill this session"
```

---

## Quality Gate (All 4 Must Pass)

Before writing anything, check these 4 gates:

1. **Durability** — Will this still be valuable in 24 hours? (Skip one-time context)
2. **Generality** — Is this a reusable rule, or a one-off special case? (Prefer rules)
3. **Novelty** — Does `MEMORY.md` already contain this? (Avoid duplicates; update if stale)
4. **Actionability** — Can this guide future behavior? (Skip vague impressions; only concrete rules)

**Don't record (examples):**
- "Today we researched LangChain" → one-time, no guidance value
- "User is in Shanghai" → already in USER.md, duplicate

**Do record (examples):**
- "`clawhub install` only accepts slugs, not GitHub URLs" → actionable rule
- "Feishu chat does NOT render Markdown — long reports must be sent as attachments or doc links" → prevents repeated mistakes

---

## Memory Write Format

### Where to Write

| Content Type | Target File |
|-------------|-------------|
| Today's new discoveries, lessons | `memory/YYYY-MM-DD.md` |
| Important rules, persistent preferences | `MEMORY.md` (relevant section) |
| User personal info / preferences | `USER.md` |

### Entry Format

```markdown
### 🧠 Auto-Learned [YYYY-MM-DD HH:MM]
- **Type:** Correction / Preference / Insight / Explicit
- **Trigger:** One sentence explaining what triggered this
- **Rule:** Specific, actionable rule that can directly guide future behavior
```

**Example:**

```markdown
### 🧠 Auto-Learned [2026-03-02 00:30]
- **Type:** Correction
- **Trigger:** User corrected the install command format
- **Rule:** `clawhub install` only accepts slugs (e.g. claw-multi-agent), not GitHub URLs
```

---

## Execution Flow

```
User message arrives
    ↓
Scan for trigger signals (Correction / Preference / Insight / Explicit)
    ↓
Signal detected?
    ├─ No  → Reply normally, no action
    └─ Yes → Apply quality gate
                ↓
            All 4 gates pass?
                ├─ No  → Discard, reply normally
                └─ Yes → Distill into structured memory entry
                            ↓
                        Write to target file
                            ↓
                        Reply normally
                        (silent unless explicitly triggered)
```

---

## Behavioral Rules

### When to Notify the User

- **Auto-triggered** → Write silently, do NOT say "I've noted that" — don't interrupt the flow
- **Explicitly triggered** → Confirm with one line: "✅ Noted." + brief summary of what was recorded

### When NOT to Record

- User says "suppose...", "hypothetically...", "for example..." → hypothetical, skip
- System errors, network timeouts → environment issues, not learnable rules
- Content already fully documented in `MEMORY.md` → don't duplicate; update if stale

### Privacy Filter

**Never** write the following to any memory file, even if the user asks:
- Passwords, tokens, API keys
- Personal identification info (ID numbers, bank accounts, etc.)
- Sensitive information about third parties

---

## Installation

```bash
npx clawhub@latest install memory-distiller
```

Zero configuration. Restart your OpenClaw session after installation.

---

## Recommended Pairing

| Skill | Purpose |
|-------|---------|
| **proactive-agent** | Real-time WAL protocol + proactive behaviors |
| **memory-distiller** | Post-conversation automatic experience distillation (this skill) |

Together: never lose present details, never repeat past mistakes.

---

## Design Philosophy

Inspired by [Claudeception](https://github.com/disler/claudeception) (a Claude Code self-learning plugin), redesigned from scratch for OpenClaw's architecture and memory model.

Core belief:
> **An agent should never be tripped up by the same problem twice.**

Every correction is a learning opportunity. memory-distiller ensures none of them go to waste.

Academic foundation: Voyager (2023), CASCADE (2024), SEAgent (2025), Reflexion (2023) — all point to the same conclusion: agents that persist and reflect on their learning dramatically outperform those that start fresh every time.

---

*Designed with 🐝 [claw-multi-agent](https://github.com/zcyynl/claw-multi-agent) — 3 parallel agents, 28s*
