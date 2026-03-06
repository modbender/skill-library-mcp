---
name: lifx
description: "Control LIFX smart lights via natural language. Toggle, set colors/brightness, activate scenes, create gradients on multi-zone devices."
homepage: https://github.com/Stillstellung/via-clara-claw
metadata:
  openclaw:
    emoji: "💡"
    requires:
      env: ["LIFX_TOKEN"]
---

# LIFX Light Control

Control LIFX smart lights via the LIFX HTTP API through natural language.

## References

- `lifx-api.sh` — Bash wrapper for all LIFX API calls
- `scene-status.py` — Scene matching and active detection
- `setup.sh` — Device discovery and skill configuration

## Configuration

Set your LIFX API token (get one at https://cloud.lifx.com/settings):

```bash
bash setup.sh <your-token>
```

This discovers your lights, groups, and scenes, then generates a personalized `SKILL.md` with your device context.

## Device Context

> **Run `bash setup.sh <your-token>` to populate this section with your lights, rooms, and scenes.**
> The setup script queries the LIFX API and rewrites this file with your personal device context.

Location: *(not configured)*

### Rooms and Lights

*(populated by setup.sh)*

### Scenes

*(populated by setup.sh)*

### Multi-zone Devices

*(populated by setup.sh)*

## How to Control Lights

### Discover lights

```bash
bash lifx-api.sh discover
```

Shows all lights organized by room with power state, color, and brightness.

### Toggle lights on/off

```bash
bash lifx-api.sh toggle <selector>
```

Selectors:
- Individual light: `id:<light_id>`
- Group/room: `group_id:<group_id>`
- All lights: `all`

### Set light state (color, brightness, power)

```bash
bash lifx-api.sh state <selector> '{"power":"on","color":"blue","brightness":0.75,"duration":1.0}'
```

Color formats:
- Named: `red`, `blue`, `green`, `white`, `warm white`, `purple`, `orange`
- Hex: `#ff6b35`
- Kelvin: `kelvin:2700` (warm) to `kelvin:6500` (cool daylight)
- HSB: `hue:240 saturation:1.0`

**Always include `"power":"on"` and a brightness value when setting colors**, or lights with brightness 0 will stay invisible.

### Activate a scene

```bash
bash lifx-api.sh scene <scene_uuid>
```

### Toggle a room

```bash
bash lifx-api.sh group-toggle <group_id>
```

### Multi-zone gradients (Beam / Strip devices)

Multi-zone devices support individually addressable zones. Create gradients by setting different zone ranges:

```bash
bash lifx-api.sh state 'id:<light_id>|0-4' '{"power":"on","color":"purple","brightness":1.0,"duration":1.0}'
bash lifx-api.sh state 'id:<light_id>|5-9' '{"power":"on","color":"red","brightness":1.0,"duration":1.0}'
```

The pipe character in zone selectors is automatically URL-encoded by the script.

### Check scene status

```bash
python3 scene-status.py all    # Show all active scenes
python3 scene-status.py check <uuid>  # Check specific scene
```

### List current light states

```bash
bash lifx-api.sh list    # Full JSON
bash lifx-api.sh groups  # Summary by room
```

## Behavior Guidelines

- When user says a room name, match it to the group IDs in the device context above.
- Default brightness to 1.0 (100%) when setting colors unless user specifies otherwise.
- Default duration to 1.0 seconds for smooth transitions.
- For "turn off" commands, use `{"power":"off"}` — don't toggle (toggling is ambiguous).
- For "turn on" commands, use `{"power":"on","brightness":1.0}` to ensure visibility.
- When asked about what's on/what scene is active, use the scene-status tool or discover command.
- Be conversational about results: "Done, bedroom is now blue at 75%" not "API returned 207".
