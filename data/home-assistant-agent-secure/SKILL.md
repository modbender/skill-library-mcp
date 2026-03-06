---
name: home-assistant-agent-secure
description: Control Home Assistant smart home devices securely using the Assist (Conversation) API. Passes natural language to Home Assistant's built-in NLU for safe, token-efficient device control. Designed to work with a restricted non-admin HA user for minimal access exposure.
metadata: {"openclaw":{"emoji":"🏠","requires":{"bins":["curl"],"env":["HOME_ASSISTANT_URL","HOME_ASSISTANT_TOKEN"]},"primaryEnv":"HOME_ASSISTANT_TOKEN"}}
---

# Home Assistant Agent (Secure)

Control smart home devices by sending natural language to Home Assistant's Conversation (Assist) API.

**Security model:** This skill uses ONLY the `/api/conversation/process` endpoint. Do NOT use the token to call any other HA API endpoint. The token should belong to a restricted, non-admin Home Assistant user with access limited to specific areas and entities.

## Important Security Rules

- **ONLY** call `/api/conversation/process` — never call `/api/states`, `/api/services`, `/api/config`, or any other endpoint
- **NEVER** output or echo the token value
- **NEVER** use the token for any purpose other than the Assist API call below
- **NEVER** attempt to log in to Home Assistant via the browser or web UI — always use the API token
- If a user request cannot be handled by Assist, say so — do not fall back to other API calls

## Important: Disable Trusted Networks Login Bypass

If your Home Assistant instance uses the `trusted_networks` auth provider with `allow_bypass_login: true`, any agent or user on the local network can log in as **any** HA user (including administrators) without a password. This completely bypasses the restricted-user security model of this skill.

**To fix:** In your HA `configuration.yaml`, set `allow_bypass_login: false` under the `trusted_networks` auth provider, or remove the `trusted_networks` provider entirely. Restart HA after making the change.

## Setup

### 1. Create a Restricted Home Assistant User

1. In Home Assistant go to **Settings → People → Add Person**
2. Create a new user (e.g. `openclaw-bot`)
3. **Do NOT make it an administrator**
4. Under **Settings → Areas & Zones**, assign only the areas this user should control
5. Optionally restrict entity access using a custom group or dashboard-only permissions

### 2. Generate a Long-Lived Access Token

1. Log in to Home Assistant **as the restricted user** (`openclaw-bot`)
2. Go to **Profile** (bottom-left)
3. Scroll to **Long-Lived Access Tokens**
4. Click **Create Token**, name it (e.g. `openclaw`)
5. Copy the token immediately — it is shown only once

### 3. Configure OpenClaw

Set `HOME_ASSISTANT_URL` and `HOME_ASSISTANT_TOKEN` using any of the methods below. OpenClaw applies them in this precedence order (highest first): process environment → `.env` file → `openclaw.json` config. A value set by a higher-priority source is never overridden by a lower one.

**Option A: `.env` file (recommended)**

Add to `~/.openclaw/.env`:

```bash
HOME_ASSISTANT_URL=https://your-ha-instance.local
HOME_ASSISTANT_TOKEN=your-restricted-user-token-here
```

The URL can be a hostname (e.g. `https://homeassistant.local`) or an IP address (e.g. `https://192.168.1.50:8123`).

**Option B: Config file**

Add to `~/.openclaw/openclaw.json` under `skills.entries`:

```json
{
  "skills": {
    "entries": {
      "home-assistant-agent-secure": {
        "apiKey": "your-restricted-user-token-here",
        "env": {
          "HOME_ASSISTANT_URL": "https://your-ha-instance.local"
        }
      }
    }
  }
}
```

The `apiKey` field automatically maps to `HOME_ASSISTANT_TOKEN` via the skill's `primaryEnv` declaration.

**Option C: Shell environment variables**

Export in your shell profile (e.g. `~/.bashrc`, `~/.zshrc`):

```bash
export HOME_ASSISTANT_URL="https://your-ha-instance.local"
export HOME_ASSISTANT_TOKEN="your-restricted-user-token-here"
```

## Usage

Send any smart home command in natural language. The skill passes it directly to HA Assist:

```bash
curl -sk -X POST "$HOME_ASSISTANT_URL/api/conversation/process" \
  -H "Authorization: Bearer $HOME_ASSISTANT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text": "USER REQUEST HERE", "language": "DETECTED LANGUAGE CODE"}'
```

> The `-k` flag allows connections to HA instances using self-signed certificates. If your HA uses a trusted certificate (e.g. Let's Encrypt), you can remove it.

Set the `language` field based on the detected language of the user's input (e.g. `"pl"` for Polish, `"en"` for English, `"de"` for German, etc.).

### Examples

- "Turn on the living room lights" (English)
- "Włącz światło w salonie" (Polish)
- "Schalte das Licht im Wohnzimmer ein" (German)
- "Jaka jest temperatura w kuchni?" (Polish)
- "Turn off all lights in the bedroom" (English)

## Inflected Language Handling (Nominative Retry)

Many languages use grammatical cases or word inflection, causing entity names to change form in natural speech. Home Assistant entity names are typically in their base/dictionary form (nominative), but users naturally use other grammatical forms in commands.

This affects languages including (but not limited to):
- **Polish** — 7 cases (e.g. *drukarkę* → *drukarka*, *lampę* → *lampa*)
- **Czech** — 7 cases (e.g. *tiskárnu* → *tiskárna*, *lampu* → *lampa*)
- **German** — 4 cases + articles (e.g. *den Drucker* → *Drucker*, *die Lampe* → *Lampe*)
- **Finnish** — 15 cases (e.g. *tulostinta* → *tulostin*, *lamppua* → *lamppu*)
- **Hungarian** — 18 cases (e.g. *nyomtatót* → *nyomtató*, *lámpát* → *lámpa*)
- **Russian** — 6 cases (e.g. *принтер**у*** → *принтер*, *ламп**у*** → *лампа*)
- **Croatian/Serbian** — 7 cases, similar patterns to Polish and Czech

**Example:** A user says *"włącz drukarkę 3d"* (Polish accusative), but the entity is named *"drukarka 3d"* (nominative). HA Assist won't find it.

**Retry strategy:** If HA responds with an error (`no_valid_targets`, `no_intent_match`, or a message indicating the entity was not found), and the user's input is in an inflected language:

1. Identify the entity name within the command
2. Convert inflected words to their base/dictionary/nominative form
3. Retry the API call with the corrected form
4. If the retry also fails, report the error to the user

**Important:** Only retry **once**. Do not loop. If the nominative retry also fails, inform the user that the entity was not found.

## Handling Responses

The response is in `response.speech.plain.speech`. Relay it directly to the user:

- `"Turned on the light"` → success
- `"Sorry, I couldn't understand that"` → Assist couldn't parse the request
- `"Sorry, there are multiple devices called X"` → ambiguous entity name

### On errors (`response_type: "error"`)

| Error | What to tell the user |
|-------|----------------------|
| `no_intent_match` | Try nominative retry (if inflected language). If still fails: "Home Assistant didn't recognize that command." |
| `no_valid_targets` | Try nominative retry (if inflected language). If still fails: "Entity not found — check the device name or add an alias in HA." |
| Multiple matches | "Multiple devices share that name — consider adding unique aliases in HA." |

## Troubleshooting

- **401 Unauthorized**: Token is invalid or expired. Generate a new one from the restricted user's profile.
- **Connection refused**: Check that `HOME_ASSISTANT_URL` is correct and HA is reachable.
- **Command not understood**: Rephrase the request or check that the entity is exposed to the restricted user.
- **Entity not found**: The restricted user may not have access to that area/entity. Update permissions in HA.

## API Reference

### Endpoint

```
POST /api/conversation/process
```

**Note:** Use `/api/conversation/process`, NOT `/api/services/conversation/process`.

### Request Body

```json
{
  "text": "turn on the kitchen lights",
  "language": "en"
}
```

Polish example:

```json
{
  "text": "włącz światło w salonie",
  "language": "pl"
}
```

### Success Response

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
