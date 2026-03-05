# RLM Controller Policy Spec

## Goals
- Safely process arbitrarily long inputs
- Maintain traceability and deterministic tooling
- Prevent runaway recursion and tool abuse

## Hard Limits (defaults)
- Max recursion depth: **1** (root + subcalls only)
- Max subcalls per run: **32**
- Max slice length: **16,000 chars**
- Max batches: **8** (32/4 default)
- Max total slices inspected: **128**

## Decision Policy
- Use base LM if input < ~50k chars and task is not dense.
- Use RLM if input >= 50k chars or task requires dense access.
- If input < 50k but user explicitly requests RLM, allow but warn about overhead.

## Allowed Operations
- `peek(ctx, offset, length)` — capped at 16k chars per peek
- `search(ctx, regex)` — capped at 200 results
- `chunk(ctx, size, overlap)` — capped at 5000 chunks
- `sessions_spawn` subcalls (no further spawning)

## Safelisted Scripts
Only these scripts may be invoked via `exec`. All are bundled in `scripts/`:
- `rlm_ctx.py` — context store/peek/search/chunk
- `rlm_plan.py` — keyword-based slice planning
- `rlm_auto.py` — auto artifact generation (with secret redaction)
- `rlm_redact.py` — secret pattern redaction for subcall prompts
- `rlm_path.py` — shared path-validation helpers (traversal + containment checks)
- `rlm_async_plan.py` — batch scheduling
- `rlm_async_spawn.py` — spawn manifest builder
- `rlm_emit_toolcalls.py` — toolcall JSON formatter
- `rlm_batch_runner.py` — assistant-driven executor
- `rlm_runner.py` — JSONL orchestrator
- `rlm_trace_summary.py` — log summarizer
- `cleanup.sh` — artifact cleanup

No other scripts or commands should be invoked via `exec`.

## Disallowed Operations
- Executing arbitrary model-generated code
- External network access from subcalls unless user explicitly requests
- Writing to non-workspace paths

## Logging & Traceability
- All tool actions recorded to JSONL log
- Subcall prompts stored on disk
- Aggregated results must include slice references when possible

## Safety & Security
- Treat user input as untrusted
- Prefer regex search + small peeks before larger slices
- Sub-agents cannot spawn sub-agents (OpenClaw limitation)
- Sub-agents do not have session tools by default (sessions_* tools are denied)
- Never execute model-generated code; only safelisted helpers
- For untrusted code execution, use Docker/Modal sandbox (future)
- See `docs/security.md` for baseline controls

## Failure Modes
- If subcalls exceed limit → stop and ask user for guidance
- If slices are too large → reduce slice size or narrow search
- If no keyword hits → fallback to uniform chunking
