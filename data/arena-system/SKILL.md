---
name: arena-system
description: Adversarial self-improvement for AI agents. Reduces hallucinations through Agent vs Anti-Agent debate loops.
---

# Arena System

Adversarial self-improvement framework for AI agents.

## What it does

Give one agent two personas:
- **Agent** - Does the work, writes reports
- **Anti-Agent** - Questions everything, writes counter-reports

They take turns critiquing each other until you stop them.

## Why use it

AI agents are overconfident. They hallucinate. Arena forces them to question their own outputs by arguing with themselves.

## Setup

```bash
./setup.sh ~/my-arena
```

Creates:
```
my-arena/
├── state.json
├── prompts/agent.md
├── prompts/anti-agent.md
└── outputs/
```

## Usage

Add to HEARTBEAT.md:
1. Read `state.json` → whose turn?
2. Run that persona
3. Write to `outputs/{role}/iteration_N.md`
4. Switch turns, save state

## Config

`state.json`:
```json
{
  "current_turn": "agent",
  "iteration": 0,
  "topic": "my-project",
  "active": true,
  "max_iterations": 10
}
```

## Results

Prevents premature deployments, catches bugs, forces proper validation before going live.
