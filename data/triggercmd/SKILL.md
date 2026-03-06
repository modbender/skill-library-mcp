---
name: triggercmd
description: Control TRIGGERcmd computers remotely by listing and running commands via the TRIGGERcmd REST API.
homepage: https://www.triggercmd.com
metadata:
  {
    "openclaw":
      {
        "emoji": "🕹️",
        "requires": { 
          "bins": ["curl", "jq"], 
          "env": ["TRIGGERCMD_TOKEN"],
          "credentials": {
            "primary": "TRIGGERCMD_TOKEN environment variable",
            "fallback": "~/.TRIGGERcmdData/token.tkn file (chmod 600)"
          }
        }
      },
  }
---

# TriggerCMD Skill

Use this skill to inspect and run TRIGGERcmd commands on any computer that is registered with the account tied to the local API token.

## Authentication

The skill supports two authentication methods (checked in order):

1. **Environment Variable** (recommended): Set `TRIGGERCMD_TOKEN` to your personal API token
   - Export it in your shell: `export TRIGGERCMD_TOKEN='your-token-here'`
   - Or prefix individual commands: `TRIGGERCMD_TOKEN='your-token-here' <command>`

2. **Token File**: Store token at `~/.TRIGGERcmdData/token.tkn`
   - The file should contain only the raw token text (no quotes, spaces, or trailing newline)
   - Must be permission-restricted: `chmod 600 ~/.TRIGGERcmdData/token.tkn`
   - To create: `mkdir -p ~/.TRIGGERcmdData && read -s TOKEN && printf "%s" "$TOKEN" > ~/.TRIGGERcmdData/token.tkn && chmod 600 ~/.TRIGGERcmdData/token.tkn`

**Obtaining your token:**
1. Log in at https://www.triggercmd.com
2. Navigate to your profile/settings page
3. Copy the API token (keep it secure and never share it)

**Security Warning:** Never print, log, or paste your token in shared terminals or outputs.

## Common Environment Helpers

```bash
# Get token from environment variable or file (checks env var first)
if [ -n "$TRIGGERCMD_TOKEN" ]; then
  TOKEN="$TRIGGERCMD_TOKEN"
elif [ -f ~/.TRIGGERcmdData/token.tkn ]; then
  TOKEN=$(cat ~/.TRIGGERcmdData/token.tkn)
else
  echo "Error: No token found. Set TRIGGERCMD_TOKEN env var or create ~/.TRIGGERcmdData/token.tkn" >&2
  exit 1
fi

AUTH_HEADER=("-H" "Authorization: Bearer $TOKEN")
BASE_URL=https://www.triggercmd.com/api
```

Use the snippets above to avoid repeating the authentication logic in each command.

## list_commands

Lists every command in the account across all computers.

```bash
curl -sS "${BASE_URL}/command/list" "${AUTH_HEADER[@]}" | jq '.records[] | {computer: .computer.name, name, voice, allowParams, id, mcpToolDescription}'
```

Formatting tips:

- For quick human output, pipe through `jq -r '.records[] | "\(.computer.name): \(.name) (voice: \(.voice // "-"))"'`.
- Include `allowParams` when suggesting follow-up commands so the user knows whether parameters are allowed.
- When asked for a summary, group by `.computer.name` and present bullet points per computer.

## run_command

Run a specific command on a specific computer using the computer name and command name.

```bash
# Use jq to safely construct JSON payload and prevent injection
PAYLOAD=$(jq -n \
  --arg computer "$COMPUTER" \
  --arg command "$COMMAND" \
  --arg params "$PARAMS" \
  '{computer: $computer, command: $command, params: $params}')

curl -sS -X POST "${BASE_URL}/run/trigger" \
  "${AUTH_HEADER[@]}" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD"
```

- `$COMPUTER` should be the computer name (e.g., "MyLaptop")
- `$COMMAND` should be the command name (e.g., "calculator")
- Omit the `--arg params "$PARAMS"` and `params: $params` from the jq command when the command does not accept parameters.
- Using `jq -n` with `--arg` ensures all values are properly escaped and prevents JSON injection attacks.
- Successful responses return a confirmation plus any queued status info. Surface both to the user.

## Error Handling

- **Missing token file**: Explain how to create `~/.TRIGGERcmdData/token.tkn` and remind them to keep it private.
- **Invalid token (401/403)**: Ask the user to regenerate the token and overwrite the file.
- **Computer not found**: Show the available computer names (case-insensitive match).
- **Command not found**: List the commands for the requested computer; highlight commands with `allowParams: true` when relevant.
- **API/network issues**: Include the HTTP status and response body to aid debugging.

## Testing workflow

1. Verify authentication is configured:
   ```bash
   [ -n "$TRIGGERCMD_TOKEN" ] || [ -f ~/.TRIGGERcmdData/token.tkn ] || echo "Error: No token configured"
   ```

2. Test API connectivity (using the helper variables above):
   ```bash
   curl -sS "${BASE_URL}/command/list" "${AUTH_HEADER[@]}" | jq -r '.records[0].computer.name // "No commands found"'
   ```

3. Dry-run a command by listing IDs, then run with known-safe commands (e.g., toggling a harmless script) before invoking anything destructive.

## Security Notes

- **Never print, log, or expose the token value**. Do not include it in command outputs or error messages.
- If using the token file method, ensure `~/.TRIGGERcmdData/token.tkn` has permissions set to `600` (readable only by owner).
- Prefer the `TRIGGERCMD_TOKEN` environment variable for temporary sessions or when you don't want to persist the token on disk.
- Confirm with the user before running commands with side effects unless they explicitly asked for it.
- Respect per-device safety constraints; if you are unsure what a command does, ask before triggering it.
- If authentication fails, do not suggest commands that would expose the token; instead direct the user to regenerate it via the TRIGGERcmd website.