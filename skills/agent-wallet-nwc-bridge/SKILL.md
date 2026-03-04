---
name: agent-wallet-nwc-bridge
version: 0.1.0
description: Expose a local @moneydevkit/agent-wallet as a Nostr Wallet Connect (NIP-47) wallet-service (systemd user service).
repo: https://github.com/kristapsk/agent-wallet-nwc-bridge
---

# agent-wallet-nwc-bridge (skill)

This skill provides a small, self-hosted **Nostr Wallet Connect (NIP-47)** bridge that lets an NWC client (e.g. Stacker.News) send `make_invoice` / `pay_invoice` requests to a local **@moneydevkit/agent-wallet**.

It is intended to be run as a **systemd user service**.

## What you get

- `index.js` bridge implementation
- portable `agent-wallet-nwc-bridge.service` unit (uses `%h`)
- installer script `install_systemd_user.sh`
- env + state files (`nwc.env`, `state.json`) stored locally (not committed)

## Requirements

- Linux with systemd user services
- Node.js + npm
- Nostr relay access (default example uses `wss://nos.lol`)

## Install

```bash
git clone https://github.com/kristapsk/agent-wallet-nwc-bridge
cd agent-wallet-nwc-bridge

npm install
cp -n nwc.env.example nwc.env

# initialize state + create wallet service pubkey
node index.js init --relay wss://nos.lol

# install + start as user service
./install_systemd_user.sh

# follow logs
journalctl --user -u agent-wallet-nwc-bridge.service -f
```

## Configure

Edit `nwc.env`:

- `NWC_RELAYS` — comma-separated relay list (e.g. `wss://nos.lol,wss://relay.damus.io`)
- `NWC_STATE` — defaults to `state.json` (relative to WorkingDirectory)
- `NWC_AUTO_REGISTER` — `0` recommended (use explicit URIs/permissions)
- `NWC_DEFAULT_BUDGET_SATS` — default spending cap when generating URIs

**Security note:** `state.json` contains NWC connection secrets. Do not commit it.

## Typical usage flow (Stacker.News)

1. Run the bridge.
2. Generate an NWC URI for *receive* and attach it in SN wallets UI.
3. Generate a separate NWC URI for *send* (spending permission) and attach it.
4. Verify end-to-end:
   - SN `make_invoice` requests appear in bridge logs
   - SN `pay_invoice` requests appear and result in a paid invoice

## Operations

Restart after changes:

```bash
systemctl --user restart agent-wallet-nwc-bridge.service
```

Disable:

```bash
systemctl --user disable --now agent-wallet-nwc-bridge.service
```

## Publishing to ClawHub

- Ensure `README.md`, `SKILL.md`, and `package.json` are present.
- Keep secrets out of git (`nwc.env`, `state.json`, `node_modules/` are ignored by default).
