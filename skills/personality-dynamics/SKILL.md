---
name: personality-dynamics
description: Dynamic personality evolution for OpenClaw agents. Learn interaction patterns, adapt tone, and mode switching.
metadata: { "openclaw": { "requires": { "bins": ["node"], "files": ["SOUL.md", "MEMORY.md"] } } }
---

# Personality Dynamics

Transform your OpenClaw agent from a static assistant into a dynamic companion that learns your preferences and adapts to your communication style.

## What It Does

### 1. Pattern Recognition
Tracks how you interact:
- Communication style (bullet points vs paragraphs)
- Response preferences (autonomous vs ask first)
- Engagement topics (what excites you vs bores you)

### 2. Mode Switching
Explicit personas for different contexts:
- **Professional Mode** — Work communications, formal contexts
- **Creative Mode** — Brainstorming, building, experimental
- **Casual Mode** — Late night, relaxed, friendly banter
- **Focus Mode** — Minimal chatter, maximum efficiency

### 3. Auto-Evolution
Weekly analysis generates suggestions for SOUL.md updates.

## Quick Start

```bash
# Initialize
npx personality-dynamics init

# Generate AI-powered persona
npx personality-dynamics generate
```

## Commands

- `init` - Initialize PERSONA folder
- `generate` - AI-powered persona generation
- `analyze` - Analyze session patterns
- `report` - Weekly evolution report
- `mode [set/get]` - Switch personality modes

## Configuration

Enable via OpenClaw config:

```json
{
  "personality": {
    "enabled": true,
    "evolution_frequency": "weekly"
  }
}
```

## License

MIT
