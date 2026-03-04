---
name: langfuse-continuous-optimizer
description: Continuous LangFuse-driven optimization loop for OpenClaw/OpenRouter model routing and prompt usage controls with persistent local memory. Use when Codex needs to ingest LangFuse observations and evaluator scores, generate task-level routing policy JSON, and run scheduled safe promotion cycles that tune cost-quality-latency tradeoffs automatically.
metadata: {"openclaw":{"emoji":"🧠","requires":{"env":["LANGFUSE_PUBLIC_KEY","LANGFUSE_SECRET_KEY"],"anyBins":["python","python3"]},"primaryEnv":"LANGFUSE_SECRET_KEY"}}
---

# Langfuse Continuous Optimizer

## Overview

Run an automated observe -> evaluate -> adapt loop backed by LangFuse data.

This skill is independent and self-contained: it includes both policy builder and continuous optimizer scripts.

## Quick Start

```bash
# Single optimization cycle (LangFuse API -> staged policy -> promoted live policy if gate passes)
python scripts/langfuse_openclaw_optimizer.py run-once \
  --langfuse-host https://us.cloud.langfuse.com \
  --window-hours 24 \
  --out-dir ~/.openclaw/optimizer \
  --live-policy-path ~/.openclaw/llm_routing_policy.json \
  --promote-live-policy \
  --write-memory \
  --save-config

# Continuous daemon
python scripts/langfuse_openclaw_optimizer.py daemon \
  --interval-min 30 \
  --save-config

# Toggle settings later (persisted)
python scripts/langfuse_openclaw_optimizer.py configure --disable-promote-live-policy --show
python scripts/langfuse_openclaw_optimizer.py configure --promote-live-policy --write-memory --show
```

Credentials:

- `LANGFUSE_PUBLIC_KEY`
- `LANGFUSE_SECRET_KEY`

## Workflow

1. Pull LangFuse observations and scores from the configured time window.
2. Normalize telemetry and build staged routing policy artifacts.
3. Compare staged policy against current live policy with switch guardrails.
4. Promote only when gain and quality constraints are met and promotion is explicitly enabled.
5. Persist cycle memory to reduce policy churn and enable rollback reasoning.

## Safety

- Network egress: calls LangFuse Public API.
- Local writes: writes raw snapshots, staged artifacts, and optional memory state under `--out-dir`.
- Live policy overwrite is opt-in via `--promote-live-policy`.
- Without `--promote-live-policy`, cycles are non-destructive (stage/evaluate only).
- Save persisted defaults with `--save-config`; edit/toggle with `configure`.

## Runtime Integration

Use the generated live policy in OpenClaw/LLM runtime via:

```bash
--llm-routing-policy-file ~/.openclaw/llm_routing_policy.json
--llm-policy-reload-sec 300
```

Tag requests with stable task keys (`planning`, `tool-selection`, `retrieval`, `summarization`, `generation`, etc.) so per-task routing converges quickly.

## Resources (optional)

### scripts/

- `scripts/langfuse_openclaw_optimizer.py`: API pull + cycle orchestration + promotion gating + persistent memory.
- `scripts/closed_loop_prompt_ops.py`: normalization and policy generation engine used by the optimizer.

### references/

- `references/data-contracts.md`: input/output schemas and artifacts.
- `references/closed-loop-playbook.md`: guardrails, mutation policy, memory strategy, runtime integration notes.
