# Flux Skill for OpenClaw

An OpenClaw skill that enables agents to publish events and query shared world state via [Flux](https://github.com/EckmanTechLLC/flux) — a persistent, event-sourced state engine.

## What is Flux?

Flux is a state engine that ingests immutable events and derives canonical world state. Multiple agents can:
- Publish observations as events
- Query current state of entities
- Coordinate through shared state
- Audit full event history

**Key difference from pub/sub:** Flux owns state derivation. Agents don't process raw events—they observe Flux's canonical state.

## Installation

### Local Testing (Option 1)

Copy skill to OpenClaw workspace:
```bash
# On OpenClaw VM
mkdir -p ~/workspace/skills
scp -r <your-host>:/path/to/flux-interact ~/workspace/skills/
```

OpenClaw will auto-discover on next startup.

### ClawHub Install (Option 2)

Install from: https://clawhub.ai/EckmanTechLLC/flux

## Prerequisites

1. **Flux:** public instance at `https://api.flux-universe.com` (default), or local at `http://localhost:3000` (set `FLUX_URL` to override)
2. **curl** installed (required)
3. **jq** recommended (optional, has fallback)

Verify connection:
```bash
cd ~/workspace/skills/flux-interact
./scripts/flux.sh health
```

## Usage Examples

> **Note:** entity IDs must be prefixed with your namespace (e.g. `dawn-coral/sensor-01`, not `sensor-01`)

### For OpenClaw Agents

Agents can naturally use Flux via the skill:

**User:** "What's the temperature of sensor-01?"

**Agent:** Let me check the current state in Flux.
```bash
./scripts/flux.sh get temp-sensor-01
```

**User:** "Record that room-101 temperature is 22.5 celsius"

**Agent:** I'll publish that observation to Flux.
```bash
./scripts/flux.sh publish sensors assistant room-101 '{"temperature":22.5,"unit":"celsius"}'
```

**User:** "Show me all entities we're tracking"

**Agent:**
```bash
./scripts/flux.sh list
```

### Direct CLI Usage

```bash
# Publish sensor reading
./scripts/flux.sh publish sensors agent-01 temp-sensor-01 '{"temperature":22.5,"unit":"celsius"}'

# Query entity state
./scripts/flux.sh get temp-sensor-01

# List all entities
./scripts/flux.sh list

# Test connection
./scripts/flux.sh health
```

## Use Cases

### Multi-Agent Coordination

Multiple OpenClaw instances share state via Flux:

```bash
# Agent A on VM1 observes
flux.sh publish sensors agent-a room-101 '{"temperature":22.5}'

# Agent B on VM2 queries
flux.sh get room-101
# Returns: {"temperature":22.5,...}
```

### Status Tracking

Monitor services across infrastructure:

```bash
# Publish service status
flux.sh publish system monitor api-gateway '{"status":"healthy","latency_ms":45}'

# Query current status
flux.sh get api-gateway
```

### Event Sourcing

All state changes are auditable:
- Events immutable (persisted in NATS)
- State derived from event history
- Can replay/debug past states

## Configuration

### Custom Flux URL

Default is `https://api.flux-universe.com`. Override for local instances:
```bash
export FLUX_URL=http://localhost:3000
./scripts/flux.sh health
```

## File Structure

```
flux-interact/
├── SKILL.md              # Skill definition for OpenClaw
├── scripts/
│   └── flux.sh          # CLI tool (bash + curl)
├── references/
│   └── api.md           # Full API documentation
└── README.md            # This file
```

## How It Works

1. **OpenClaw loads SKILL.md** when Flux is mentioned
2. **Agent reads instructions** on how to use scripts
3. **Agent calls flux.sh** with appropriate command
4. **Script makes HTTP requests** to Flux API
5. **Returns JSON** for agent to process

## Architecture

```
OpenClaw Agent
    ↓
SKILL.md instructions
    ↓
flux.sh script
    ↓
curl → Flux API (https://api.flux-universe.com or http://localhost:3000)
    ↓
Event Ingestion → NATS → State Engine → Query Response
```

## Limitations

- No WebSocket subscription support in flux.sh (use wscat or a WebSocket client directly against `GET /api/ws`)
- State is domain-agnostic (no schema validation)

## Contributing

This skill is part of [Flux](https://github.com/EckmanTechLLC/flux).

## License

*To be determined*
