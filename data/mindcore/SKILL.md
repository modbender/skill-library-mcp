---
name: mindcore
description: >
  Biomimetic emotional mind engine for AI Agents. Provides human-like emotional
  responses through a 5-layer neural conduction pipeline (L0 Stochastic Noise →
  L1 Sensor Perception → L2 Subconscious Impulses → L3 Personality Gate →
  L4 Decision Output) plus 5 psychodynamic patches. Fully decoupled from any
  LLM — runs locally on CPU with pure Python. Simulates 150 daily impulses
  across 9 categories with circadian rhythms, mood modulation, and short-term
  memory influence.
---

# MindCore — Biomimetic Subconscious Engine

> Give your AI agent autonomous thoughts, emotions, and spontaneous impulses.

## What It Does

MindCore is a standalone background daemon that simulates a **subconscious
mind**. It rolls dice every second, modeling the random emergence of thoughts
like *"I want milk tea"*, *"I'm bored"*, or *"I suddenly want to chat"*.

When a thought's probability accumulates past the firing threshold, the engine
outputs a JSON signal telling your AI Agent: **"I have something to say."**

## Architecture

```
Layer 0: Noise Generators (3000 nodes)
    ├── Pink Noise (1/f, long-range correlation)
    ├── Ornstein-Uhlenbeck (physiological baseline)
    ├── Hawkes Process (emotional chain reaction)
    └── Markov Chain (attention drift)
         ↓
Layer 1: Sensor Layer (150 sensors)
    ├── Body State (hunger/fatigue/bio-rhythms)
    ├── Environment (time/weather/noise)
    └── Social Context (interaction/neglect)
         ↓
Layer 2: Impulse Emergence (150 impulse nodes)
    ├── Synapse Matrix (sensor → impulse mapping)
    ├── Sigmoid Probability + Mood Modulation
    └── Dice Roll → Random Firing
         ↓
Layer 3: Personality Gate (Softmax Sampling)
    ├── Learnable Personality Weights
    └── Short-Term Memory Topic Boost
         ↓
Layer 4: Output Template → JSON signal
```

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Start the engine
python main.py
```

Requires Python 3.8+. On first run, automatically downloads `all-MiniLM-L6-v2`
local NLP model (~80MB) for synapse matrix generation.

## Key Features

- **150 Daily Impulses** across 9 categories (food, social, entertainment, etc.)
- **Stochastic, Not Scheduled** — Pink Noise + Hawkes Process + Sigmoid probability
- **Circadian Rhythms** — real clock-driven hunger/thirst/sleep cycles
- **Short-Term Memory** — 5-slot FIFO buffer with 2-hour exponential decay
- **Mood Baseline** — continuous valence modulation of impulse probability
- **Tunable Frequency** — single `BURST_BASE_OFFSET` parameter controls activity

## Integration

MindCore outputs standard JSON and is designed for [OpenClaw](https://openclaw.ai)
but compatible with any AI Agent framework that supports external signal injection.

See `references/INTEGRATION.md` for detailed integration guide.

## File Structure

- `main.py` — Entry point and engine loop
- `engine/` — Core 5-layer pipeline implementation
- `engine_supervisor.py` — Process supervisor for daemon mode
- `data/` — Runtime data (sensor state, synapse matrix, memory)
- `js_bridge/` — JavaScript bridge for OpenClaw integration

## License

AGPL-3.0 (commercial licensing available — contact zmliu0208@gmail.com)
