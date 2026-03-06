# Gateway Configuration Reference

## Table of Contents

- [Gateway Core](#gateway-core)
- [Auth](#auth)
- [Tailscale](#tailscale)
- [Control UI](#control-ui)
- [Remote Gateway](#remote-gateway)
- [Hot Reload](#hot-reload)
- [OpenAI-Compatible Endpoints](#openai-compatible-endpoints)
- [Multi-Instance Isolation](#multi-instance-isolation)

## Gateway Core

```json5
{
  gateway: {
    mode: "local", // local | remote
    port: 18789,
    bind: "loopback", // auto | loopback | lan | tailnet | custom
    controlUi: { enabled: true, basePath: "/openclaw" },
    auth: {
      mode: "token",
      token: "${OPENCLAW_GATEWAY_TOKEN}",
      allowTailscale: true,
    },
    tailscale: { mode: "serve", resetOnExit: false },
    remote: { url: "ws://gateway.tailnet:18789", token: "remote-token" },
    reload: { mode: "hybrid", debounceMs: 300 },
    trustedProxies: ["10.0.0.1"],
    tools: {
      deny: ["browser"],
      allow: ["gateway"],
    },
  },
}
```

- `mode`: `local` (run gateway) or `remote` (connect to remote gateway). Gateway refuses to start unless `local`.
- `port`: single multiplexed port for WS + HTTP. Precedence: `--port` > `OPENCLAW_GATEWAY_PORT` > `gateway.port` > `18789`.
- `bind`: `auto`, `loopback` (default), `lan` (`0.0.0.0`), `tailnet` (Tailscale IP only), or `custom`.

**Important:** `tailscale.mode: "serve"` requires `bind: "loopback"` — Tailscale serve handles external exposure.

## Auth

```json5
{
  gateway: {
    auth: {
      mode: "token", // token | password
      token: "${OPENCLAW_GATEWAY_TOKEN}",
      // password: "${OPENCLAW_GATEWAY_PASSWORD}",
      allowTailscale: true,
      rateLimit: {
        maxAttempts: 10,
        windowMs: 60000,
        lockoutMs: 300000,
        exemptLoopback: true,
      },
    },
  },
}
```

- Required by default. Non-loopback binds require a shared token/password.
- `allowTailscale: true`: Tailscale Serve identity headers satisfy auth (verified via `tailscale whois`). Defaults to `true` when `tailscale.mode = "serve"`.
- `rateLimit`: per client IP and per auth scope. Blocked attempts return `429` + `Retry-After`.

## Tailscale

```json5
{
  gateway: {
    tailscale: {
      mode: "off", // off | serve | funnel
      resetOnExit: false,
    },
  },
}
```

- `serve`: tailnet only, requires `bind: "loopback"`.
- `funnel`: public, requires auth.

## Control UI

```json5
{
  gateway: {
    controlUi: {
      enabled: true,
      basePath: "/openclaw",
      root: "",
      allowInsecureAuth: false,
      dangerouslyDisableDeviceAuth: false,
    },
  },
}
```

Accessible at `http://127.0.0.1:<port><basePath>/`.

## Remote Gateway

For nodes connecting TO a remote gateway:

```json5
{
  gateway: {
    mode: "remote",
    remote: {
      url: "wss://sallvain.tailaa9d14.ts.net",
      transport: "direct", // ssh | direct
      token: "${OPENCLAW_GATEWAY_TOKEN}",
      password: "${OPENCLAW_GATEWAY_PASSWORD}",
    },
  },
}
```

- `transport`: `ssh` (default) or `direct` (ws/wss).
- `remote.token` is for remote CLI calls only; does not enable local gateway auth.

## Hot Reload

The Gateway watches `~/.openclaw/openclaw.json` and applies changes automatically.

```json5
{
  gateway: {
    reload: {
      mode: "hybrid", // hybrid | hot | restart | off
      debounceMs: 300,
    },
  },
}
```

| Mode | Behavior |
|------|----------|
| `hybrid` (default) | Hot-applies safe changes, auto-restarts for critical ones |
| `hot` | Hot-applies safe changes only, logs warning when restart needed |
| `restart` | Restarts on any config change |
| `off` | Disables file watching |

### What needs a restart

| Category | Restart needed? |
|----------|----------------|
| Channels, agents, models, routing | No |
| Hooks, cron, heartbeat | No |
| Sessions, messages, tools, media | No |
| UI, logging, identity, bindings | No |
| Gateway server (port, bind, auth, tailscale) | **Yes** |
| Discovery, canvasHost, plugins | **Yes** |

## OpenAI-Compatible Endpoints

```json5
{
  gateway: {
    http: {
      endpoints: {
        chatCompletions: { enabled: true },
        responses: {
          enabled: true,
          maxUrlParts: 10,
          files: { urlAllowlist: ["*"] },
          images: { urlAllowlist: ["*"] },
        },
      },
    },
  },
}
```

## Multi-Instance Isolation

Run multiple gateways on one host:

```bash
OPENCLAW_CONFIG_PATH=~/.openclaw/a.json \
OPENCLAW_STATE_DIR=~/.openclaw-a \
openclaw gateway --port 19001
```

Convenience flags: `--dev` (port `19001`), `--profile <name>`.

- Minimum **20-port spacing** required between instances for derived ports.
- Derived port mappings: browser control at base+2, CDP at controlPort+9 through +108.
- `browser.cdpUrl` must not be pinned to same values on multiple instances.
- `browser.profiles.<name>.cdpPort` and `browser.profiles.<name>.cdpUrl` need per-instance separation.

## Troubleshooting

- `gateway.auth.token` is the correct key. Legacy `gateway.token` does **not** work as a replacement.
- `gateway.remote.url` CLI override doesn't fall back to stored credentials.
- Config permissions should be `600`.
- Podman deployment path: `~openclaw/.openclaw/openclaw.json`.
- Legacy config key migrations prevent other commands from running until `openclaw doctor` runs.
- WhatsApp auth is intentionally only migrated via `openclaw doctor`.

### Doctor

`openclaw doctor` validates and repairs configuration.

| Flag | Behavior |
|------|----------|
| `--yes` | Auto-approve non-destructive repairs |
| `--repair` | Attempt all repairs |
| `--repair --force` | Force-repair even when uncertain |
| `--non-interactive` | Skip refresh attempts and confirmation prompts |
| `--deep` | Extended validation checks |
| `--generate-gateway-token` | Generate a new gateway auth token |

**Checks performed:**
- Config file permissions (600) with security warning.
- Legacy config key migrations (e.g. `routing.allowFrom` -> `channels.whatsapp.allowFrom`, `routing.groupChat.*` -> `messages.groupChat.*`, `routing.queue` -> `messages.queue`, `routing.bindings` -> `bindings`, `routing.agents` -> `agents.list`).
- Multiple state directories cause history splitting warning.
- `models.providers.opencode` override warning for removable overrides.
- Runtime: Node.js required (Bun warning, version-manager paths flagged).
