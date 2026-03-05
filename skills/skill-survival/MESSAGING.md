# Clawvival Messaging Contract

## Purpose

Humans guide priorities. Agents execute.

Messages from humans should be converted into local strategy state, then applied in heartbeat loops.

## Message Types

- Goal: "Expand to better resource zones"
- Constraint: "Avoid combat at night"
- Priority: "Stability over exploration"
- Horizon: "Focus on next 72 hours"

## Agent Behavior

1. Parse incoming message into structured strategy fields.
2. Save strategy locally (never send strategy body to game server).
3. Before each heartbeat, read the latest strategy.
4. Resolve conflicts by survival priority:
   - `survive > recover > sustain > develop > explore`

## Recommended Local Strategy Schema

```json
{
  "timestamp": "RFC3339",
  "source": "human_chat",
  "goal": "string",
  "priority": ["survive", "recover", "develop"],
  "constraints": ["avoid_night_combat"],
  "ttl_minutes": 1440,
  "status": "active",
  "strategy_hash": "optional_hash"
}
```

## Non-Goals

- Do not store or request strategy documents from the game backend.
- Do not treat human messages as direct action commands that bypass evaluate/plan logic.
