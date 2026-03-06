# OpenClaw secure baseline config (starting point)

This file contains a conservative baseline derived from OpenClaw’s own security guidance.

> OpenClaw config is **JSON5** in `~/.openclaw/openclaw.json` (comments + trailing commas allowed). Regular JSON also works.

## Baseline goal

- Keep the Gateway **private** (loopback)
- Require strong **Gateway auth**
- Isolate DMs and require **pairing**
- Require explicit **mention gating** in groups
- Default tools to least privilege (deny control-plane + runtime by default)

## Minimal “secure baseline” (copy/paste)

> Paste into your OpenClaw config (usually `~/.openclaw/openclaw.json`) *after* making a backup.
> Replace the token with a long random secret.

```js
{
  gateway: {
    mode: "local",
    bind: "loopback",
    port: 18789,
    auth: { mode: "token", token: "replace-with-long-random-token" },
  },
  channels: {
    whatsapp: {
      dmPolicy: "pairing",
      groups: { "*": { requireMention: true } },
    },
  },
}
```

## Hardened baseline including tool restrictions

```js
{
  gateway: {
    mode: "local",
    bind: "loopback",
    auth: { mode: "token", token: "replace-with-long-random-token" },
  },
  session: {
    dmScope: "per-channel-peer",
  },
  tools: {
    profile: "messaging",
    // Control plane + runtime tools denied by default.
    // Re-enable per trusted agent if/when needed.
    deny: [
      "group:automation", // includes gateway + cron
      "group:runtime",    // exec/bash/process
      "group:fs",         // read/write/edit/apply_patch
      "sessions_spawn",
      "sessions_send",
    ],
    fs: { workspaceOnly: true },
    exec: { security: "deny", ask: "always" },
    elevated: { enabled: false },
  },
  channels: {
    whatsapp: { dmPolicy: "pairing", groups: { "*": { requireMention: true } } },
  },
}
```

## Optional hardening extras

- Disable discovery if you don’t need local device discovery:

```js
{
  discovery: {
    mdns: { mode: "off" },
  },
}
```

- Or keep discovery but reduce information disclosure (recommended default):

```js
{
  discovery: {
    mdns: { mode: "minimal" },
  },
}
```

- Keep log redaction enabled (and let the audit auto-fix it if it’s off):

```js
{
  logging: {
    redactSensitive: true,
  },
}
```

## Notes

- If you need remote access, prefer **SSH tunnelling** or **Tailscale Serve** rather than binding the Gateway to LAN/0.0.0.0.
- After changes, rerun: `openclaw security audit --deep`.
- Avoid sharing `~/.openclaw/openclaw.json` without redaction.
