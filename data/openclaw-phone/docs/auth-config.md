# Auth and Config

This skill follows OpenClaw key handling best practice.

## Resolution order

1. Environment variable: `CALLMYCALL_API_KEY`
2. User config: `~/.openclaw/openclaw.json` at `skills.openclaw-phone.apiKey`
3. If missing, prompt once for an API key and ask if it should be saved.

## Persist behavior

When the key is provided interactively:

- Ask: "Save this key to ~/.openclaw/openclaw.json for future sessions?"
- Persist only on explicit confirmation.
- Store at: `skills.openclaw-phone.apiKey`

If the user declines, use the key for the current task only.

## Security rules

- Never store API keys in this skill repository (`SKILL.md`, `README.md`, `examples/`, `references/`).
- Never store API keys in call memory/state such as `recent_calls`.
- Never echo the full key in chat output.

## Example config shape

```json
{
  "skills": {
    "openclaw-phone": {
      "apiKey": "<redacted>"
    }
  }
}
```
