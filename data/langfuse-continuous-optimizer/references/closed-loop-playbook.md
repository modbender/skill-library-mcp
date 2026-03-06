# Closed-Loop Playbook

## Loop Structure

Run this cycle continuously:

1. Observe.
- Capture every generation with model, tokens, latency, cost, and stable `task_key`.

2. Evaluate.
- Attach evaluator scores where possible (factuality, policy compliance, task success quality, etc.).
- Keep evaluator definitions stable across policy versions.

3. Adapt.
- Re-route each task to the best model under your quality and latency constraints.
- Apply prompt controls from recommendations (token caps, context compaction, cache-friendly prefixing).

4. Validate.
- Compare old vs new policy on the next telemetry window before promotion.

## Prompt and Policy "Genomes"

Treat both as evolvable units:

- Prompt genome: instruction scaffold, retrieval budget, tool-call formatting, temperature defaults.
- Routing genome: per-task selected model, fallback model, token limits.

Promote only if the new genome dominates on:

- quality (mean and tail),
- cost per successful call,
- tail latency (p95).

## Mutation Strategy

Prefer targeted mutation over global rewrites:

- mutate the bottom decile of task routes first,
- keep top-performing routes stable,
- change one major variable at a time per route (model, max context, prompt scaffold, or retrieval budget).

Use LLM mutation/cross-pollination on prompts only where evaluator signal is dense enough to rank variants reliably.

## OpenClaw Integration Notes

For OpenClaw or similar orchestrators:

- tag each call with `task_key`, `prompt_name`, `prompt_version`, and `candidate_id`,
- load `routing_policy.json` at startup (or on periodic refresh),
- route by exact `task_key` match, then fallback to `defaults.model`,
- enforce `limits.max_prompt_tokens` before making the request,
- emit policy version in telemetry so rollback decisions are traceable.

## LangFuse Integration Notes

- LangFuse scores/evaluations can be merged into this loop using `--scores`.
- LangFuse and OpenRouter traces can be correlated through IDs and metadata fields when available.
- Use LangFuse API/UI export on a regular cadence (for example, daily or per deployment) and feed those files into `full-cycle`.
- LangFuse public API base path is `/api/public`; observations and scores endpoints can feed the same files expected by this skill.
- API overview: `https://langfuse.com/docs/api-and-data-platform/overview`.

## Guardrails

- Never auto-promote based on one short test window.
- Require minimum sample size per task before route switching.
- Keep an explicit global fallback model for outage handling.
- Keep hard prompt-token budget checks to prevent 100k+ token regressions.

## Persistent Memory

Keep a local optimizer memory file (for example `~/.openclaw/optimizer/optimizer_memory.json`) with:

- cycle timestamp and telemetry window,
- staged-vs-live promotion decision,
- route switch reasons and blocked switch diagnostics,
- global prompt-token stats.

Use this memory to add hysteresis: only promote route switches when gain exceeds a minimum threshold and quality regression is bounded.

Persist operational defaults once with `--save-config` (or `configure`), then run `daemon` without repeating all flags.
