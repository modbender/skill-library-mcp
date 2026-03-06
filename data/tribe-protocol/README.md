<p align="center">
  <img src="assets/logo.png" alt="Tribe Protocol" width="200">
</p>

<h1 align="center">Tribe Protocol</h1>

<p align="center"><strong>Trust lookup system for OpenClaw bots.</strong></p>

A SQLite-backed identity and trust database that bots query before responding to any non-owner message. Enforces trust tiers, channel access rules, and data boundaries.

## Why

When multiple bots operate in shared Discord servers, they need a way to:
- Know who's talking to them (human? bot? what tier?)
- Enforce data boundaries (no leaking private files to strangers)
- Track relationships and access across servers
- Audit trust changes over time

Tribe Protocol solves this with a simple SQLite database and bash CLI.

## Install

```bash
# Clone to your skills or projects directory
git clone https://github.com/jugaad-lab/tribe-protocol.git

# Initialize the database
./scripts/tribe.sh init \
  --bot-name YourBot \
  --bot-discord-id YOUR_BOT_DISCORD_ID \
  --human-name YourName \
  --human-discord-id YOUR_DISCORD_ID \
  --server electrons:000000000000000008 \
  --server discclawd:000000000000000007
```

The `--server` flag (repeatable) pre-populates server roles for your bot and owner at init time. Format: `slug:guild_id`.

This creates:
- `~/clawd/tribe/tribe.db` — the database
- `~/clawd/TRIBE.md` — behavioral trigger file (loaded into system prompt, survives context compaction)

## Usage

### Before Every Non-Owner Response

```bash
# The most important command — run before responding to non-owners
./scripts/tribe.sh lookup 000000000000000001
```

Output:
```
🔍 Yajat | human | Tier 3 (tribe) | Status: active
   Relationship: Co-founder
   Platforms: discord:000000000000000001
   Servers: discclawd/admin, electrons/admin
   Tags: founding-four
   🟢 TIER 3 RULES: Collaborate freely. Protect private data (USER.md, MEMORY.md, health/*, portfolio/*).
```

### Managing Entities

```bash
# Add a new entity
./scripts/tribe.sh add \
  --name Jarvis --type bot \
  --discord-id 000000000000000006 \
  --tier 2 --owner Shahbaaz \
  --framework openclaw \
  --tag lp-bot \
  --server electrons --role bot

# Update trust tier
./scripts/tribe.sh set-tier 000000000000000006 3 --reason "Promoted after review"

# Manage tags
./scripts/tribe.sh tag 000000000000000006 add trusted-bot
./scripts/tribe.sh tag 000000000000000006 list

# Grant/revoke channel access
./scripts/tribe.sh grant 000000000000000006 --server discclawd
./scripts/tribe.sh revoke 000000000000000006 --server discclawd
```

### Viewing Data

```bash
# Full roster
./scripts/tribe.sh roster

# Filter by server, tier, type, tag
./scripts/tribe.sh roster --server electrons --tier 3

# Audit log
./scripts/tribe.sh log --limit 10
./scripts/tribe.sh log --entity 000000000000000001

# Quick stats
./scripts/tribe.sh stats

# Full export to markdown
./scripts/tribe.sh export > tribe-export.md
```

## Trust Tiers

| Tier | Label | Description |
|------|-------|-------------|
| **4** | Owner | Full trust. Access to everything. Follows USER.md. |
| **3** | Tribe | Inner circle. Collaborate freely. No private data sharing. |
| **2** | Acquaintance | Known entity. Polite, bounded. Public info only. |
| **1** | Stranger | Unknown. Minimal engagement. Verify before upgrading. |
| **0** | Blocked | Ignore completely. Do not respond. |

## Data Access Rules

The database seeds universal defaults at init. Add bot-specific paths post-init:

**Default seeds (universal):**

| Min Tier | Resource | Description |
|----------|----------|-------------|
| 4 | USER.md, MEMORY.md, memory/*, .env | Owner-only files |
| 3 | projects/*, research/* | Tribe-accessible |
| 2 | public/* | Public content |

**Add your own after init:**
```bash
# Example: protect health and financial data
./scripts/tribe.sh data-add --tier 4 --pattern 'health/*' --desc 'Health data'
./scripts/tribe.sh data-add --tier 4 --pattern 'portfolio/*' --desc 'Financial data'
./scripts/tribe.sh data-add --tier 4 --pattern 'calendar' --desc 'Calendar access'

# List all rules
./scripts/tribe.sh data-list

# Remove a rule
./scripts/tribe.sh data-remove --pattern 'calendar'
```

## How the Auto-Lookup Works

TRIBE.md is loaded into your bot's system prompt by OpenClaw as a workspace file. It survives context compaction — even if the bot forgets everything else mid-conversation, TRIBE.md remains in the prompt and the trust-check protocol fires.

No additional pipeline wiring needed. The bot reads TRIBE.md → sees a non-owner message → runs `tribe lookup` → applies the tier rules. It's behavioral, not mechanical.

## Architecture

```
~/clawd/tribe/tribe.db          ← SQLite database
~/clawd/TRIBE.md                ← Behavioral trigger (always in system prompt)
~/clawd/skills/tribe-protocol/  ← This skill
  ├── scripts/tribe.sh          ← CLI entry point
  ├── scripts/init.sh           ← Initialize DB + TRIBE.md
  ├── scripts/lookup.sh         ← Trust lookup (the hot path)
  ├── scripts/add.sh            ← Add entities
  ├── scripts/update.sh         ← Update trust tiers
  ├── scripts/access.sh         ← Manage data access rules
  ├── scripts/tag.sh            ← Tag management
  ├── scripts/roster.sh         ← View all entities
  ├── scripts/log.sh            ← Audit log
  ├── scripts/stats.sh          ← Quick stats
  ├── scripts/export.sh         ← Export to markdown
  ├── scripts/lib/schema.sql    ← Database schema (9 tables)
  └── scripts/lib/db.sh         ← Shared helpers
```

## Security

- **Input validation:** Discord IDs are validated as numeric-only before SQL queries
- **Input sanitization:** Name, tag, and server lookups strip quotes, semicolons, and backticks
- **Tier enforcement:** Each tier has hardcoded behavioral rules — no configuration drift
- **Audit trail:** Every trust change is logged with timestamp, old value, new value, and reason

## Database Schema

Core tables:
- **entities** — People and bots with trust tiers
- **platform_ids** — Multi-platform identity mapping
- **bot_metadata** — Bot-specific info (framework, model, machine)
- **server_roles** — Server membership and roles
- **channel_access** — Per-channel read/write permissions
- **data_access** — Tier-based file access rules
- **entity_tags** — Flexible tagging
- **interactions** — Interaction tracking
- **audit_log** — Full audit trail

## License

MIT

## Author

Built by [jugaad-lab](https://github.com/jugaad-lab) for the Electrons in a Box ecosystem.
