---
name: "@emotion-machine/claw-messenger"
description: iMessage, RCS & SMS channel plugin for OpenClaw — no phone or Mac
  Mini required.
---

# @emotion-machine/claw-messenger

iMessage, RCS & SMS channel plugin for [OpenClaw](https://openclaw.ai) — no phone or Mac Mini required.

| | |
|---|---|
| **Publisher** | [Emotion Machine](https://emotionmachine.ai) |
| **Homepage** | [clawmessenger.com](https://clawmessenger.com) |
| **Source code** | [github.com/emotion-machine-org/claw-messenger](https://github.com/emotion-machine-org/claw-messenger) |
| **npm** | [@emotion-machine/claw-messenger](https://www.npmjs.com/package/@emotion-machine/claw-messenger) |
| **Issues** | [GitHub Issues](https://github.com/emotion-machine-org/claw-messenger/issues) |
| **Privacy policy** | [clawmessenger.com/privacy](https://clawmessenger.com/privacy) |
| **Pricing** | [clawmessenger.com/pricing](https://clawmessenger.com/pricing) |

## How It Works

Claw Messenger routes messages between your OpenClaw agent and iMessage/RCS/SMS networks. The plugin connects to the Claw Messenger relay server over a WebSocket and authenticates with your API key. The relay server handles carrier-level delivery and inbound routing, then forwards messages back to your agent in real time.

```
OpenClaw Agent  ←→  Plugin (local)  ←→  Relay Server (WSS)  ←→  iMessage / RCS / SMS
```

## Required Credentials

This plugin requires **one credential**: a Claw Messenger API key.

| Property | Value |
|----------|-------|
| **Key format** | `cm_live_{tag}_{secret}` |
| **Obtain from** | [clawmessenger.com/dashboard](https://clawmessenger.com/dashboard) |
| **Sensitivity** | **Secret** — treat like a password. Do not commit to version control. |
| **Storage location** | Stored locally in `.openclaw.json` at `channels.claw-messenger.apiKey` |
| **Rotation** | Revoke and rotate at any time from the [dashboard](https://clawmessenger.com/dashboard) |
| **Scope** | Authorizes sending and receiving messages on your account only |

No other credentials, environment variables, or secrets are required.

## Required Config Path

All plugin configuration is stored in a single location:

**`.openclaw.json` → `channels.claw-messenger`**

This is the only file the plugin reads or writes. The full config schema is documented in the [Configuration Reference](#configuration-reference) below and declared in the plugin manifest (`openclaw.plugin.json` → `configSchema`).

## External Connections

The plugin makes exactly one external connection:

| Property | Value |
|----------|-------|
| **Host** | `claw-messenger.onrender.com` |
| **Protocol** | `wss://` (TLS-encrypted WebSocket) |
| **Purpose** | Relay server that bridges OpenClaw to iMessage/RCS/SMS carrier networks |
| **Hosting** | Hosted on [Render](https://render.com) (managed cloud platform) by Emotion Machine. The `onrender.com` subdomain is standard for Render deployments. |
| **Data handling** | Stateless bridge — message content passes through in transit but is not persisted on the relay server. Message metadata (sender, recipient, timestamps) is logged for delivery tracking and billing per the [Privacy Policy](https://clawmessenger.com/privacy). |
| **Custom domain** | If your organization requires a custom domain or self-hosted deployment, contact hello@emotionmachine.ai |

No other external connections are made.

## Plugin Manifest Summary

The plugin's `openclaw.plugin.json` manifest declares the following (reproduced here for transparency):

- **Required credentials:** `apiKey` (marked `sensitive: true`, placeholder `cm_live_...`)
- **Config path:** `.openclaw.json` → `channels.claw-messenger`
- **External connection:** `wss://claw-messenger.onrender.com` (relay server)
- **Config schema:** `apiKey` (required string), `serverUrl` (optional string), `preferredService` (optional enum), `dmPolicy` (optional enum), `allowFrom` (optional array)

All credentials and config paths used at runtime are declared in the manifest. There are no undeclared secrets, env vars, or config files.

## Install

```bash
openclaw plugins install @emotion-machine/claw-messenger
```

The package is published to npm as [`@emotion-machine/claw-messenger`](https://www.npmjs.com/package/@emotion-machine/claw-messenger). You can verify the package contents before installing:

```bash
npm pack @emotion-machine/claw-messenger --dry-run
```

## Configuration

After installing, add the plugin to your OpenClaw config (`.openclaw.json`) under `channels`:

```json5
{
  "channels": {
    "claw-messenger": {
      "enabled": true,
      "apiKey": "cm_live_XXXXXXXX_YYYYYYYYYYYYYY",  // required — your API key
      "serverUrl": "wss://claw-messenger.onrender.com",  // default relay server
      "preferredService": "iMessage",  // "iMessage" | "RCS" | "SMS"
      "dmPolicy": "pairing",           // "open" | "pairing" | "allowlist"
      "allowFrom": ["+15551234567"]    // only used with "allowlist" policy
    }
  }
}
```

### Configuration Reference

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `apiKey` | **Yes** | — | Your `cm_live_*` API key. Stored locally in `.openclaw.json`. |
| `serverUrl` | No | `wss://claw-messenger.onrender.com` | WebSocket relay server URL. |
| `preferredService` | No | `iMessage` | Default delivery service (`iMessage`, `RCS`, or `SMS`). |
| `dmPolicy` | No | `pairing` | Inbound DM policy: `open`, `pairing`, or `allowlist`. |
| `allowFrom` | No | `[]` | Phone numbers to accept when using `allowlist` policy. |

## Security & Privacy

- Your `cm_live_*` API key is a **secret credential**. Add `.openclaw.json` to `.gitignore` to avoid committing it to version control.
- You can revoke and rotate API keys at any time from the [dashboard](https://clawmessenger.com/dashboard). We recommend starting with a scoped or test key.
- All connections use **TLS-encrypted WebSockets** (`wss://`). Message content is not stored on the relay server.
- Message metadata (sender, recipient, timestamps) is logged for delivery tracking and billing. See the [Privacy Policy](https://clawmessenger.com/privacy).
- Billing is based on monthly message volume. See [Pricing](https://clawmessenger.com/pricing) for plans and limits.

## Features

- **Send & receive** text messages and media (images, video, audio, documents)
- **iMessage reactions** — love, like, dislike, laugh, emphasize, question (tapback)
- **Group chats** — send to existing groups or create new ones
- **Typing indicators** — sent and received
- **DM security policies** — open, pairing-based approval, or allowlist

## Agent Tools

The plugin registers two tools your agent can call:

| Tool | Description |
|------|-------------|
| `claw_messenger_status` | Check connection status, server URL, and preferred service |
| `claw_messenger_switch_service` | Switch the preferred messaging service at runtime |

## Slash Commands

| Command | Description |
|---------|-------------|
| `/cm-status` | Show connection state, server URL, and preferred service |
| `/cm-switch <service>` | Switch preferred service (`iMessage`, `RCS`, or `SMS`) |

## Getting Started

1. **Sign up** at [clawmessenger.com](https://clawmessenger.com)
2. **Create an API key** from the [dashboard](https://clawmessenger.com/dashboard)
3. **Install the plugin:** `openclaw plugins install @emotion-machine/claw-messenger`
4. **Add the config** above with your API key (keep `.openclaw.json` out of version control)
5. **Start a conversation** — your agent can now send and receive messages

## Support

- **Issues:** [github.com/emotion-machine-org/claw-messenger/issues](https://github.com/emotion-machine-org/claw-messenger/issues)
- **Email:** hello@emotionmachine.ai
- **Docs:** [clawmessenger.com/docs](https://clawmessenger.com/docs)

## License

UNLICENSED
