---
name: model-router-premium
version: 0.1.1
description: Route model requests based on configured models, costs and task complexity. Use for routing general/low-complexity requests to the cheapest available model and for higher-complexity requests to stronger models.
---

# model-router

This skill provides a compact, runnable router that inspects an OpenClaw-style configuration (or a simple models JSON) and selects an appropriate model for an incoming request based on:

- declared model capabilities and an optional cost score
- task complexity (heuristic: short/simple vs long/complex)
- explicit overrides (user or caller hints)

Design principles
- Keep decision logic small and deterministic.
- Default to the cheapest model for general, not-complex tasks.
- Escalate to stronger models when the task appears complex or asks for high-fidelity results.
- Make model metadata explicit (capabilities, cost_score, tags) so the router is transparent and auditable.

What this skill includes
- scripts/router.py — a small CLI and library to pick a model given a task description and a models configuration file.
- examples/models.json — example model configurations (name, provider, cost_score, capabilities).

When to use
- Trigger when you need to programmatically choose which LLM to call for a user request.
- Use for batching or middleware routing in server apps.

Usage (quick)
- Prepare a models file (JSON) with model entries. See examples/models.json.
- Call: python3 scripts/router.py --models examples/models.json --task "Summarize this email" --mode auto
- The script prints the chosen model and the reasoning.

Files
- scripts/router.py — router CLI/library
- examples/models.json — sample model list


