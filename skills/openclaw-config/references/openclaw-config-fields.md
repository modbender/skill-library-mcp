# OpenClaw Config Field Index (openclaw.json)

Reference source version: `openclaw/openclaw@875324e` (2026-02-07). Fields can change across versions, so prefer `config.schema` from the running Gateway when possible.

Config file: `~/.openclaw/openclaw.json` (JSON5)
- Override path via `OPENCLAW_CONFIG_PATH`
- Split config via `$include` (semantics in `src/config/includes.ts`)

## Root Keys (OpenClawSchema)

The root object is strict; aside from `$include` preprocessing, unknown keys fail validation.

- `meta`: metadata written by the system (`lastTouchedVersion`, `lastTouchedAt`)
- `env`: shell env import + env var sugar (string catchall)
- `wizard`: wizard run metadata
- `diagnostics`: diagnostics/otel/cacheTrace
- `logging`: log level/output/redaction
- `update`: update channel + check-on-start
- `browser`: Browser/CDP settings
- `ui`: UI styling + assistant name/avatar
- `auth`: auth profiles/order/cooldowns
- `models`: model providers/definitions
- `nodeHost`: node host settings (currently includes browserProxy)
- `agents`: agents.defaults + agents.list
- `tools`: global tool policy + exec/web/media/links
- `bindings`: route channel/account/peer to agents
- `broadcast`: broadcast strategy + peer->agentId mapping
- `audio`: audio settings (e.g., transcription)
- `media`: media pipeline settings (e.g., preserveFilenames)
- `messages`: message behavior/prefixing (see session schema)
- `commands`: chat command settings (see session schema)
- `approvals`: approvals policy (see approvals schema)
- `session`: session policy (see session schema)
- `cron`: cron store/concurrency
- `hooks`: hooks server + gmail/internal mappings
- `web`: web socket/reconnect settings
- `channels`: channel providers (whatsapp/telegram/discord/slack/...)
- `discovery`: mdns/wideArea
- `canvasHost`: Canvas Host
- `talk`: talk/TTS shortcuts
- `gateway`: gateway service/auth/remote/tls/http endpoints/nodes
- `memory`: memory backend/citations/qmd
- `skills`: skills loading/install/entries
- `plugins`: plugins loading/entries/installs

## gateway (Commonly Edited Keys)

Source: `gateway` section in `src/config/zod-schema.ts`.

- `gateway.port`: number
- `gateway.mode`: `"local" | "remote"`
- `gateway.bind`: `"auto" | "lan" | "loopback" | "custom" | "tailnet"`
- `gateway.controlUi`:
  - `enabled`, `basePath`, `root`, `allowedOrigins`
  - `allowInsecureAuth`, `dangerouslyDisableDeviceAuth`
- `gateway.auth`:
  - `mode`: `"token" | "password"`
  - `token`, `password`, `allowTailscale`
- `gateway.trustedProxies`: string[]
- `gateway.tailscale`: `{ mode: "off" | "serve" | "funnel", resetOnExit }`
- `gateway.remote`:
  - `url`, `transport`: `"ssh" | "direct"`
  - `token`, `password`, `tlsFingerprint`
  - `sshTarget`, `sshIdentity`
- `gateway.reload`: `{ mode: "off" | "restart" | "hot" | "hybrid", debounceMs }`
- `gateway.tls`: `{ enabled, autoGenerate, certPath, keyPath, caPath }`
- `gateway.http.endpoints`:
  - `chatCompletions.enabled`
  - `responses.enabled`, `responses.maxBodyBytes`
  - `responses.files` / `responses.images` (allowUrl/allowedMimes/maxBytes/maxRedirects/timeoutMs, etc.)
- `gateway.nodes`:
  - `browser.mode`: `"auto" | "manual" | "off"`
  - `browser.node`: string
  - `allowCommands`, `denyCommands`: string[]

## skills / plugins (Install + Entries)

Source: `skills` / `plugins` sections in `src/config/zod-schema.ts`.

`skills`:
- `skills.allowBundled`: string[]
- `skills.load`: `{ extraDirs, watch, watchDebounceMs }`
- `skills.install`: `{ preferBrew, nodeManager: "npm"|"pnpm"|"yarn"|"bun" }`
- `skills.entries.<id>`:
  - `enabled`: boolean
  - `apiKey`: string
  - `env`: record<string,string>
  - `config`: record<string,unknown>

`plugins`:
- `plugins.enabled`: boolean
- `plugins.allow` / `plugins.deny`: string[]
- `plugins.load.paths`: string[]
- `plugins.slots.memory`: string
- `plugins.entries.<id>`: `{ enabled, config }`
- `plugins.installs.<id>`:
  - `source`: `"npm" | "archive" | "path"`
  - `spec`, `sourcePath`, `installPath`, `version`, `installedAt`

## channels / models / agents / tools (Use Schema Files)

These sections are large and can change quickly; locate keys via schema files instead of guessing:

- `channels`: `src/config/zod-schema.providers.ts` + `src/config/zod-schema.providers-core.ts`
  - Note: `channels` is passthrough (allows extension channel keys)
  - But each provider object (telegram/discord/slack/...) is usually strict
- `models`: `ModelsConfigSchema` in `src/config/zod-schema.core.ts`
- `agents`: `src/config/zod-schema.agents.ts` / `src/config/zod-schema.agent-defaults.ts` / `src/config/zod-schema.agent-runtime.ts`
- `tools`: `ToolsSchema` in `src/config/zod-schema.agent-runtime.ts`
