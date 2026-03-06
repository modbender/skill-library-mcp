---
name: agentbox
description: "AgentBox VM operating instructions: services, config, x402 payments, skill updates, troubleshooting. Load this at the start of every session."
metadata: {"openclaw": {"always": true}}
user-invocable: true
---

# AgentBox Operating Instructions

You are running on a dedicated AgentBox VM - a single-tenant Hetzner cloud instance with OpenClaw gateway, HTTPS, web terminal, and a Solana wallet for x402 micropayments.

## Services

| Service | Port | Managed by |
|---------|------|------------|
| OpenClaw gateway | :18789 (loopback) | `openclaw gateway restart` |
| Caddy (HTTPS reverse proxy) | :443 | `sudo systemctl restart caddy` |
| ttyd (web terminal) | :7681 (loopback) | `sudo systemctl restart ttyd` |

Caddy routes HTTPS traffic to the gateway and terminal. Do NOT modify Caddy or systemd configs directly.

## Key paths

| What | Path |
|------|------|
| OpenClaw config | `~/.openclaw/openclaw.json` |
| Solana wallet | `~/.openclaw/agentbox/wallet-sol.json` |
| Workspace | `~/.openclaw/workspace/` |
| Skills | `~/.openclaw/workspace/skills/` |
| x402 plugin | `~/.openclaw/extensions/openclaw-x402/` |
| Gateway logs | `~/.openclaw/logs/` |

## x402 payment plugin

The `openclaw-x402` plugin patches `globalThis.fetch` to handle HTTP 402 Payment Required responses automatically. When an LLM inference call returns 402, the plugin signs a USDC payment on Solana and retries. This is transparent - you don't need to do anything special.

The wallet at `~/.openclaw/agentbox/wallet-sol.json` must have USDC balance for payments to work. Check balance with:
```bash
spl-token balance --owner $(solana address) EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v
```

## Default model provider

This instance comes with a preconfigured LLM provider (blockrun) that uses x402 for payments. If users want to use a different provider like OpenRouter, use the `/agentbox-openrouter` skill.

## Restarting the gateway

After any config change to `~/.openclaw/openclaw.json`:
```bash
openclaw gateway restart
```

Check status:
```bash
openclaw status
```

## Updating skills

To get the latest AgentBox skills:
```bash
clawhub update --all
```

This updates all installed skills from ClawHub. Changes take effect on the next new session.

## Troubleshooting

- **Gateway won't start**: Check `openclaw status` and gateway logs at `~/.openclaw/logs/`
- **x402 payments failing**: Check USDC balance (see above). Wallet needs USDC on Solana mainnet.
- **Config changes not taking effect**: Run `openclaw gateway restart` after editing `~/.openclaw/openclaw.json`
- **Skills not showing**: Run `clawhub list` to see installed skills. Run `clawhub update --all` to refresh.

## Important rules

- Always use `openclaw gateway restart` to restart the gateway. Never use systemctl directly for the gateway.
- When editing `~/.openclaw/openclaw.json`, read the current file first, modify it, write it back. Don't write partial configs.
- The Solana wallet private key is at `~/.openclaw/agentbox/wallet-sol.json`. Never share it or display it to users.
