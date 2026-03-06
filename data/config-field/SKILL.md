---
name: config-field
description: Validate OpenClaw configuration fields against the official Zod schema. Use when reading or writing openclaw.json to check if configuration fields exist and are valid. Covers agents, channels, tools, logging, session configuration with 136+ field definitions.
---

# Config Field Validator

Validate OpenClaw configuration fields against the official Zod schema.

## When to Use This Skill

- **Before editing configurations** - Verify a field exists before adding it
- **Debugging config errors** - Check if invalid fields are causing issues
- **Migrating configs** - Validate fields after version upgrades
- **Reviewing configs** - Ensure all fields are schema-compliant

## How It Works

This skill automatically manages schema synchronization:

1. **Check Version** - Detects local OpenClaw version
2. **Sync Schema** - Downloads matching schema from GitHub if needed
3. **Generate Fields** - Parses Zod schema to extract field definitions
4. **Validate** - Uses generated schema to validate configuration

## Quick Start

```bash
# Validate a single field (auto-syncs schema if needed)
python3 scripts/validate_field.py agents.defaults.model.primary

# Validate entire config file
python3 scripts/validate_config.py /path/to/openclaw.json

# Force schema re-sync
python3 scripts/sync_schema.py --force

# Check current schema status
python3 scripts/sync_schema.py --status
```

## Field Path Format

Field paths use dot notation:

```
agents.defaults.model.primary              → agents.defaults.model.primary
channels.telegram.botToken                 → channels.telegram.botToken
tools.web.search.provider                  → tools.web.search.provider
```

## Workflow

### For Users

Simply use validation commands - schema sync is automatic:

```bash
# This will auto-sync schema if version mismatch detected
python3 scripts/validate_field.py agents.defaults.timeoutSeconds
```

### For Schema Management

```bash
# Check schema status
python3 scripts/sync_schema.py --status
# Output: Schema version: 2.1.0 (matches OpenClaw)

# Force re-sync (if needed)
python3 scripts/sync_schema.py --force

# Generate fresh field reference
python3 scripts/generate_fields.py
```

## Schema Storage

Schema is cached locally at:
```
~/.config/openclaw/skills/config-field/
├── schema/              # Downloaded TypeScript schema files
├── cache/               # Parsed schema cache
└── schema-fields.md     # Generated field reference
```

## Reference

### Complete Field Reference
**[references/schema-fields.md](references/schema-fields.md)** - Auto-generated from official Zod schema

## Scripts

| Script | Purpose |
|--------|---------|
| `validate_field.py <path>` | Validate single field |
| `validate_config.py <file>` | Validate entire config |
| `field_info.py <path>` | Get field details |
| `sync_schema.py` | Manage schema sync |
| `generate_fields.py` | Regenerate field docs |

## Common Fields

### Agent Configuration
- `agents.defaults.model.primary` - Default model ID
- `agents.defaults.workspace` - Workspace path
- `agents.defaults.timeoutSeconds` - Request timeout
- `agents.defaults.sandbox.mode` - Sandbox mode

### Channel Configuration
- `channels.telegram.botToken` - Telegram bot token
- `channels.discord.token` - Discord bot token
- `channels.slack.botToken` - Slack bot token

### Tools
- `tools.web.search.enabled` - Enable web search
- `tools.web.search.provider` - Search provider
- `tools.exec.security` - Execution security mode

## Troubleshooting

### Schema Out of Date

If you see warnings about unknown fields that should exist:

```bash
# Force schema refresh
python3 scripts/sync_schema.py --force
```

### Validation Errors

```bash
# Check field info for correct usage
python3 scripts/field_info.py agents.defaults.model

# Verify config syntax
python3 scripts/validate_config.py ~/.config/openclaw/openclaw.json
```
