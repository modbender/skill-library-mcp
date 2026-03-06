---
name: strategy-translator
description: >
  Translate trading strategies between different frameworks and languages.
  Use when converting Pine Script to Python, porting strategies to NautilusTrader, or cross-platform migration.
version: "1.0.0"
allowed-tools: Read, Write, Edit
---

# Strategy Translator

Source: https://mcpmarket.com/tools/skills/strategy-translator

## Use When

- You need to apply this capability as part of trading research workflows (data, features, backtests, ML, reporting).
- You want a reproducible output that can be committed to this repo (code, configs, docs).

## Inputs To Ask For

- Objective: what success looks like (metric, constraints, time horizon).
- Data: symbols, timeframe, sampling, data sources, and leakage risks.
- Constraints: compute budget, latency, interpretability, and deployment requirements.

## Outputs

- A concrete plan (steps + checks).
- A minimal implementation sketch (files to create/change) and verification steps.
- If applicable: a risk checklist (leakage, overfitting, evaluation pitfalls).

## Workflow

1. Restate the task in measurable terms.
2. Enumerate required artifacts (datasets, features, configs, scripts, reports).
3. Propose a default approach and 1-2 alternatives.
4. Add validation gates (walk-forward, Monte Carlo, sanity checks).
5. Produce repo-ready deliverables (code + docs) and a run command.
