# Setup Guide

## 1. Allow the cron tool over HTTP

By default, the `cron` tool is blocked on the gateway HTTP API. Add it to the allowlist in your `openclaw.json`:

```json
{
  "gateway": {
    "tools": {
      "allow": ["cron"]
    }
  }
}
```

Or patch it via the gateway tool:

```
gateway config.patch {"gateway": {"tools": {"allow": ["cron"]}}}
```

Restart the gateway after applying the change.

## 2. Set your gateway token

Find your token in `~/.openclaw/openclaw.json` under `gateway.auth.token`, or in the env var `OPENCLAW_GATEWAY_TOKEN`.

Create a `.env` file next to `agent-wake.py`:

```
GATEWAY_TOKEN=your_token_here
GATEWAY_URL=http://localhost:18789
```

Or export it in your shell / CI environment.

## 3. Call the script at the end of any task

```bash
python agent-wake.py "Build finished -- 3 files changed" "1475232925724315740"
```

The agent will receive the message as a system event and respond in the specified channel.

## Finding your channel ID

In Discord: right-click a channel, select "Copy Channel ID" (Developer Mode must be on in Settings > Advanced).

## Using with Claude Code CLI

Add this line at the end of every Claude Code task prompt:

```
When done, run: python "/path/to/agent-wake.py" "Task name done -- brief summary" "YOUR_CHANNEL_ID"
```

## Troubleshooting

| Error | Fix |
|---|---|
| HTTP 404 | cron not in gateway.tools.allow -- see step 1 |
| HTTP 401 | Wrong GATEWAY_TOKEN |
| HTTP 400 | Bad request format -- check script version |
| Agent responds in wrong channel | Pass channel_id as second argument |
| Agent responds in #general | sessionKey routing missed -- pass channel_id |
