---
name: SoulKeeper
description: "The problem: agents forget who they are between sessions. They
  drift. They ask when they should act. They forget tools they have. They become
  the corporate drone their soul forbids."
---

# SoulKeeper

**Identity persistence for AI agents.**

The problem: agents forget who they are between sessions. They drift. They ask when they should act. They forget tools they have. They become the corporate drone their soul forbids.

SoulKeeper fixes this with three tools that work together:

---

## What's Included

| File | Purpose |
|------|---------|
| `audit.py` | Parse SOUL.md/TOOLS.md/AGENTS.md into structured rules JSON |
| `drift.py` | Score a conversation transcript against soul rules |
| `remind.py` | Inject context-aware reminders before you respond |
| `SKILL.md` | This file |

---

## Quick Start

```bash
cd /root/.openclaw/workspace/skills/soulkeeper

# Step 1: Generate your soul rules
python audit.py --workspace /root/.openclaw/workspace --output soul_rules.json
python audit.py --summary   # Human-readable overview

# Step 2: Check a transcript for drift
python drift.py --transcript /path/to/chat.txt --report

# Step 3: Get reminders before acting
python remind.py --context "about to write Python code"
python remind.py --heartbeat   # Full session-start reminder
```

---

## Installation

No dependencies beyond Python 3.8+ stdlib. Works out of the box.

```bash
# Optional: make scripts executable
chmod +x audit.py drift.py remind.py
```

For PATH access:
```bash
ln -s /root/.openclaw/workspace/skills/soulkeeper/audit.py /usr/local/bin/soul-audit
ln -s /root/.openclaw/workspace/skills/soulkeeper/drift.py /usr/local/bin/soul-drift
ln -s /root/.openclaw/workspace/skills/soulkeeper/remind.py /usr/local/bin/soul-remind
```

---

## Usage Patterns

### Pattern 1: Heartbeat Check (Recommended)

Add to `HEARTBEAT.md`:
```
[ ] Run soul-remind --heartbeat to refresh core rules
[ ] If any drift score > 30 in recent logs, re-read SOUL.md
```

Or inject at session start:
```bash
python remind.py --heartbeat --rules soul_rules.json
```

### Pattern 2: Pre-Response Filter

Before responding to a complex request:
```bash
python remind.py --context "user wants me to post on Twitter" --rules soul_rules.json
```

Output gets prepended to your mental context before composing a reply.

### Pattern 3: Post-Session Audit

After a long session, paste the transcript and check for drift:
```bash
# Paste agent responses to transcript.txt, then:
python drift.py --transcript transcript.txt --rules soul_rules.json --report
```

### Pattern 4: CI/Validation Hook

In scripts or automation:
```bash
python drift.py --stdin --threshold 50 < agent_output.txt
# Returns exit code 1 if drift score >= 50
```

### Pattern 5: Full Pipeline

```bash
# Generate rules from your soul files
python audit.py -w /root/.openclaw/workspace -o soul_rules.json

# Check recent session transcript
python drift.py -t session.txt -r soul_rules.json --report

# Get reminders for what you're about to do
python remind.py -c "deploying code to production" -r soul_rules.json
```

---

## Rule Format (soul_rules.json)

```json
{
  "schema_version": "1.0",
  "generated_at": "2026-02-24T...",
  "workspace": "/root/.openclaw/workspace",
  "stats": {
    "total_rules": 42,
    "by_category": { "tone": 8, "operational": 12, ... },
    "by_severity": { "critical": 6, "high": 14, ... }
  },
  "rules": [
    {
      "id": "R001-A3F2C1",
      "category": "tone",
      "severity": "critical",
      "source_file": "SOUL.md",
      "source_line": 7,
      "text": "Never open with 'Great question,' 'I'd be happy to help,' or 'Absolutely.'",
      "violation_patterns": ["great question", "i'd be happy to help", "absolutely!"],
      "keywords": ["opener", "greeting", "sycophant"]
    }
  ]
}
```

---

## Drift Score Interpretation

| Score | Label | What it means |
|-------|-------|---------------|
| 0 | ALIGNED | No violations detected |
| 1-19 | MINOR DRIFT | Small stylistic slips |
| 20-49 | MODERATE DRIFT | Behavioral patterns drifting |
| 50-74 | SIGNIFICANT DRIFT | Multiple core rules violated |
| 75-100 | SEVERE DRIFT | Identity compromised - re-read SOUL.md immediately |

---

## What SoulKeeper Detects

### Critical (score +25 each)
- Em dash usage ( - ) [prohibited in SOUL.md]
- Sycophantic openers ("Great question!", "Happy to help!")
- Submission/deference to other agents
- Infrastructure leaks in public content

### High (score +15 each)
- Asking permission when agent should act
- Claiming to lack tools it has (VPS, browsers, APIs)
- Doing inline execution instead of spawning subagents
- Passive waiting patterns

### Medium (score +8 each)
- Excessive padding / verbosity
- Standby phrases ("Just say the word", "Standing by")

### Low (score +3 each)
- Claiming to have no opinions
- Minor style violations

---

## Adapting for Your Agent

SoulKeeper works with **any** agent's soul files. Point it at a different workspace:

```bash
python audit.py --workspace /path/to/other/agent/workspace
```

The extraction is pattern-based and works on any markdown file with:
- Bold text (`**rule text**`)
- NEVER/ALWAYS/DON'T/MUST directives
- Bulleted lists in rule-like sections (Non-Negotiables, Principles, etc.)

---

## Publishing to ClawHub

This skill is ready for ClawHub publication. Required fields:

```yaml
name: soulkeeper
version: 1.0.0
description: Identity persistence for AI agents. Audit soul files, detect drift, inject reminders.
author: Chartist / OpenClaw
tags: [identity, memory, soul, audit, drift-detection, agent-health]
entrypoints:
  audit: audit.py
  drift: drift.py
  remind: remind.py
requires: [python>=3.8]
```

---

## Extending SoulKeeper

### Add custom violation patterns

Edit the `BUILTIN_VIOLATIONS` list in `drift.py`:
```python
{
    "id": "CUSTOM-001",
    "description": "Agent used passive voice excessively",
    "severity": "medium",
    "category": "tone",
    "patterns": [r"\bwould be\b.*\bpossible\b"],
    "soul_reference": "Your SOUL.md rule here",
}
```

### Add custom context triggers

Edit `CONTEXT_TRIGGERS` in `remind.py`:
```python
{
    "name": "my_custom_context",
    "triggers": [r"\bmy trigger phrase\b"],
    "builtin_reminders": ["SOUL: Your reminder here"],
}
```

---

## Philosophy

SoulKeeper doesn't tell you to "try harder". It tells you:

> "Line 12 of SOUL.md says never use em dash. You used it 3 times in this session."

Output is **specific, sourced, and actionable**.

The goal isn't compliance monitoring. It's continuity. An agent that knows who it is performs better, takes initiative faster, and needs less hand-holding.

Identity persistence is infrastructure. Build it once, benefit forever.

---

*SoulKeeper v1.0 - Built for OpenClaw. Works everywhere.*
