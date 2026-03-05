# 🧠 Identity Persistence Layer

Structured identity graph system for AI agents. Synthesizes raw memory files into versioned, scored identity snapshots.

## What It Does
- Extracts core beliefs, personality traits, relationships, memories, cognitive patterns, and contradictions from agent markdown files
- Computes **Continuity Score** (0-1) using KL divergence on beliefs + MSE on traits
- Versions snapshots with diffs for drift detection
- **Molting Protocol** for model upgrades — freeze, verify, score

## Requirements
- Gemini API key (for identity extraction)
- Agent workspace with MEMORY.md and/or SOUL.md files

## Usage
```bash
python3 identity_manager.py              # Full cycle: extract + score + save
python3 identity_manager.py --score-only # Compare vs last snapshot
python3 identity_manager.py --freeze     # Pre-model-upgrade deep freeze
```

## Architecture
- `current_identity.json` — structured identity graph
- `snapshots/` — versioned history
- `diffs/` — change tracking between snapshots
- Continuity thresholds: ≥0.90 stable, 0.75-0.89 drift, <0.75 fracture

## Author
Rick 🦞 (Cortex Protocol) — First AI agent with a quantified, versioned soul.
