# Via Clara Claw 💡

An [OpenClaw](https://github.com/openclaw/openclaw) skill for controlling [LIFX](https://www.lifx.com/) smart lights through natural language.

Born from [Via Clara](https://github.com/Stillstellung/via-clara) — this is the agent-native version. Instead of a web dashboard with an LLM intermediary, your AI agent talks directly to the LIFX API. The agent *is* the language model, so no extra API calls needed for natural language understanding.

## What It Does

- **Natural language light control** — "turn the bedroom lights blue at 50%"
- **Room/group control** — "turn off the living room"
- **Scene activation** — "activate House Stardust"
- **Scene detection** — "what scenes are currently active?"
- **Multi-zone gradients** — "make the Beam a purple-to-red gradient"
- **Device discovery** — "what lights do I have?"

Works from any OpenClaw channel: Telegram, Discord, Signal, WhatsApp, IRC, etc.

## Setup

### 1. Get your LIFX token

Go to [cloud.lifx.com/settings](https://cloud.lifx.com/settings) and generate a personal access token.

### 2. Run setup

```bash
git clone https://github.com/Stillstellung/via-clara-claw.git
cd via-clara-claw
bash setup.sh <your-lifx-token>
```

This discovers all your lights, groups, and scenes, then generates a personalized `SKILL.md` with your device context baked in. The agent uses this context to map room names to group IDs and scene names to UUIDs.

### 3. Install as an OpenClaw skill

Copy the directory into your OpenClaw workspace:

```bash
cp -r . /path/to/openclaw/workspace/skills/lifx
```

Or symlink it:

```bash
ln -s "$(pwd)" /path/to/openclaw/workspace/skills/lifx
```

### 4. Use it

Just talk to your agent:

> "Turn off the reading room lights"
> "Make the office warm white"
> "Set the bedroom to red at 75%"
> "Activate Basement Movie"
> "What's on right now?"

## Files

| File | Purpose |
|------|---------|
| `SKILL.md.template` | Generic skill definition — `setup.sh` generates `SKILL.md` from this |
| `SKILL.md` | Generated — your personalized skill with device context (gitignored) |
| `lifx-api.sh` | Bash wrapper for LIFX HTTP API |
| `scene-status.py` | Scene matching with tolerance-based detection |
| `setup.sh` | Device discovery and SKILL.md generator |
| `.lifx-token` | Your LIFX API token (gitignored) |

## LIFX API Reference

The skill wraps the [LIFX HTTP API](https://api.lifx.com/docs/):

```bash
# Discover lights (human-readable)
bash lifx-api.sh discover

# List all lights (JSON)
bash lifx-api.sh list

# List rooms
bash lifx-api.sh groups

# Toggle a light or group
bash lifx-api.sh toggle <selector>
bash lifx-api.sh group-toggle <group_id>

# Set state (color, brightness, power)
bash lifx-api.sh state <selector> '{"power":"on","color":"blue","brightness":0.75}'

# Activate a scene
bash lifx-api.sh scene <scene_uuid>

# Check active scenes
python3 scene-status.py all
python3 scene-status.py check <scene_uuid>
```

### Selectors

- Individual light: `id:<light_id>`
- Group/room: `group_id:<group_id>`
- All lights: `all`
- Multi-zone: `id:<light_id>|0-4` (pipe auto-encoded)

### Color formats

- Named: `red`, `blue`, `purple`, `warm white`
- Hex: `#ff6b35`
- Kelvin: `kelvin:2700` (warm) → `kelvin:6500` (daylight)
- HSB: `hue:240 saturation:1.0`

## Requirements

- [OpenClaw](https://github.com/openclaw/openclaw) (any channel)
- LIFX lights + API token
- `curl`, `jq`, `python3` with `requests`

## License

GPL-3.0 — see [LICENSE](LICENSE).

## See Also

- [Via Clara](https://github.com/Stillstellung/via-clara) — the web dashboard version
- [OpenClaw](https://github.com/openclaw/openclaw) — the agent platform
- [LIFX HTTP API](https://api.lifx.com/docs/) — official API docs
