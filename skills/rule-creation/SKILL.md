---
name: rule-creation
description: "Auto-triggers Context Engineering compliance and Lobster enforcement when proposing, creating, or formalizing rules, policies, processes, or behavioral constraints. Implements the principle: the act of stating a rule IS the trigger to wire it."
metadata:
  openclaw:
    emoji: "📜"
---

# rule-creation Skill

## Description

Auto-triggers **Context Engineering** compliance and Lobster enforcement evaluation when **proposing, creating, or formalizing new rules, policies, processes, workflows, or behavioral constraints**.

**Context Engineering** is the practice of wiring rules into your AI's context so they're reliably followed — not just hoped for via prompting. Credit: [Muratcan Koylan (@koylanai)](https://x.com/koylanai/status/2025286163641118915)

Use this skill any time you are:
- Declaring a new rule (e.g. "From now on, always X")
- Formalizing a policy (e.g. "The policy for Y is Z")
- Creating a behavioral constraint (e.g. "Never do X without doing Y first")
- Proposing a process or workflow
- Updating governance documents (TOOLS.md, CRITICAL-RULES.md, CONSTITUTION.md, etc.)

---

## When This Skill Matches

**Trigger phrases:**
- "Add this rule…"
- "Create a policy…"
- "From now on…"
- "The rule is…"
- "New constraint…"
- "Formalize that…"
- "Wire this rule…"
- "Make it a HARD rule…"
- Any governance/policy update request

---

## Mandatory Workflow

When this skill triggers, **always** execute the following steps in order. Do NOT ask permission — CE-PROCESS compliance means **wire first, report after**.

### Step 1: Identify the Rule

Extract:
- **Rule name** — short slug (e.g. `no-bare-spawns`, `external-message-gate`)
- **Rule description** — plain language statement of what the rule requires
- **Rule type** — `HARD` (non-negotiable, always enforced) or `soft` (guideline, use judgment)

### Step 2: Evaluate Enforcement Need (CR-012 Criteria)

Run `scripts/evaluate-enforcement-need.js` or apply manually:

A rule **needs Lobster enforcement** if ANY of the following are true:

| Criterion | Examples |
|-----------|----------|
| **High-stakes** | Sends external messages, spends money, deletes data, publishes public content, deploys to production |
| **Pattern of violations** | A similar rule was already stated but broken or ignored |
| **Multi-step sequence** | Requires multiple ordered steps (do A, then B, then C) |
| **External / public action** | Affects things outside the user's local files |

**Scoring:**
- 0 criteria matched → `needsEnforcement: false` (wire to TOOLS.md only)
- 1+ criteria matched → `needsEnforcement: true` (create Lobster workflow + wire)

### Step 3: Lobster Availability Preflight

Before creating any workflow, verify Lobster is actually enabled:

Run `scripts/check-lobster-available.js` **or** check manually:
```bash
openclaw plugins list | grep -i lobster
```

| Output | Meaning | Action |
|--------|---------|--------|
| `lobster … loaded` | ✅ Available | Proceed to Step 3a |
| `lobster … disabled` | ❌ Unavailable | Use fallback (below) |
| No lobster row | ❌ Not installed | Use fallback (below) |

**Fallback when Lobster is unavailable:**
- Skip workflow creation entirely
- Proceed directly to Step 4 (wire to docs) — no Lobster reference in the entry
- Report: `⚠️ Enforcement: unavailable (Lobster not enabled)`
- Include hint: `Run: openclaw plugins enable lobster` to activate

**Never claim enforcement is wired when Lobster is disabled.**

### Step 3a: Create Lobster Workflow (enforcement needed AND Lobster available)

If `needsEnforcement: true` **and** Lobster preflight passed:
1. Copy `templates/lobster-workflow.template.lobster`
2. Fill in: `name`, `description`, steps specific to rule enforcement
3. Save to `workflows/<rule-name>.lobster`
4. Note the workflow path for wiring

### Step 4: Wire to Docs

Run `scripts/wire-rule-to-docs.js` or manually append to the appropriate file:

**Routing:**
- Operational rules → `TOOLS.md`
- Identity/persona constraints → `SOUL.md` or `agents/identity.md`
- Hard system rules → `CRITICAL-RULES.md` (if exists) or `AGENTS.md`
- Project-specific rules → relevant project board or `agents/projects.md`

**Entry format** (from `templates/tools-md-entry.template.md`):
```
## <Rule Name> (<HARD|soft>)

<Rule description>

[If Lobster enforcement]: **Enforced by:** `workflows/<rule-name>.lobster`
```

### Step 5: Report What Was Done

Your response must include:

```
✅ Rule wired: <Rule Name>
📄 Location: <file where it was added>
🔒 Enforcement: <Lobster workflow path OR "TOOLS.md entry only">
📋 Type: <HARD|soft>
```

**Never say:**
- ❌ "Want me to add this to TOOLS.md?"
- ❌ "Should I wire this through CE?"
- ❌ "Is this CE compliant?"

**Always say:**
- ✅ "Added `<rule>` to `<file>`. Enforcement: `<status>`."

---

## Script Reference

| Script | Purpose |
|--------|---------|
| `scripts/check-lobster-available.js` | Preflight: verify Lobster plugin is enabled in this OpenClaw instance |
| `scripts/evaluate-enforcement-need.js` | Evaluate CR-012 criteria against rule description |
| `scripts/wire-rule-to-docs.js` | Append rule entry to TOOLS.md or specified target file |
| `scripts/report-rule-creation.js` | Generate user-facing summary of what was created |

---

## Workflow Reference

| Workflow | Purpose |
|----------|---------|
| `workflows/create-rule.lobster` | Full end-to-end rule creation pipeline |

---

## Context Engineering Auto-Trigger (HARD)

This skill embodies the Context Engineering Auto-Trigger principle:

> "When proposing any new rule, behavioral constraint, or policy change: Wire it first. Add the rule to the appropriate file BEFORE responding. Never ask permission to formalize a rule."

The act of recognizing a rule IS the trigger. Wire immediately. Report after.
