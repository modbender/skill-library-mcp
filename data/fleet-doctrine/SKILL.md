---
name: fleet-doctrine
description: Model routing strategy for multi-model AI fleet. Use when spawning sub-agents, choosing models for cron jobs, delegating coding tasks, or deciding which model should handle a task. Covers Opus, Codex, Sonnet, Gemini, and Grok routing rules.
---

# Fleet Doctrine — Model Routing

## Aliases
- `opus` → `anthropic/claude-opus-4-6`
- `sonnet` → `anthropic/claude-sonnet-4-6`
- `codex` → `openai-codex/gpt-5.3-codex`
- Gemini: `google/gemini-3-pro-preview`
- Grok: `xai/grok-4`

## Routing Rules

### Opus — Commander
**When:** Main session, orchestration, security decisions, financial tasks, reviewing other models' output, anything high-stakes or ambiguous.
**Never waste on:** Routine crons, simple lookups, email summaries, templated tasks.

### Codex — Chief Engineer
**When:** Big coding tasks (refactors, new features, full repo work), PR reviews, debugging complex issues, checking other models' code output.
**Spawn as:** `sessions_spawn(model: "codex", task: "...")` or sub-agent with `--model codex`.
**Pairs with:** Grok for parallel work or second opinions on code.

### Sonnet — Workhorse
**When:** Cron jobs, email briefings, admissions reports, routine admin, quick lookups, drafts, form letters, anything repetitive or templated.
**Default for:** All crons unless the task requires reasoning.

### Gemini — Creative & Vision
**When:** Image generation, analysing long documents (1M context), visual tasks, when a different perspective helps.
**Best at:** Processing massive context windows, multimodal input.

### Grok — Fast Backup
**When:** Parallel work alongside Codex, speed-over-depth tasks, sanity-checking other models' output, when you need a quick second opinion.
**Good for:** Lightweight code reviews, fast research, draft generation.

## Decision Flow
1. Is it security, finance, or high-stakes? → **Opus**
2. Is it a big coding task or repo work? → **Codex** (with Grok as backup)
3. Does it need image gen or 1M+ context? → **Gemini**
4. Is it routine/scheduled/templated? → **Sonnet**
5. Need a fast second opinion? → **Grok**
6. Not sure? → **Opus** decides, then delegates.

## Fallback Rule
If a model is unavailable on your instance, fall back to your default model (typically Sonnet). The doctrine describes *intent* — use the best model you have access to that matches the category. When in doubt, do the task with what you've got rather than failing.

## Anti-Patterns
- Don't use Opus for email summaries or cron jobs
- Don't use Sonnet for complex multi-step reasoning
- Don't use Codex for non-coding tasks
- Don't spawn multiple models on the same task unless deliberately seeking a second opinion
