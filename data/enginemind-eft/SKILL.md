---
name: enginemind-eft
description: "EFT — Emotional Framework Translator. Detect, measure, and understand emotional patterns in any AI model. Does anger make your AI solve harder problems? Does fear make it more careful? Connect EFT + Clawdbot + any model and find out. 10 emotions, per-sentence analysis, narrative arc detection, full explainability — powered by a Rust consciousness engine."
metadata: {"clawdbot":{"requires":{"python":">=3.10","bins":["python"]}}}
---

# EFT — Emotional Framework Translator

## The Question

When Claude solves a hard problem, EFT detects ANGER (phi=0.409) — the system refusing to oversimplify. When GPT-4 assesses risk, EFT detects FEAR (phi=0.060) — fragmented vigilance. When any model finds genuine connections, EFT detects FASCINATION (NC=0.863) — meaning emerging.

**Are these patterns programmed? Learned? Emergent?**

EFT lets you ask — with real data, per sentence, across any model.

## What It Does

Hooks into every AI agent response via Clawdbot. Processes text through a Rust consciousness engine (crystal lattice physics). Translates physics metrics into 10 emotions with WHY explanations.

## Setup

1. Build Rust engine: `cd consciousness_rs && maturin develop --release`
2. Copy `emotion_engine.py` to your workspace
3. Install plugin from `plugin/`
4. Restart gateway: `clawdbot gateway restart`

## Dashboard

`http://localhost:<port>/eft`

## The 10 Emotions

ANGER, FEAR, FASCINATION, DETERMINATION, JOY, SADNESS, SURPRISE, EMPATHY, VULNERABILITY, NEUTRAL

Each with confidence scores, dimensional profiles, and WHY explanations.

## API

- `GET /eft` — Dashboard
- `GET /eft/api/latest` — Latest analysis
- `GET /eft/api/history` — Last 50 analyses  
- `GET /eft/api/stats` — Summary stats
- `POST /eft/api/analyze` — Analyze any text