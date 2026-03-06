# TS3

Backends that scale.

## Core Ideas

TS3 combines HTTP server scaffolding with middleware composition. Request validation and structured logging are first-class; no add-ons required.

## Quickstart

```bash
claw install skill-ts3
./scripts/server-init.sh --routes --health
```

## API

- `--routes` — Scaffold route handlers
- `--health` — Configure `/health` endpoint
- `--describe` — Show server architecture
