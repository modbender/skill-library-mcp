# home-assistant-agent-secure

An OpenClaw skill for controlling Home Assistant smart home devices securely using the Conversation (Assist) API.

## Why This Approach?

Unlike skills that use the full HA REST API, this skill **only** calls the `/api/conversation/process` endpoint. Combined with a restricted non-admin HA user, this limits the attack surface significantly:

- No access to configuration, logs, or add-on management
- No ability to call arbitrary services
- The Assist pipeline only handles recognized smart home intents
- Even if the token is leaked, the restricted user limits what can be accessed

## Requirements

- `curl` on PATH
- A running Home Assistant instance with HTTPS access
- A **restricted (non-admin)** HA user with a Long-Lived Access Token

> **Note:** If your HA instance uses a self-signed certificate, the skill uses curl's `-k` flag to allow the connection. If you use a trusted certificate (e.g. Let's Encrypt), you can remove the `-k` flag from the curl command in `SKILL.md`.

## Installation

### 1. Set Up Home Assistant

1. Create a non-admin user in HA (e.g. `openclaw-bot`) via **Settings > People > Add Person**
2. Log in as that user and go to **Profile > Long-Lived Access Tokens > Create Token**
3. Copy the token immediately

### 2. Install the Skill

Copy the skill folder into your OpenClaw skills directory:

```bash
cp -r home-assistant-agent-secure ~/.openclaw/skills/home-assistant-agent-secure
```

### 3. Configure Secrets

OpenClaw picks up environment variables in this order (highest priority first): process environment → `.env` file → `openclaw.json` config. Use whichever method you prefer.

**Option A: `.env` file (recommended)**

Add to `~/.openclaw/.env` alongside your other API keys:

```bash
HOME_ASSISTANT_URL=https://your-ha-instance
HOME_ASSISTANT_TOKEN=your-restricted-user-token
```

The URL can be a hostname (e.g. `https://homeassistant.local`) or an IP address (e.g. `https://192.168.1.50:8123`).

**Option B: Config file**

Add to `~/.openclaw/openclaw.json` under `skills.entries`:

```json
{
  "skills": {
    "entries": {
      "home-assistant-agent-secure": {
        "apiKey": "your-restricted-user-token",
        "env": {
          "HOME_ASSISTANT_URL": "https://your-ha-instance"
        }
      }
    }
  }
}
```

The `apiKey` field maps to `HOME_ASSISTANT_TOKEN` automatically via the skill's `primaryEnv` declaration.

**Option C: Shell environment variables**

Export in your shell profile (e.g. `~/.bashrc`, `~/.zshrc`):

```bash
export HOME_ASSISTANT_URL="https://your-ha-instance"
export HOME_ASSISTANT_TOKEN="your-restricted-user-token"
```

### 4. Verify

Ask OpenClaw to control a device (e.g. "turn on the living room lights"). It should relay the command through HA Assist and return the result.

## Usage Examples

Works in any language supported by Home Assistant:

- "Turn on the living room lights" (English)
- "Włącz światło w salonie" (Polish)
- "Schalte das Licht im Wohnzimmer ein" (German)
- "Jaka jest temperatura w kuchni?" (Polish)
- "Turn off all lights in the bedroom" (English)

### Entity Aliases (Recommended)

The Assist API matches commands against entity names. By default, entities often have technical names (e.g. `light.relay_1`) that are hard to use in conversation. **Setting up aliases is crucial** for this skill to work well.

To add aliases in Home Assistant:

1. Go to **Settings > Devices & Services > Entities**
2. Click on an entity
3. Click the gear icon to edit
4. Add one or more **Aliases** — these are alternative names Assist will recognize

**Tips:**
- Use natural, conversational names (e.g. "living room light", "bedroom lamp")
- Add aliases in every language you plan to use (e.g. "salon light" and "światło w salonie")
- For inflected languages, use the nominative/base form — the skill handles case conversion automatically
- Add multiple aliases if a device has common nicknames (e.g. "TV", "telewizor", "television")

### Inflected Language Support

Many languages (Polish, Czech, German, Finnish, Hungarian, Russian, etc.) change word forms based on grammatical case. Since Home Assistant entity names are in base/nominative form, the skill automatically retries with the nominative form if HA can't find an entity on the first attempt. For example, *"włącz drukarkę 3d"* (accusative) is retried as *"włącz drukarka 3d"* (nominative).

## Security Notes

- The skill instructs the agent to **never** call any HA endpoint other than `/api/conversation/process`
- The token should belong to a **non-admin** user with limited area/entity access
- The token is **never** echoed or logged by the skill
- If Assist can't handle a request, the skill reports the error rather than falling back to other API calls
- **Important caveat:** The Long-Lived Access Token is not technically scoped to the Conversation API — it grants access to all HA API endpoints available to that user. The endpoint restriction is enforced by the skill instructions, not by the token itself. This is why using a **restricted non-admin user** is critical — it limits the blast radius even if the token is misused

### Trusted Networks Warning

If your HA uses the `trusted_networks` auth provider with `allow_bypass_login: true`, anyone on the local network (including OpenClaw) can log in as **any** user without a password — including admin accounts. This bypasses all restricted-user protections.

**Fix:** Set `allow_bypass_login: false` in your HA `configuration.yaml`, or remove the `trusted_networks` auth provider entirely. Restart HA after the change.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| 401 Unauthorized | Token expired or invalid — regenerate from the restricted user's profile |
| Connection refused | Check `HOME_ASSISTANT_URL` is correct and HA is reachable |
| Command not understood | Rephrase, or check the entity is exposed to the restricted user |
| Entity not found | The restricted user may lack access — update permissions in HA |

## License

MIT
