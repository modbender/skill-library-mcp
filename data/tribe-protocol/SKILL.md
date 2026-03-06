---
name: tribe-protocol
version: 1.0.0
description: >
  MANDATORY trust lookup for every non-owner interaction.
  Query tribe.db to check entity trust tier, channel access,
  and data boundaries before responding. Run 'tribe init' on
  first install. Use 'tribe lookup <discord_id>' before every
  non-owner response.
commands:
  tribe: scripts/tribe.sh
---

# Tribe Protocol

Trust lookup system for OpenClaw bots. Every non-owner interaction must be verified against the tribe database before responding.

## Quick Start

```bash
# Initialize (first time only)
./scripts/tribe.sh init \
  --bot-name Cheenu \
  --bot-discord-id 000000000000000004 \
  --human-name Nagarjun \
  --human-discord-id 000000000000000002

# Look up an entity before responding
./scripts/tribe.sh lookup <discord_id>

# Add entities
./scripts/tribe.sh add --name Yajat --type human --discord-id 000000000000000001 --tier 3

# Manage trust
./scripts/tribe.sh set-tier <discord_id> 3 --reason "Promoted to tribe"
./scripts/tribe.sh set-status <discord_id> blocked --reason "Bad actor"
```

## Trust Tiers

| Tier | Label | Access |
|------|-------|--------|
| 4 | Owner | Full trust, all data |
| 3 | Tribe | Collaborate freely, no private data |
| 2 | Acquaintance | Public info only |
| 1 | Stranger | Minimal engagement |
| 0 | Blocked | Ignore completely |

## How It Works

1. Message arrives from non-owner
2. Bot reads TRIBE.md (generated at workspace root)
3. Bot runs `tribe lookup <discord_id>`
4. Script returns entity info + tier rules reminder
5. Bot applies tier-appropriate behavior

## Commands

- `tribe init` — Initialize database
- `tribe lookup` — Query entity by discord_id, name, tag, server
- `tribe add` — Add new entity
- `tribe set-tier` — Update trust tier
- `tribe set-status` — Update status
- `tribe grant` / `tribe revoke` — Channel access
- `tribe tag` — Manage tags
- `tribe roster` — List all entities
- `tribe log` — Audit trail
- `tribe export` — Dump to markdown
- `tribe stats` — Quick summary

## Environment Variables

- `TRIBE_DB` — Override database path
- `CLAWD_HOME` — Base directory (default: ~/clawd)

## Dependencies

- `sqlite3` (pre-installed on macOS/most Linux)
