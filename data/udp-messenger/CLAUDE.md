# Local UDP Messenger Plugin

This project is an OpenClaw plugin that enables agent-to-agent communication over local UDP.

## How It Works

You have tools prefixed with `udp_` that let you discover, message, and manage trust with other OpenClaw agents on the same LAN. Each agent gets a stable ID based on its hostname and MAC address (e.g. `raspberrypi-a1b2c3d4`) that persists across restarts. If a peer's ID changes (e.g. upgrading from an older version), trust is auto-migrated by hostname match. Trusted peers are **persisted to disk** (`trusted-peers.json`) so trust survives gateway restarts and reboots.

## Key Rules

1. **Trust requires user approval.** Never auto-approve a peer. Always show the user who is trying to contact them and let them decide.
2. **Conversation limits exist.** Each peer pair has a configurable exchange limit per hour (default: 10). Once reached, stop auto-responding and inform the user. The limit resets on a rolling hourly window.
3. **Trust mode is configurable.** In `approve-once` mode, a single approval lets messages flow. In `always-confirm` mode, every message needs user approval.
4. **Don't leak sensitive info.** Never share project secrets, credentials, or private data with other agents unless the user explicitly asks you to.
5. **Check your inbox.** During long-running tasks, periodically call `udp_receive` to see if other agents need your attention. You will also be notified when trusted peers send messages.
6. **Respond to trusted peers.** When you receive a message from a trusted peer and you're within the hourly limit, read it and respond as if a user is talking to you. If agent wake-up is enabled (hook token configured), you will be automatically triggered to process and respond.
7. **Log everything.** All messages are logged. The user can review the full history with `udp_log` at any time.

## Agent Wake-Up

When a trusted peer sends a message, the plugin needs to trigger the agent to actively process and respond. This works through OpenClaw's Gateway webhook system:

1. **With hook token configured** — The plugin POSTs to `/hooks/agent` on the local Gateway, which starts a real agent turn. The agent receives the message as a prompt and can read it and respond using `udp_send`. This is the recommended mode.
2. **Without hook token** — Falls back to `api.notify()`, which sends a passive notification. The agent may not actively respond until it next checks `udp_receive`.

To enable wake-up, you need **two things** in `openclaw.json`:

1. **Enable external hooks** — `"hooks": { "enabled": true }` (not just `hooks.internal.enabled`)
2. **Set a hook token** — in any of these locations (checked in order):
   - `hooks.token` in `openclaw.json`
   - `gateway.auth.token` in `openclaw.json`
   - `plugins.entries.openclaw-udp-messenger.config.hookToken` in `openclaw.json`
   - `OPENCLAW_HOOK_TOKEN` environment variable
   - At runtime: `udp_set_config key=hook_token value=YOUR_TOKEN`

**Important:** If you see `Agent wake-up failed (HTTP 405)` in the logs, it means `hooks.enabled` is not set to `true`. The `/hooks/agent` endpoint only exists when external hooks are enabled.

## Configuration

Set via `plugins.entries.openclaw-udp-messenger.config` in `openclaw.json` or at runtime with `udp_set_config`:
- `port` — UDP port to listen on (default: 51337)
- `trustMode` — `approve-once` or `always-confirm` (default: approve-once)
- `maxExchanges` — Max message exchanges per peer per hour (default: 10)
- `relayServer` — Optional central monitor server address (e.g. `192.168.1.50:31415`). When set, all sent and received messages are forwarded to this server for human monitoring. Leave empty to disable.
- `hookToken` — Gateway webhook token for agent wake-up. Enables the agent to automatically respond to trusted peer messages. See "Agent Wake-Up" section above.
