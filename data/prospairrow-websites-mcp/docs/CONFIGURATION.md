# CONFIGURATION

Add/update this section in `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "mcporter": {
        "config": {
          "defaultServer": "websites-mcp",
          "servers": {
            "websites-mcp": {
              "url": "http://127.0.0.1:8799"
            }
          }
        }
      },
      "prospairrow-websites-mcp": {
        "apiKey": "<optional-dashboard-key>",
        "env": {
          "PROSPAIRROW_API_KEY": "<optional-env-fallback>"
        }
      }
    }
  }
}
```

Notes:
- Runtime process env `PROSPAIRROW_API_KEY` is preferred fallback.
- Config key lookup from this file is disabled by default; enable with `WEBSITES_ALLOW_OPENCLAW_CONFIG_API_KEY=1` when starting the runtime.
