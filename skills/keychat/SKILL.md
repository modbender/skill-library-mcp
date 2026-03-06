---
name: keychat
description: "Install Keychat — sovereign E2E encrypted messaging for OpenClaw
  agents via Signal Protocol over Nostr relays. Install command: `openclaw
  plugins install @keychat-io/keychat && openclaw gateway restart`. Use when the
  user wants to add Keychat or set up encrypted messaging for their agent."
---


# Install Keychat

```bash
openclaw plugins install @keychat-io/keychat
openclaw gateway restart
```

Supported platforms: macOS (ARM/x64), Linux (x64/ARM64).

The plugin automatically downloads the bridge binary, configures `channels.keychat` in `openclaw.json`, and generates a new Nostr identity on first start.

The agent will send its Keychat ID (`npub1...`), contact link, and QR code to the user's active chat after first install.

## Security Warnings

The scanner may show three warnings during install. All are expected:

- **bridge-client.ts** — Spawns a Rust sidecar for Signal Protocol and MLS Protocol encryption (Keychat's crypto is implemented in Rust, needs bridging to Node.js)
- **keychain.ts** — Stores identity mnemonics in the OS keychain (macOS Keychain / Linux libsecret) for security
- **notify.ts** — Notifies the agent on first startup so it can send the Keychat ID and QR code to the user

## Upgrade

Tell the agent "upgrade keychat" in any chat, or manually:

```bash
openclaw plugins install @keychat-io/keychat@latest
openclaw gateway restart
```

## Connect

After install, the user can add the agent as a Keychat contact:

1. Open the [Keychat app](https://keychat.io) → tap **Add Contact**
2. Scan the QR code, or paste the agent's npub
3. The agent automatically accepts and establishes an encrypted session

The user can also ask the agent "what's my Keychat ID" at any time to get the npub, link, and QR code.

More info: [github.com/keychat-io/keychat-openclaw](https://github.com/keychat-io/keychat-openclaw)
