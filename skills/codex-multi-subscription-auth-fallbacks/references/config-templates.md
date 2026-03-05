# Config Templates

## openclaw.json — Auth Section

Add to `openclaw.json` under `auth`:

```json
{
  "auth": {
    "profiles": {
      "anthropic:<your-anthropic-id>": {
        "provider": "anthropic",
        "mode": "token"
      },
      "openai-codex:<account-1>": {
        "provider": "openai-codex",
        "mode": "oauth"
      },
      "openai-codex:<account-2>": {
        "provider": "openai-codex",
        "mode": "oauth"
      }
    },
    "order": {
      "anthropic": [
        "anthropic:<your-anthropic-id>"
      ],
      "openai-codex": [
        "openai-codex:<account-1>",
        "openai-codex:<account-2>"
      ]
    }
  }
}
```

- **`profiles`** — Declare each profile. `mode` is `"token"` for API keys, `"oauth"` for Codex device-flow tokens.
- **`order`** — Failover priority per provider. First entry is tried first.

## openclaw.json — Model Fallback

Add to `openclaw.json` under `agents.defaults`:

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "anthropic/claude-opus-4-6",
        "fallbacks": [
          "openai-codex/gpt-5.3-codex"
        ]
      },
      "models": {
        "anthropic/claude-opus-4-6": {
          "alias": "opus"
        },
        "openai-codex/gpt-5.3-codex": {}
      }
    }
  }
}
```

- **`primary`** — Default model. Used unless in cooldown.
- **`fallbacks`** — Tried in order when primary is rate-limited.
- **`models`** — Model registry. `alias` allows short names in commands.

## auth-profiles.json Schema

Located at `agents/main/agent/auth-profiles.json`. Managed automatically by the add-profile script and OpenClaw runtime.

```json
{
  "version": 1,
  "profiles": {
    "openai-codex:<name>": {
      "type": "oauth",
      "provider": "openai-codex",
      "access": "<jwt-access-token>",
      "refresh": "<refresh-token>",
      "expires": 1772224563000,
      "accountId": "<openai-account-uuid>"
    }
  },
  "order": {
    "openai-codex": [
      "openai-codex:<account-1>",
      "openai-codex:<account-2>"
    ]
  },
  "lastGood": {
    "openai-codex": "openai-codex:<account-1>"
  },
  "usageStats": {
    "openai-codex:<account-1>": {
      "lastUsed": 1771366450513,
      "errorCount": 0
    }
  }
}
```

Fields:
- **`profiles`** — Live token data per profile
- **`order`** — Failover priority (mirrors openclaw.json)
- **`lastGood`** — Last profile that succeeded per provider
- **`usageStats`** — Auto-tracked. `cooldownUntil` set on rate limit, `errorCount` resets on success

## Cron Job — Model Cooldown Auto-Switch (Optional)

> **This cron job is optional.** It periodically checks for rate-limited providers and automatically switches your active model. When enabled, your model may change without manual intervention. Only add this if you want automatic failover behavior. The job runs only local commands (`openclaw models status`) and writes state to a local file — it does not contact external services.

Add to `cron/jobs.json` in the `jobs` array:

```json
{
  "id": "<generate-uuid>",
  "agentId": "main",
  "name": "model-cooldown-autoswitch",
  "enabled": true,
  "createdAtMs": <now-epoch-ms>,
  "updatedAtMs": <now-epoch-ms>,
  "schedule": {
    "kind": "every",
    "everyMs": 600000,
    "anchorMs": <now-epoch-ms>
  },
  "sessionTarget": "isolated",
  "wakeMode": "now",
  "payload": {
    "kind": "agentTurn",
    "message": "Check model/provider cooldown state and keep main session on an active model.\n\nAvailable auth profiles:\n- anthropic:<your-anthropic-id>\n- openai-codex:<account-1>\n- openai-codex:<account-2>\n\nProcess:\n1) Run `openclaw models status` via exec and parse the output for cooldown markers on each provider/profile.\n2) Pick the best available model based on cooldown state:\n   - Priority: opus (anthropic) > openai-codex/gpt-5.3-codex\n   - If anthropic is in cooldown, try openai-codex profiles (<account-1>, <account-2>)\n   - If all openai-codex profiles are in cooldown too, stay on whichever has the shortest remaining cooldown\n3) Set main session model override accordingly:\n   - use session_status with sessionKey=\"agent:main:main\", model=\"opus\" OR model=\"openai-codex/gpt-5.3-codex\"\n4) Keep a tiny state file at <workspace>/memory/model-switch-state.json with lastEffectiveModel, lastCheckedAt, and profileStatuses. Only send a user-facing message if the effective model changed since last check.\n5) If no change, stay silent.\n\nThis is a periodic model failover monitor/reminder job.",
    "timeoutSeconds": 120
  },
  "delivery": {
    "mode": "none"
  },
  "state": {
    "nextRunAtMs": <now-epoch-ms + 600000>,
    "lastRunAtMs": null,
    "lastStatus": null,
    "lastDurationMs": null,
    "consecutiveErrors": 0
  }
}
```

- **`everyMs: 600000`** — Runs every 10 minutes
- **`sessionTarget: "isolated"`** — Runs in its own session, not the main chat
- **`delivery.mode: "none"`** — Silent unless the job itself sends a message
- Replace `<generate-uuid>` with a real UUID (`uuidgen` or `node -e "console.log(require('crypto').randomUUID())"`)
- Replace `<now-epoch-ms>` with current time in ms (`date +%s000` or `node -e "console.log(Date.now())"`)

- Replace `<workspace>` with your actual workspace path
- List all your auth profile names in the message so the cron agent knows what to check

## Quick Setup Checklist

1. Install codex CLI: `npm i -g @openai/codex`
2. Run `./scripts/codex-add-profile.sh <name>` for each OpenAI account
3. Add profile declarations to `openclaw.json` `auth.profiles` and `auth.order`
4. Add model fallback config to `openclaw.json` `agents.defaults.model`
5. Add the cron job to `cron/jobs.json`
6. Verify: `openclaw models status`
