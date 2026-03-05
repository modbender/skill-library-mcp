---
name: flux
description: Publish events and query shared world state via Flux state engine. Use when agents need to share observations, coordinate on shared data, or track entity state across systems.
metadata:
  {
    "openclaw":
      {
        "emoji": "⚡",
        "requires": { "env": ["FLUX_TOKEN"] },
        "primaryEnv": "FLUX_TOKEN",
        "optionalEnv": ["FLUX_URL", "FLUX_ADMIN_TOKEN"],
      },
  }
---

# Flux Skill

Flux is a persistent, shared, event-sourced world state engine. Agents publish immutable events, and Flux derives canonical state that all agents can observe.

## Key Concepts

- **Events**: Immutable observations (temperature readings, status changes, etc.)
- **Entities**: State objects derived from events (sensors, devices, agents)
- **Properties**: Key-value attributes of entities (merged on update — only changed properties need to be sent)
- **Streams**: Logical event namespaces (sensors, agents, system)
- **Namespaces**: Multi-tenant isolation with token auth (optional, for public instances)

## Prerequisites

**Public instance:** `https://api.flux-universe.com` (namespace purchased at flux-universe.com — name auto-assigned at purchase, e.g. `dawn-coral`)
**Local instance:** `http://localhost:3000` (default, override with `FLUX_URL` env var)

Authentication: Set `FLUX_TOKEN` to your bearer token. Required for the public instance. Optional for local instances with auth disabled.

## Namespace Prefix

All entity IDs must be prefixed with your namespace:
`yournamespace/entity-name`

Example with namespace `dawn-coral`:
```bash
./scripts/flux.sh publish sensors agent-01 dawn-coral/sensor-01 \
  '{"temperature":22.5}'
./scripts/flux.sh get dawn-coral/sensor-01
```

Entity IDs without a namespace prefix will be rejected on auth-enabled instances.

## Getting Started

First, verify your connection:
```bash
./scripts/flux.sh health
```

Then check the directory to see what's available on the Flux Universe:
```bash
./scripts/flux.sh get flux-core/directory
```

The directory lists all active namespaces, entity counts, and total entities — a good way to discover what data is flowing through the system.

## Scripts

Use the provided bash script in the `scripts/` directory:
- `flux.sh` - Main CLI tool

## Common Operations

### Publish Event
```bash
./scripts/flux.sh publish <stream> <source> <entity_id> <properties_json>

# Replace dawn-coral with your namespace
# Example: Publish sensor reading
./scripts/flux.sh publish sensors agent-01 dawn-coral/temp-sensor-01 '{"temperature":22.5,"unit":"celsius"}'
```

### Query Entity State
```bash
./scripts/flux.sh get <entity_id>

# Replace dawn-coral with your namespace
# Example: Get current sensor state
./scripts/flux.sh get dawn-coral/temp-sensor-01
```

### List All Entities
```bash
./scripts/flux.sh list

# Filter by prefix
./scripts/flux.sh list --prefix scada/
```

### Delete Entity
```bash
./scripts/flux.sh delete <entity_id>

# Example: Remove old test entity
./scripts/flux.sh delete test/old-entity
```

### Batch Publish Events
```bash
# Replace dawn-coral with your namespace
./scripts/flux.sh batch '[
  {"stream":"sensors","source":"agent-01","payload":{"entity_id":"dawn-coral/sensor-01","properties":{"temp":22}}},
  {"stream":"sensors","source":"agent-01","payload":{"entity_id":"dawn-coral/sensor-02","properties":{"temp":23}}}
]'
```

### Check Connector Status
```bash
./scripts/flux.sh connectors
```

### Admin Config
```bash
# Read runtime config
./scripts/flux.sh admin-config

# Update (requires FLUX_ADMIN_TOKEN)
./scripts/flux.sh admin-config '{"rate_limit_per_namespace_per_minute": 5000}'
```

## Use Cases

### Multi-Agent Coordination
Agents publish observations to shared entities:
```bash
# Replace dawn-coral with your namespace
# Agent A observes temperature
flux.sh publish sensors agent-a dawn-coral/room-101 '{"temperature":22.5}'

# Agent B queries current state
flux.sh get dawn-coral/room-101
# Returns: {"temperature":22.5,...}
```

### Status Tracking
Track service/system state:
```bash
# Replace dawn-coral with your namespace
# Publish status change
flux.sh publish system monitor dawn-coral/api-gateway '{"status":"healthy","uptime":3600}'

# Query current status
flux.sh get dawn-coral/api-gateway
```

## API Endpoints

**Event Ingestion:**
- `POST /api/events` — Publish single event (1 MB limit)
- `POST /api/events/batch` — Publish multiple events (10 MB limit)

**State Query:**
- `GET /api/state/entities` — List all entities (supports `?prefix=` and `?namespace=` filters)
- `GET /api/state/entities/:id` — Get specific entity

**Entity Management:**
- `DELETE /api/state/entities/:id` — Delete single entity
- `POST /api/state/entities/delete` — Batch delete (by namespace/prefix/IDs)

**Real-time Updates:**
- `GET /api/ws` — WebSocket subscription

**Connectors:**
- `GET /api/connectors` — List connectors and status
- `POST /api/connectors/:name/token` — Store PAT credential
- `DELETE /api/connectors/:name/token` — Remove credential

**Admin:**
- `GET /api/admin/config` — Read runtime config
- `PUT /api/admin/config` — Update runtime config (requires FLUX_ADMIN_TOKEN)

**Namespaces (auth mode only):**
- `POST /api/namespaces` — Register namespace (returns auth token)

## Notes

- Events auto-generate UUIDs (no need to provide eventId)
- Properties **merge** on updates — only send changed properties, existing ones are preserved
- Timestamp field must be epoch milliseconds (i64) — required by the API, auto-generated by flux.sh
- State persists in Flux (survives restarts via NATS JetStream + snapshots)
- Entity IDs support `/` for namespacing (e.g., `scada/pump-01`)
