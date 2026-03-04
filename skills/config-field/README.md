# OpenClaw Config Field Validator

Validate OpenClaw configuration fields against the official Zod schema.

## Features

- ✅ **Version Sync** - Auto-detects local OpenClaw version and syncs schema
- ✅ **Field Validation** - Check if configuration fields exist in schema
- ✅ **Typo Detection** - Suggests corrections for invalid field paths
- ✅ **Config Validation** - Validate entire openclaw.json files
- ✅ **Field Info** - Get detailed field type information and enum values

## Installation

### Method 1: Direct Download

```bash
# Download the skill file to OpenClaw skills directory
curl -L -o ~/.config/openclaw/skills/config-field.skill \
  https://github.com/YOUR_USERNAME/openclaw-config-field/releases/latest/download/config-field.skill

# Restart OpenClaw or reload skills
openclaw skills reload
```

### Method 2: Manual Install

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/openclaw-config-field.git

# Package the skill
cd openclaw-config-field
python3 /path/to/openclaw/skills/skill-creator/scripts/package_skill.py ./config-field

# Copy to skills directory
cp config-field.skill ~/.config/openclaw/skills/
```

## Usage

Once installed, the skill automatically triggers when working with OpenClaw configurations.

### Validate a Field

```bash
python3 ~/.config/openclaw/skills/config-field/scripts/validate_field.py agents.defaults.model.primary
```

### Validate Config File

```bash
python3 ~/.config/openclaw/skills/config-field/scripts/validate_config.py ~/.config/openclaw/openclaw.json
```

### Get Field Information

```bash
python3 ~/.config/openclaw/skills/config-field/scripts/field_info.py logging.level
```

### Check Schema Status

```bash
python3 ~/.config/openclaw/skills/config-field/scripts/sync_schema.py --status
```

### Force Schema Resync

```bash
python3 ~/.config/openclaw/skills/config-field/scripts/sync_schema.py --force
```

## How It Works

1. **Version Detection** - Reads local OpenClaw version from package.json
2. **Schema Sync** - Maintains cached schema in `~/.config/openclaw/skills/config-field/`
3. **Field Generation** - Generates field reference from schema.json
4. **Validation** - Uses cached schema to validate configuration fields

## Supported Fields

The skill includes 136+ field definitions covering:

- `agents` - Agent configurations (defaults, list, sandbox, memory)
- `channels` - Channel configs (telegram, discord, slack, etc.)
- `tools` - Tool settings (web, exec, fs, profile)
- `logging` - Logging configuration
- `session` - Session management
- `commands` - Command settings
- And more...

See [references/schema-fields.md](config-field/references/schema-fields.md) for complete list.

## Development

### Project Structure

```
config-field/
├── SKILL.md                      # Skill definition
├── scripts/
│   ├── validate_field.py         # Single field validation
│   ├── validate_config.py        # Config file validation
│   ├── field_info.py             # Field information
│   ├── sync_schema.py            # Schema synchronization
│   ├── generate_fields.py        # Generate field reference
│   ├── schema_loader.py          # Schema loading utilities
│   └── schema.json               # Built-in field definitions
└── references/
    └── schema-fields.md          # Generated field reference
```

### Building

```bash
# Package the skill
python3 /path/to/openclaw/skills/skill-creator/scripts/package_skill.py ./config-field

# Output: config-field.skill
```

### Testing

```bash
# Test field validation
cd config-field
python3 scripts/validate_field.py agents.defaults.model.primary

# Test config validation
python3 scripts/validate_config.py /path/to/your/openclaw.json
```

## License

MIT License - See [LICENSE](LICENSE) for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Credits

Built for OpenClaw - The AI agent runtime.
