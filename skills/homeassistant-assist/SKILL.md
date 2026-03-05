---
name: homeassistant-assist
description: Control Home Assistant smart home devices using the Assist (Conversation) API. Use this skill when the user wants to control smart home entities - lights, switches, thermostats, covers, vacuums, media players, or any other smart device. Passes natural language directly to Home Assistant's built-in NLU for fast, token-efficient control.
homepage: https://github.com/DevelopmentCats/homeassistant-assist
metadata:
  openclaw:
    emoji: "🏠"
    requires:
      bins: ["curl"]
      env: ["HASS_SERVER", "HASS_TOKEN"]
    primaryEnv: "HASS_TOKEN"
---

# Home Assistant Assist

Control smart home devices by passing natural language to Home Assistant's Assist (Conversation) API. **Fire and forget** — trust Assist to handle intent parsing, entity resolution, and execution.

## When to Use This Skill

Use this skill when the user wants to **control or query any smart home device**. If it's in Home Assistant, Assist can handle it.

## How It Works

Pass the user's request directly to Assist:

```bash
curl -s -X POST "$HASS_SERVER/api/conversation/process" \
  -H "Authorization: Bearer $HASS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text": "USER REQUEST HERE", "language": "en"}'
```

**Trust Assist.** It handles:
- Intent parsing
- Fuzzy entity name matching
- Area-aware commands
- Execution
- Error responses

## Handling Responses

**Just relay what Assist says.** The `response.speech.plain.speech` field contains the human-readable result.

- `"Turned on the light"` → Success, tell the user
- `"Sorry, I couldn't understand that"` → Assist couldn't parse it
- `"Sorry, there are multiple devices called X"` → Ambiguous name

**Don't over-interpret.** If Assist says it worked, it worked. Trust the response.

## When Assist Returns an Error

Only if Assist returns an error (`response_type: "error"`), you can **suggest HA-side improvements**:

| Error | Suggestion |
|-------|------------|
| `no_intent_match` | "HA didn't recognize that command" |
| `no_valid_targets` | "Try checking the entity name in HA, or add an alias" |
| Multiple devices | "There may be duplicate names — consider adding unique aliases in HA" |

These are **suggestions for improving HA config**, not skill failures. The skill did its job — it passed the request to Assist.

## Setup

Set environment variables in OpenClaw config:

```json
{
  "env": {
    "HASS_SERVER": "https://your-homeassistant-url",
    "HASS_TOKEN": "your-long-lived-access-token"
  }
}
```

Generate a token: Home Assistant → Profile → Long-Lived Access Tokens → Create Token

## API Reference

### Endpoint

```
POST /api/conversation/process
```

**Note:** Use `/api/conversation/process`, NOT `/api/services/conversation/process`.

### Request

```json
{
  "text": "turn on the kitchen lights",
  "language": "en"
}
```

### Response

```json
{
  "response": {
    "speech": {
      "plain": {"speech": "Turned on the light"}
    },
    "response_type": "action_done",
    "data": {
      "success": [{"name": "Kitchen Light", "id": "light.kitchen"}],
      "failed": []
    }
  }
}
```

## Philosophy

- **Trust Assist** — It knows the user's HA setup better than we do
- **Fire and forget** — Pass the request, relay the response
- **Don't troubleshoot** — If something doesn't work, suggest HA config improvements
- **Keep it simple** — One API call, natural language in, natural language out

## Links

- [Home Assistant Conversation API Docs](https://developers.home-assistant.io/docs/intent_conversation_api/)
