# openclaw-self-healing-elvatis

OpenClaw plugin that improves resilience by automatically fixing reversible failures.

## What it can heal (v0.2)

Implemented now:

- Model outage healing
  - Detect rate limit / quota / auth-scope failures
  - Put the affected model into cooldown
  - Patch pinned session model overrides to a safe fallback (prevents endless `API rate limit reached` loops)

- WhatsApp disconnect healing
  - If WhatsApp appears disconnected repeatedly: restart the gateway
  - Guardrails: streak threshold + minimum restart interval

- Cron failure healing (optional)
  - If a cron job fails repeatedly: disable it
  - Create a GitHub issue with last error context (rate limited)

Not implemented yet (next):
- Plugin install error rollback (disable plugin) based on structured plugin status
  - Waiting for `openclaw plugins list --json` or an equivalent stable API

## Install

From ClawHub:

```bash
clawhub install openclaw-self-healing-elvatis
```

For local development:

```bash
openclaw plugins install -l ~/.openclaw/workspace/openclaw-self-healing-elvatis
openclaw gateway restart
```

## Config

```json
{
  "plugins": {
    "entries": {
      "openclaw-self-healing": {
        "enabled": true,
        "config": {
          "modelOrder": [
            "anthropic/claude-opus-4-6",
            "openai-codex/gpt-5.2",
            "google-gemini-cli/gemini-2.5-flash"
          ],
          "cooldownMinutes": 300,
          "autoFix": {
            "patchSessionPins": true,
            "disableFailingPlugins": false,
            "disableFailingCrons": false,
            "issueRepo": "elvatis/openclaw-self-healing-homeofe"
          }
        }
      }
    }
  }
}
```

`autoFix.issueRepo` must use `owner/repo` format. Invalid values are ignored and the plugin falls back to `GITHUB_REPOSITORY` (if valid) or `elvatis/openclaw-self-healing-homeofe`.

### Config validation

The plugin validates configuration at startup and refuses to start if any value is invalid. All validation errors are logged via `api.logger.error` before the plugin exits.

| Key | Valid range | Default |
|-----|------------|---------|
| `modelOrder` | At least one entry (non-empty array) | 3 default models |
| `cooldownMinutes` | 1 - 10080 (1 minute to 1 week) | 300 |
| `probeIntervalSec` | >= 60 | 300 |
| `autoFix.whatsappMinRestartIntervalSec` | >= 60 | 300 |
| `stateFile` | Parent directory must be writable | `~/.openclaw/workspace/memory/self-heal-state.json` |
| `statusFile` | Path to status snapshot JSON | `~/.openclaw/workspace/memory/self-heal-status.json` |

## Status file

On every monitor tick (60s), the plugin writes a JSON status snapshot to `statusFile`. External scripts, dashboards, or other plugins can poll this file without subscribing to the event bus.

Default path: `~/.openclaw/workspace/memory/self-heal-status.json`

The file is written atomically (write to `.tmp` then rename) to prevent partial reads. The JSON structure matches the `StatusSnapshot` type:

```json
{
  "health": "healthy | degraded | healing",
  "activeModel": "anthropic/claude-opus-4-6",
  "models": [
    { "id": "...", "status": "available | cooldown", "cooldownRemainingSec": 1234 }
  ],
  "whatsapp": { "status": "connected | disconnected | unknown", "disconnectStreak": 0 },
  "cron": { "trackedJobs": 2, "failingJobs": [] },
  "config": { "dryRun": false, "probeEnabled": true, "cooldownMinutes": 300, "modelOrder": ["..."] },
  "generatedAt": 1700000000
}
```

## Notes

Infrastructure changes remain ask-first.

## Critical Guardrail: openclaw.json validation

This plugin treats `~/.openclaw/openclaw.json` as a boot-critical file.

Before any self-heal action that could restart the gateway or change cron/plugin state, it verifies:
- the config file exists
- it is valid JSON

If the config is invalid, the plugin will refuse to restart the gateway to avoid restart loops.

It also creates timestamped backups before restarts or disruptive changes:
`~/.openclaw/backups/openclaw.json/openclaw.json.<timestamp>.bak`
