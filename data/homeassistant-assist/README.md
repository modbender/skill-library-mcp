# Home Assistant Assist

[![ClawHub](https://img.shields.io/badge/ClawHub-homeassistant--assist-blue?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik0xMiAyQzYuNDggMiAyIDYuNDggMiAxMnM0LjQ4IDEwIDEwIDEwIDEwLTQuNDggMTAtMTBTMTcuNTIgMiAxMiAyem0wIDE4Yy00LjQxIDAtOC0zLjU5LTgtOHMzLjU5LTggOC04IDggMy41OSA4IDgtMy41OSA4LTggOHoiLz48L3N2Zz4=)](https://clawhub.com/skills/homeassistant-assist)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-purple)](https://github.com/openclaw/openclaw)

An [OpenClaw](https://github.com/openclaw/openclaw) skill for controlling Home Assistant smart home devices using the **Assist (Conversation) API**.

> [!IMPORTANT]
> This is an OpenClaw skill, not a HACS integration. It runs inside OpenClaw and communicates with your Home Assistant instance via its API.

## Why This Skill?

Instead of the AI manually looking up entity IDs and building verbose service calls, this skill passes natural language directly to Home Assistant's built-in NLU.

| Approach | Tokens | API Calls | Reliability |
|----------|--------|-----------|-------------|
| Entity Lookup Method | High | Multiple | Fragile |
| **Assist API** | **Low** | **One** | **Robust** |

**Benefits:**
- Faster — Single API call instead of multiple lookups
- Cheaper — Fewer tokens spent on entity resolution
- More reliable — Home Assistant knows your home better than any AI

## Requirements

- [OpenClaw](https://github.com/openclaw/openclaw) installed and running
- Home Assistant instance with API access
- A [Long-Lived Access Token](https://developers.home-assistant.io/docs/auth_api/#long-lived-access-token) from Home Assistant

## Installation

### From ClawHub (Recommended)

```bash
clawhub install homeassistant-assist
```

Or ask your OpenClaw agent:

> "Install the homeassistant-assist skill"

### Manual Installation

```bash
git clone https://github.com/DevelopmentCats/homeassistant-assist.git \
  ~/.openclaw/workspace/skills/homeassistant-assist
```

## Configuration

Add the following to your OpenClaw config (`~/.openclaw/openclaw.json`):

```json
{
  "env": {
    "HASS_SERVER": "https://your-homeassistant-url",
    "HASS_TOKEN": "your-long-lived-access-token"
  }
}
```

### Getting Your Token

1. Open Home Assistant
2. Click your profile (bottom left)
3. Scroll to **Long-Lived Access Tokens**
4. Click **Create Token**
5. Give it a name (e.g., "OpenClaw")
6. Copy the token immediately (it won't be shown again!)

Then restart OpenClaw:

```bash
openclaw gateway restart
```

## Usage

Just talk naturally to your OpenClaw agent:

```
"Turn off the kitchen lights"
"Set the thermostat to 72"
"What's the temperature in the living room?"
"Close the garage door"
"Turn on the bedroom fan"
"Is the front door locked?"
```

The AI passes your request to Home Assistant's Assist API, which handles:
- Intent parsing
- Fuzzy entity name matching
- Area-aware commands
- Execution

## Tips & Troubleshooting

### Entity Names
Home Assistant's Assist uses **friendly names**. If "bedroom light" doesn't work but "bedroom lamp" does, that's the entity's friendly name in HA. You can:
- Add aliases in Home Assistant (Settings → Devices → Entity → Edit → Aliases)
- Use the exact friendly name shown in HA

### Automations
Assist can **enable/disable** automations but cannot **trigger** them directly. Workaround:
1. Create an automation in HA with a **sentence trigger** (e.g., "cycle the robot vacuum")
2. Have the automation call whatever service you need
3. Now you can say that phrase to Assist!

### "Sorry, I couldn't understand that"
- Try rephrasing with simpler language
- Check if the device exists and is named as expected
- Make sure the Assist pipeline is working in HA (Settings → Voice Assistants)

### Multiple Devices with Same Name
If Assist says "there are multiple devices called X", add unique aliases to your entities in Home Assistant.

## Links

- **ClawHub:** [clawhub.com/skills/homeassistant-assist](https://clawhub.com/skills/homeassistant-assist)
- **GitHub:** [github.com/DevelopmentCats/homeassistant-assist](https://github.com/DevelopmentCats/homeassistant-assist)
- **OpenClaw:** [github.com/openclaw/openclaw](https://github.com/openclaw/openclaw)
- **HA Conversation API Docs:** [developers.home-assistant.io](https://developers.home-assistant.io/docs/intent_conversation_api/)

## License

MIT © [DevelopmentCats](https://github.com/DevelopmentCats)

---

<p align="center">
  <a href="https://clawhub.com/skills/homeassistant-assist">
    <img src="https://img.shields.io/badge/Install%20with-ClawHub-blue?style=for-the-badge" alt="Install with ClawHub">
  </a>
</p>
