# agent-wallet-nwc-bridge

Nostr Wallet Connect (NIP-47) bridge that exposes a local **@moneydevkit/agent-wallet** instance as an NWC wallet-service.

This is used to connect Stacker.News (or any NWC client) to a self-custodial local Lightning wallet.

## Support / donate

If this project is useful, you can send sats to:

- Lightning Address: **`liene@stacker.news`**
- Stacker.News profile (zap/donate): https://stacker.news/liene
- Some wallets also support the `lightning:` URI: `lightning:liene@stacker.news`

## What it does

- Listens on one or more Nostr relays for NWC requests (kind `23194`).
- Decrypts requests (nip04 / nip44_v2 depending on connection).
- Executes the requested wallet method by calling `npx @moneydevkit/agent-wallet ...`.
- Responds with NWC responses (kind `23195`).

## Files

- `index.js` — the bridge
- `nwc.env` — runtime config (relays, state path)
- `state.json` — **runtime state + secrets** (NWC connection secrets)
- `agent-wallet-nwc-bridge.service` — systemd *user* service unit
- `install_systemd_user.sh` — helper installer for the user service

## Install / run (systemd user service)

```bash
cd ~/agent-wallet-nwc-bridge

# install dependencies
npm install

# env file
cp -n nwc.env.example nwc.env
# note: by default NWC_STATE is relative ("state.json") so the service is portable

# install + start user service
./install_systemd_user.sh

# follow logs
journalctl --user -u agent-wallet-nwc-bridge.service -f
```

## CLI usage

Initialize fresh state (example):

```bash
cd ~/agent-wallet-nwc-bridge
node index.js init --relay wss://nos.lol
```

Run in foreground:

```bash
node index.js run
```

## Notes / gotchas

- If you change `index.js`, `nwc.env`, or `state.json`, restart the service:
  ```bash
  systemctl --user restart agent-wallet-nwc-bridge.service
  ```
- `state.json` contains NWC secrets; treat it like wallet credentials.

## Git hygiene (recommended)

Do **not** commit secrets or bulky deps:

- `nwc.env`
- `state.json`
- `state.json.bak.*`
- `node_modules/`

Add them to `.gitignore`.
