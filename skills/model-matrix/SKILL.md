---
name: model-matrix
version: 1.0.0
description: Weighted model-routing matrix for OpenClaw (cost-aware, policy-aware, daily scorecard template).
---

# Model Matrix Skill

Use this skill to choose the best model per category using a blended score and policy constraints.

## Core Policy
1. Use the cheapest model that preserves quality.
2. If Anthropic is excluded, auto-promote #2.
3. Only swap model routes when score delta is material and confidence is high.

## Weights
- Real task evals: 45%
- Benchmarks: 30%
- Sentiment (X/Reddit): 20%
- Cost: 5%

## Effective Routing (Current)
- Research / Planning: Gemini 3.1 Pro
- Complex Coding / Complex Tasks / Enterprise Discussion: GPT-5.3 Codex
- Routine Coding + Repeat Cron Ops: GPT-5-mini
- Citizen Sentiment (X): Grok (x_search)
- Photo/Image: Gemini image stack
- Video intelligence trends: Grok ecosystem

## Daily Scorecard Template
| Category | Real Eval (45) | Bench (30) | Sentiment (20) | Cost (5) | Raw Score (/100) | Raw #1 | Effective #1 | Confidence |
|---|---:|---:|---:|---:|---:|---|---|---:|
| Research |  |  |  |  |  |  |  |  |
| Planning |  |  |  |  |  |  |  |  |
| Coding (complex) |  |  |  |  |  |  |  |  |
| Coding (routine) |  |  |  |  |  |  |  |  |
| Creative Writing |  |  |  |  |  |  |  |  |
| Enterprise Discussion |  |  |  |  |  |  |  |  |
| Citizen Sentiment (X) |  |  |  |  |  |  |  |  |

## Notes
- If Anthropic returns, include it in raw ranking and let policy choose effective winner.
- MiniMax remains trial-only unless quality holds over 7 days.
