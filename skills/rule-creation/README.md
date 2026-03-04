# rule-creation

> Auto-triggers Context Engineering compliance and Lobster evaluation when creating rules, policies, or behavioral constraints.

## What is Context Engineering?

**Context Engineering** is the practice of systematically wiring rules, constraints, and behaviors into your AI's context so they're reliably followed — not just "hoped for" via prompting.

The term was introduced by [Muratcan Koylan (@koylanai)](https://x.com/koylanai/status/2025286163641118915) in his work on building reliable AI systems.

**The core principle:** When you identify a rule your AI should follow, wire it immediately into the appropriate context file (TOOLS.md, AGENTS.md, etc.). Don't ask permission. Don't defer. Wire first, report after.

This skill automates that process.

## What It Does

When you (or your AI assistant) propose a new rule, this skill:

1. **Evaluates enforcement need** — applies CR-012 criteria to decide if a Lobster workflow is warranted
2. **Creates enforcement** — generates a Lobster workflow if the rule is high-stakes, multi-step, or shows a violation pattern
3. **Wires to docs** — appends the rule to the appropriate governance file (TOOLS.md, SOUL.md, etc.) immediately
4. **Reports** — outputs exactly what was done, where it was wired, and whether enforcement was created

No permission-seeking. No "want me to add this?" — it just does it.

## Context Engineering Auto-Trigger

This skill implements the **Context Engineering Auto-Trigger** principle:

> "The act of proposing a rule IS the trigger to wire it."

Rules are wired **before** the response is sent. The response confirms what was done. No permission-seeking. No "should I add this?" — it just wires the rule and tells you what it did.

## CR-012 Enforcement Criteria

A rule gets a Lobster workflow if ANY of the following match:

| Criterion | Examples |
|-----------|----------|
| High-stakes | Sends messages, spends money, deletes data, publishes content |
| Pattern of violations | "Again", "despite", "already told you" language |
| Multi-step sequence | Requires ordered steps (do A, then B, then C) |
| External/public action | Affects things outside local files |

## Installation

```bash
clawhub install rule-creation
```

Or clone directly:

```bash
git clone https://github.com/andrarchy/rule-creation.git ~/clawd/skills/rule-creation
```

## Usage

The skill auto-triggers from `SKILL.md` when the AI recognizes rule-creation intent. You can also run the workflow directly:

```bash
node ~/clawd/skills/rule-creation/scripts/evaluate-enforcement-need.js
# env: RULE_NAME="no-bare-spawns" RULE_DESCRIPTION="Never spawn a subagent without a receipt message"
```

Or run the full pipeline:

```bash
# Evaluate enforcement need
RULE_NAME="no-bare-spawns" \
RULE_DESCRIPTION="Never spawn a subagent without including Why/You'll get/ETA in the same message" \
node ~/clawd/skills/rule-creation/scripts/evaluate-enforcement-need.js

# Wire to docs
RULE_NAME="no-bare-spawns" \
RULE_DESCRIPTION="Never spawn a subagent without including Why/You'll get/ETA in the same message" \
RULE_TYPE="HARD" \
HAS_LOBSTER="false" \
node ~/clawd/skills/rule-creation/scripts/wire-rule-to-docs.js
```

## File Structure

```
rule-creation/
├── SKILL.md                              # AI skill instructions (auto-triggers)
├── README.md                             # This file
├── package.json                          # ClawHub metadata
├── workflows/
│   └── create-rule.lobster               # Full end-to-end pipeline
├── scripts/
│   ├── evaluate-enforcement-need.js      # CR-012 criteria evaluator
│   ├── create-lobster-workflow.js        # Lobster workflow generator
│   ├── wire-rule-to-docs.js              # Governance doc appender
│   └── report-rule-creation.js          # User-facing summary generator
└── templates/
    ├── lobster-workflow.template.lobster  # Template for enforcement workflows
    └── tools-md-entry.template.md        # Template for TOOLS.md entries
```

## Author

[andrarchy](https://github.com/andrarchy) — built for jarvOS / OpenClaw

## Tags

`governance` `lobster` `rules` `enforcement` `context-engineering` `jarvis` `openclaw`

## License

MIT
