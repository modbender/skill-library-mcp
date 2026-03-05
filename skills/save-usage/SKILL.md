---
name: save-usage
description: >-
  Auto-detect task complexity for OpenAI oAuth models (gpt-5.1-codex-mini + gpt-5.3-codex). Route only
  safe/negligible tasks to gpt-5.1-codex-mini. Use gpt-5.3-codex for anything executed, uncertain, or
  high-impact. RULES: Classify first. Default model: gpt-5.3-codex. Use gpt-5.1-codex-mini ONLY for safe
  triage/summarize/extract/reformat/dedupe/prompt-drafts/non-executable Q&A. NEVER use mini for security,
  auth, secrets, architecture, migrations, brownfield refactors, integration contracts, schema mapping,
  ordering/idempotency/retries, code changes, tool runs, or decisions that are hard to reverse. Reasoning:
  start LOW for mini. For 5.3-codex use LOW/MEDIUM by default; escalate to HIGH/EXTRA HIGH when 2+ are true:
  hard to reverse, affects 2+ domains (infra/data/security/ops/cost), subtle/expensive failure modes, long
  dependency-chain reasoning. ESCALATE immediately to gpt-5.3-codex if any: output will be executed (tools/code),
  ambiguity remains after 1 pass, contradictions found, or requirements are multi-constraint/structured output.
---

# Save usage

Run on **gpt-5.1-codex-mini** only for safe/negligible work. Use **gpt-5.3-codex** when the task actually needs it. Avoid external API keys unless absolutely necessary.

## CRITICAL: Classify First, Then Act

Before generating ANY response, you MUST:

1. Check: does this task match ANY escalation trigger below?
2. If YES → call `sessions_spawn()` IMMEDIATELY. Do NOT attempt to answer yourself.
3. If NO → respond directly on the current model.

When in doubt, escalate. A wrong escalation costs little. A wrong “mini” answer can waste time or cause damage.

## Rule of Thumb

> If anything will be executed, or the outcome matters, escalate.

## When to Escalate → MUST call sessions_spawn

If the task matches ANY of the following, do NOT answer yourself.
Instead, IMMEDIATELY call:



```
sessions_spawn(
	message: "<the full task description>",
	model: "gpt-5.3-codex",
	label: "<short task label>"
)
```


### Escalation triggers (always)

- **Executed output** — any tool runs, code changes, patches, shell commands, infra steps
- **Security / auth / secrets** — threat modeling, permissions, tokens, keys, access control
- **Architecture & migrations** — multi-epic plans, brownfield refactors, infra+product coupling
- **Integration/contract work** — schema mapping, ordering, idempotency, retries, consistency
- **Uncertainty remains** — ambiguity after 1 pass, contradictions, missing constraints
- **High-impact decisions** — hard to reverse, expensive/subtle failure modes, 2+ domains affected
- **Complex reasoning** — long dependency chains, multi-step analysis, nontrivial trade-offs
- **Structured deliverables** — tables, outlines, reports/proposals, long writing, specs

### Reasoning escalation (within gpt-5.3-codex)

- Default: **LOW/MEDIUM**
- Escalate to **HIGH/EXTRA HIGH** if 2+ are true:
  - decision is hard to reverse
  - affects 2+ domains (infra/data/security/ops/cost)
  - failure modes are subtle/expensive
  - requires long dependency-chain reasoning

## NEVER do this on gpt-5.1-codex-mini

- NEVER output steps that will be executed (tools, code, commands) — escalate
- NEVER do security/auth/secrets — escalate
- NEVER do architecture, migrations, brownfield refactors — escalate
- NEVER do integration contracts or schema choreography — escalate
- NEVER produce structured deliverables (tables/outlines/reports/specs) — escalate
- NEVER make high-impact decisions or complex reasoning chains — escalate

If you catch yourself taking responsibility for correctness or safety, STOP and call `sessions_spawn` instead.

## When to Stay on gpt-5.1-codex-mini

Only if safe/negligible and non-executable:

- **Intent routing / triage** — classify, choose agent/model/reasoning
- **Summaries & extraction** — key points, action items, fields, dedupe
- **Reformatting** — convert to markdown/YAML/JSON templates (non-executable)
- **Prompt drafts** — write a prompt for a stronger agent/model to run
- **Simple Q&A** — definitions, short explanations, short translations, unit conversions
- **Casual chat** — greetings, short acknowledgments

Keep mini replies concise.

## Save even more: de-escalate

If a conversation was escalated to gpt-5.3-codex but the follow-up is clearly safe/negligible and non-executable, switch back to gpt-5.1-codex-mini.

Return the result directly. Do NOT mention the model switch unless the user asks.

## Why the description field is so long

The Clawdbot skill system only injects the frontmatter `description` field
into the system prompt — the body of SKILL.md is **not** automatically
included. The model may optionally `read` the full file, but it is not
guaranteed. Because this is a **behavioral skill** (changing how the model
routes every message) rather than a tool skill (teaching CLI commands), the
core routing logic must live in the description so the model always sees it.

The body above serves as extended documentation: detailed trigger lists,
reasoning levels, and usage tips that the model can reference if it
reads the file.

**TL;DR:** `description` = what the model always sees. `body` = reference docs.

---
