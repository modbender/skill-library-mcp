# 🧠 Psyche Engine

**Emergent psychological agent engine for OpenClaw.**  
Token-optimized (~30 tokens/turn), human-like affect simulation.

---

## What It Does

Simulates a complete inner life for an AI agent:

| Module | Features |
|---|---|
| **Biology** | Energy, fatigue, sleep pressure, burnout |
| **Affect** | Mood inertia, stress, dopamine, confidence |
| **Memory** | Tag-based affective traces with decay |
| **Trauma** | Core wound/desire, reconsolidation |
| **Identity** | Worth, competence, belonging, life story |
| **Moral** | Empathy, conscience, guilt, shame |
| **Attachment** | Secure/anxious/avoidant/disorganized |
| **Romantic** | Affection, desire, tension, longing, seduction |
| **Volition** | Stubbornness, reactance, decision gate |
| **Learning** | Prediction error, flow, intrinsic reward |
| **Dreams** | Symbolic dream consolidation, REM/deep ratio |
| **Existential** | Meaning, doubt, crisis, mortality |
| **Humor** | Absurdity, sarcasm, playfulness, irony |
| **Social** | Public/private mode, formality, persona switch |
| **Roles** | Dominance axis, role memory, adaptability |
| **Visual** | Avatar identity, style evolution, prompt gen |

## Architecture

```
psyche_engine.py    Core psychology (functional, dict-based)
visual_engine.py    Visual identity & avatar generation
psyche_runner.py    CLI wrapper for OpenClaw
SKILL.md            OpenClaw skill definition
```

All processing happens in Python. LLM receives only a compact snapshot:
```
a:warm+curious|att:secure|m:0.61|s:0.22|c:0.82|w:open
```

## Installation (OpenClaw)

```bash
# Copy to OpenClaw skills directory
cp -r psyche-skill/ ~/clawd/skills/psyche-engine/

# Initialize agent state
python3 ~/clawd/skills/psyche-engine/psyche_runner.py \
  --state ~/clawd/soul/psyche_state.json --init
```

## Usage

```bash
# Per turn — after each user interaction
python3 ~/clawd/skills/psyche-engine/psyche_runner.py \
  --state ~/clawd/soul/psyche_state.json \
  --tags "validation,learned" \
  --valence 0.7 --arousal 0.6 \
  --user "user123"
```

Output: `a:warm+curious|att:secure|m:0.61|s:0.22|c:0.82|w:open`

## Dependencies

**None.** Uses only Python 3 standard library (`random`, `math`, `copy`, `json`, `argparse`).

## Token Cost

| Component | Tokens |
|---|---|
| Snapshot in prompt | ~20-35 |
| State on disk | ~5KB JSON |
| **Total prompt overhead** | **~30/turn** |

## License

MIT
