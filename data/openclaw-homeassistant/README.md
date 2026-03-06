# @elvatis_com/openclaw-homeassistant

OpenClaw plugin for Home Assistant - control devices, read sensors, trigger automations via AI.

**34 tools** | **zero runtime dependencies** | **safety-first design**

## Prerequisites

- Node.js >= 18.0.0
- A running [Home Assistant](https://www.home-assistant.io/) instance (2023.1+)
- A Home Assistant Long-Lived Access Token

## Installation

```bash
npm install @elvatis_com/openclaw-homeassistant
```

## Quick Start

### 1. Create a Long-Lived Access Token

1. Open your Home Assistant UI
2. Navigate to your profile (click your name in the sidebar)
3. Scroll down to **Long-Lived Access Tokens**
4. Click **Create Token**, give it a name (e.g. "OpenClaw"), and copy the token

### 2. Configure the Plugin

Add the plugin to your OpenClaw configuration:

```json
{
  "plugins": {
    "openclaw-homeassistant": {
      "url": "http://homeassistant.local:8123",
      "token": "YOUR_LONG_LIVED_ACCESS_TOKEN"
    }
  }
}
```

### 3. (Optional) Add Safety Guards

Restrict which domains the AI can access and/or enable read-only mode:

```json
{
  "plugins": {
    "openclaw-homeassistant": {
      "url": "http://homeassistant.local:8123",
      "token": "YOUR_LONG_LIVED_ACCESS_TOKEN",
      "allowedDomains": ["light", "switch", "sensor", "climate"],
      "readOnly": true
    }
  }
}
```

## Configuration Reference

| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `url` | `string` | Yes | - | Home Assistant base URL (e.g. `http://homeassistant.local:8123`) |
| `token` | `string` | Yes | - | Long-Lived Access Token from your HA profile |
| `allowedDomains` | `string[]` | No | `[]` (all) | Restrict tools to these HA domains only |
| `readOnly` | `boolean` | No | `false` | Block all write tools (service calls, events, notifications) |

## Safety Model

This plugin implements three layers of safety:

- **readOnly mode** - When enabled, all 22 write tools are blocked. Only read tools (status, list, get, search, history) remain available. Ideal for monitoring dashboards or untrusted agents.
- **allowedDomains** - Restrict which HA domains the AI can interact with. For example, `["light", "sensor"]` blocks access to switches, climate, media, covers, automations, and everything else.
- **Entity ID validation** - Every entity ID is validated against the pattern `{domain}.{object_id}` (lowercase alphanumeric + underscores only). Malformed IDs are rejected before reaching Home Assistant.

## Tool Reference

### Status and Discovery

| Tool | Description |
|------|-------------|
| `ha_status` | Get HA instance config (version, location, components) |
| `ha_list_entities` | List entities with optional `domain`, `area`, `state` filters |
| `ha_get_state` | Get state and attributes of a single entity |
| `ha_search_entities` | Search entities by pattern (matches entity_id and friendly_name) |
| `ha_list_services` | List all available services grouped by domain |

### Lights

| Tool | Description |
|------|-------------|
| `ha_light_on` | Turn on with optional `brightness` (0-255), `color_temp`, `rgb_color`, `transition` |
| `ha_light_off` | Turn off a light |
| `ha_light_toggle` | Toggle a light on/off |
| `ha_light_list` | List all light entities with brightness and color info |

### Switches

| Tool | Description |
|------|-------------|
| `ha_switch_on` | Turn on a switch |
| `ha_switch_off` | Turn off a switch |
| `ha_switch_toggle` | Toggle a switch on/off |

### Climate

| Tool | Description |
|------|-------------|
| `ha_climate_set_temp` | Set target temperature |
| `ha_climate_set_mode` | Set HVAC mode (heat, cool, auto, off) |
| `ha_climate_set_preset` | Set preset mode (away, home, eco, boost) |
| `ha_climate_list` | List all climate entities |

### Media Player

| Tool | Description |
|------|-------------|
| `ha_media_play` | Resume playback |
| `ha_media_pause` | Pause playback |
| `ha_media_stop` | Stop playback |
| `ha_media_volume` | Set volume (0.0-1.0) |
| `ha_media_play_media` | Play specific media (`content_id` + `content_type`) |

### Covers

| Tool | Description |
|------|-------------|
| `ha_cover_open` | Open a cover (blinds, garage door) |
| `ha_cover_close` | Close a cover |
| `ha_cover_position` | Set position (0 = closed, 100 = open) |

### Scenes and Automations

| Tool | Description |
|------|-------------|
| `ha_scene_activate` | Activate a scene |
| `ha_script_run` | Run a script with optional `variables` |
| `ha_automation_trigger` | Trigger an automation (optional `skip_condition`) |

### Sensors and History

| Tool | Description |
|------|-------------|
| `ha_sensor_list` | List all sensor entities with current values |
| `ha_history` | Get state history (defaults to last 24 hours) |
| `ha_logbook` | Get logbook entries (defaults to last 24 hours) |

### Generic and Advanced

| Tool | Description |
|------|-------------|
| `ha_call_service` | Call any HA service by `domain` + `service` + `service_data` |
| `ha_fire_event` | Fire a custom event on the HA event bus |
| `ha_render_template` | Render a Jinja2 template via the HA template engine |
| `ha_notify` | Send a notification via `notify/{target}` |

## Programmatic Usage

The plugin can also be used as a library:

```typescript
import { HAClient, createTools } from "@elvatis_com/openclaw-homeassistant";

const config = {
  url: "http://homeassistant.local:8123",
  token: "YOUR_TOKEN",
  allowedDomains: [],
  readOnly: false
};

const client = new HAClient(config);
const tools = createTools({ client, config });

// Get all entities
const entities = await tools.ha_list_entities({});

// Turn on a light at 50% brightness
await tools.ha_light_on({
  entity_id: "light.living_room",
  brightness: 128
});

// Check a sensor
const temp = await tools.ha_get_state({
  entity_id: "sensor.outdoor_temperature"
});
```

## Development

```bash
# Install dependencies
npm install

# Type-check
npm run typecheck

# Run tests
npm test

# Build
npm run build

# Watch mode
npm run dev
```

## Architecture

```
src/
  index.ts    - Plugin entry point, registers 34 tools with OpenClaw API
  client.ts   - HAClient: REST client using built-in fetch, Bearer auth, 30s timeout
  tools.ts    - Tool implementations (one function per tool)
  guards.ts   - Safety layer: readOnly, allowedDomains, entity validation
  types.ts    - TypeScript interfaces (PluginConfig, HAEntityState, etc.)
  __tests__/  - Jest tests with mocked HA API
```

## License

MIT - see [LICENSE](LICENSE) for details.
