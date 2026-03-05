# Environment, Providers, and Misc Configuration

## Table of Contents

- [Environment Variables](#environment-variables)
- [Env Var Substitution](#env-var-substitution)
- [Custom Providers](#custom-providers)
- [Provider Examples](#provider-examples)
- [Auth Storage](#auth-storage)
- [Skills](#skills)
- [Plugins](#plugins)
- [Browser](#browser)
- [Hooks](#hooks)
- [Cron](#cron)
- [Discovery](#discovery)
- [Canvas Host](#canvas-host)
- [UI](#ui)
- [Logging](#logging)
- [Memory](#memory)
- [Wizard](#wizard)
- [Update](#update)
- [Meta](#meta)
- [Bridge (Removed)](#bridge-removed)
- [Config Includes](#config-includes)

## Environment Variables

```json5
{
  env: {
    OPENROUTER_API_KEY: "sk-or-...",
    vars: { GROQ_API_KEY: "gsk-..." },
    shellEnv: {
      enabled: true,
      timeoutMs: 15000,
    },
  },
}
```

- `OPENCLAW_HOME`: override the home directory used for all internal path resolution.
- `OPENCLAW_LOAD_SHELL_ENV=1`: equivalent to `shellEnv.enabled: true`.
- `OPENCLAW_SHELL_ENV_TIMEOUT_MS`: equivalent to `shellEnv.timeoutMs`.
- Inline env vars only applied if process env is missing the key.
- `.env` files: CWD `.env` + `~/.openclaw/.env` (neither overrides existing vars).
- `shellEnv`: imports missing keys from login shell profile.
- **Full precedence order** (never override existing values): 1) process env, 2) CWD `.env`, 3) global `~/.openclaw/.env`, 4) config `env` block, 5) optional login-shell import (`shellEnv`).

## Env Var Substitution

Reference env vars in any config string with `${VAR_NAME}`:

```json5
{
  gateway: { auth: { token: "${OPENCLAW_GATEWAY_TOKEN}" } },
}
```

- Only uppercase names: `[A-Z_][A-Z0-9_]*`.
- Missing/empty vars throw error at load.
- Works inside `$include` files.

## Custom Providers

```json5
{
  models: {
    mode: "merge", // merge | replace
    providers: {
      "custom-proxy": {
        baseUrl: "http://localhost:4000/v1",
        apiKey: "${LITELLM_KEY}",
        authHeader: "Authorization", // custom auth header name
        headers: { "X-Custom": "value" },
        api: "openai-completions", // openai-completions | openai-responses | anthropic-messages | google-generative-ai
        models: [
          {
            id: "llama-3.1-8b",
            name: "Llama 3.1 8B",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 128000,
            maxTokens: 32000,
          },
        ],
      },
    },
  },
}
```

- `mode`: `merge` (default, adds to built-in providers) or `replace` (only use custom providers).
- **Local model caveats:** Avoid small/heavily-quantized models for prompt-injection risk. Keep models pre-loaded to avoid cold-start latency. Local setups bypass provider-side filters; maintain narrow agent scope.
- Compatible proxies: vLLM, LiteLLM, OAI-proxy (in addition to LM Studio, Ollama).

## Provider Examples

### Cerebras (GLM 4.6/4.7)
```json5
{
  models: {
    providers: {
      cerebras: {
        baseUrl: "https://api.cerebras.ai/v1",
        apiKey: "${CEREBRAS_API_KEY}",
        api: "openai-completions",
        models: [
          { id: "zai-glm-4.7", name: "GLM 4.7 (Cerebras)" },
          { id: "zai-glm-4.6", name: "GLM 4.6 (Cerebras)" },
        ],
      },
    },
  },
}
```

### Z.AI (GLM-4.7)
Set `ZAI_API_KEY`. Shortcut: `openclaw onboard --auth-choice zai-api-key`.

### MiniMax M2.1
```json5
{
  models: {
    providers: {
      minimax: {
        baseUrl: "https://api.minimax.io/anthropic",
        apiKey: "${MINIMAX_API_KEY}",
        api: "anthropic-messages",
        models: [{ id: "MiniMax-M2.1", name: "MiniMax M2.1" }],
      },
    },
  },
}
```

### Moonshot (Kimi)
```json5
{
  models: {
    providers: {
      moonshot: {
        baseUrl: "https://api.moonshot.ai/v1",
        apiKey: "${MOONSHOT_API_KEY}",
        api: "openai-completions",
        models: [{ id: "kimi-k2.5", name: "Kimi K2.5", contextWindow: 256000 }],
      },
    },
  },
}
```

### LM Studio (local)
```json5
{
  models: {
    providers: {
      lmstudio: {
        baseUrl: "http://127.0.0.1:1234/v1",
        apiKey: "lmstudio",
        api: "openai-responses",
        models: [{ id: "minimax-m2.1-gs32", name: "MiniMax M2.1 GS32" }],
      },
    },
  },
}
```

## Auth Storage

```json5
{
  auth: {
    profiles: {
      "anthropic:me@example.com": { provider: "anthropic", mode: "oauth", email: "me@example.com" },
      "anthropic:work": { provider: "anthropic", mode: "api_key" },
    },
    order: {
      anthropic: ["anthropic:me@example.com", "anthropic:work"], // OAuth before API keys in round-robin
    },
    cooldowns: {
      billingBackoffHours: 5, // starting billing backoff
      billingBackoffHoursByProvider: {}, // per-provider billing backoff override map
      billingMaxHours: 24, // max billing cooldown cap
      failureWindowHours: 24, // before backoff counters reset
    },
  },
}
```

**Auth profile credential types:**
- `api_key`: fields `type`, `provider`, `key`.
- `oauth`: fields `type`, `provider`, `access`, `refresh`, `expires`, `email`, `projectId`, `enterpriseUrl`, `accountId`.

**Cooldown backoff schedule:** 1m, 5m, 25m, 1h cap. Billing failures use longer disables vs short cooldowns.

**Usage stats** (`auth-profiles.json`): `lastUsed`, `cooldownUntil`, `disabledUntil`, `disabledReason`, `errorCount`.

- Format/invalid-request errors trigger failover same as rate limits.
- User-pinned profiles via `/model ...@<profileId>` syntax locks to a specific profile for the session.
- `OPENROUTER_API_KEY` env var: fallback for OpenRouter provider scanning.
- OAuth expiry warnings within 24 hours of token expiration.

**OAuth details:**
- Legacy import from `~/.openclaw/credentials/oauth.json` (one-time).
- Runtime cache: `~/.openclaw/agents/<agentId>/agent/auth.json`.
- File-locked refresh prevents concurrent token invalidation.
- Token refresh is automatic when `expires` is in the past.
- CLI commands: `openclaw models auth login`, `openclaw models auth setup-token`, `openclaw models auth paste-token`, `openclaw models status`.

## Skills

```json5
{
  skills: {
    allowBundled: ["gemini", "peekaboo"],
    load: { extraDirs: ["~/Projects/agent-scripts/skills"] },
    install: { preferBrew: true, nodeManager: "npm" }, // npm | pnpm | yarn
    entries: {
      "nano-banana-pro": { apiKey: "KEY", env: { GEMINI_API_KEY: "KEY" } },
      peekaboo: { enabled: true },
      sag: { enabled: false },
    },
  },
}
```

- `allowBundled`: optional allowlist for bundled skills only.
- `entries.<key>.enabled: false` disables a skill.

## Plugins

```json5
{
  plugins: {
    enabled: true,
    allow: ["voice-call"],
    deny: [],
    slots: { memory: "memory-core" }, // memory-core | memory-lancedb | none
    load: { paths: ["~/Projects/oss/voice-call-extension"] },
    entries: {
      "voice-call": { enabled: true, config: { provider: "twilio" } },
    },
  },
}
```

**Plugin discovery order** (precedence): 1) `load.paths`, 2) workspace extensions, 3) global extensions (`~/.openclaw/extensions`), 4) bundled plugins.

- `plugins.installs`: tracks npm-installed plugins.
- `plugins.entries.<id>.config`: supports JSON Schema validation via plugin manifest.
- `plugins.slots.<category>`: only one plugin active at a time per slot.
- `OPENCLAW_PLUGIN_CATALOG_PATHS` / `OPENCLAW_MPM_CATALOG_PATHS` env vars for external catalog paths.
- External catalog paths: `~/.openclaw/mpm/plugins.json`, `catalog.json`.
- Unknown IDs in `entries`, `allow`, `deny`, `slots` cause errors.

**Bundled auth plugins:** `google-antigravity-auth`, `google-gemini-cli-auth`, `qwen-portal-auth`, `copilot-proxy`.

**Plugin manifest (`openclaw.plugin.json`):** `id`, `configSchema`, `uiHints`, `kind`, `skills`.
- `openclaw.extensions` in `package.json` for plugin entry points.
- Channel plugin manifest: `id`, `label`, `selectionLabel`, `docsPath`, `blurb`, `order`, `aliases`, `preferOver`.
- Install manifest: `npmSpec`, `localPath`, `defaultChoice`.

**Security:** symlink/path traversal blocking, world-writable paths rejected, ownership checks, `--ignore-scripts` on install.

**CLI commands:** `openclaw plugins list`, `info`, `install`, `update`, `enable`, `disable`, `doctor`.

Config changes require gateway restart.

## Browser

```json5
{
  browser: {
    enabled: true,
    evaluateEnabled: true,
    defaultProfile: "chrome",
    headless: false,
    noSandbox: false,
    executablePath: "/usr/bin/google-chrome",
    attachOnly: false,
    profiles: {
      openclaw: { cdpPort: 18800, color: "#FF4500" },
      work: { cdpPort: 18801, color: "#0066CC" },
      remote: { cdpUrl: "http://10.0.0.42:9222", color: "#00AA00" },
    },
    color: "#FF4500",
  },
}
```

Auto-detect order: default browser (if Chromium-based) > Chrome > Brave > Edge > Chromium > Chrome Canary.

## Hooks

```json5
{
  hooks: {
    enabled: true,
    token: "shared-secret",
    path: "/hooks",
    maxBodyBytes: 262144,
    defaultSessionKey: "hook:ingress",
    allowRequestSessionKey: false,
    allowedSessionKeyPrefixes: ["hook:"],
    allowedAgentIds: ["hooks", "main"],
    presets: ["gmail"],
    transformsDir: "~/.openclaw/hooks",
    mappings: [
      {
        match: { path: "gmail" },
        action: "agent",
        agentId: "hooks",
        wakeMode: "now",
        name: "Gmail",
        sessionKey: "hook:gmail:{{messages[0].id}}",
        messageTemplate: "From: {{messages[0].from}}\nSubject: {{messages[0].subject}}",
        deliver: true,
        channel: "last",
        model: "openai/gpt-5.2-mini",
        thinking: "low",
        transform: "",
      },
    ],
  },
}
```

**Endpoints:**
- `POST /hooks/wake` - `{ text, mode?: "now"|"next-heartbeat" }`
- `POST /hooks/agent` - `{ message, name?, agentId?, sessionKey?, wakeMode?, deliver?, channel?, to?, model? }`
- `POST /hooks/<name>` - resolved via `hooks.mappings`

Auth: `Authorization: Bearer <token>` or `x-openclaw-token: <token>`.

- `mappings[].match.source`: match by source identifier.
- `mappings[].thinking`: thinking level for the agent run.
- `mappings[].transform`: path to a transform script.

### Gmail Integration

```json5
{
  hooks: {
    gmail: {
      account: "openclaw@gmail.com",
      topic: "projects/<project-id>/topics/gog-gmail-watch",
      subscription: "gog-gmail-watch-push",
      pushToken: "shared-push-token",
      hookUrl: "http://127.0.0.1:18789/hooks/gmail",
      includeBody: true,
      maxBytes: 20000,
      renewEveryMinutes: 720,
      model: "openai/gpt-5.2-mini",
      thinking: "low",
      serve: { bind: "127.0.0.1", port: 8788, path: "/" },
      tailscale: { mode: "funnel", path: "/gmail-pubsub" },
    },
  },
}
```

## Cron

```json5
{
  cron: {
    enabled: true,
    store: "~/.openclaw/cron/jobs.json", // verify: docs say jobs.json, reference had store.json
    maxConcurrentRuns: 2,
    sessionRetention: "24h", // verify: in reference but not in docs page
    webhook: "", // deprecated fallback URL
    webhookToken: "", // optional bearer token for webhook
  },
}
```

- `OPENCLAW_SKIP_CRON=1` env var bypasses cron config entirely.

### Job fields

```json5
{
  name: "daily-report",
  jobId: "daily-report-1",
  enabled: true,
  description: "Generate daily summary",
  agentId: "main",
  sessionTarget: "cron:daily",
  wakeMode: "now", // now | next-heartbeat
  deleteAfterRun: false, // for one-shot jobs
  schedule: {
    kind: "every", // at | every | cron
    // at: "2026-03-01T09:00:00Z",   // for kind: "at"
    everyMs: 3600000,                 // for kind: "every"
    // expr: "0 9 * * *",            // for kind: "cron"
    tz: "America/New_York",           // IANA timezone
    staggerMs: 0,                     // default: up to 5m stagger for top-of-hour
  },
  payload: {
    // Option 1: systemEvent
    systemEvent: { text: "Run daily report" },
    // Option 2: agentTurn
    // agentTurn: {
    //   message: "Generate report",
    //   model: "openai/gpt-5.2-mini",
    //   thinking: "low", // off | minimal | low | medium | high | xhigh
    //   timeoutSeconds: 300,
    // },
  },
  deliver: {
    mode: "announce", // announce | webhook | none
    channel: "slack", // slack | discord | telegram | whatsapp | signal | imessage | mattermost | last
    to: "#reports",
    bestEffort: true,
  },
}
```

- One-shot (`at`) jobs disable after terminal run and do not retry.
- Retry backoff: 30s, 1m, 5m, 15m, 60m; resets after success.
- Run history: `~/.openclaw/cron/runs/<jobId>.jsonl` (auto-pruned).
- Telegram delivery targets: chat ID, explicit topic, shorthand, or prefixed formats.
```

## Discovery

### mDNS (Bonjour)
```json5
{ discovery: { mdns: { mode: "minimal" } } } // minimal | full | off
```

### Wide-area (DNS-SD)
```json5
{ discovery: { wideArea: { enabled: true } } }
```

## Canvas Host

```json5
{
  canvasHost: {
    enabled: true,
    root: "~/.openclaw/workspace/canvas",
    port: 18793,
    liveReload: true,
  },
}
```

## UI

```json5
{
  ui: {
    seamColor: "#FF4500",
    assistant: { name: "OpenClaw", avatar: "CB" },
  },
}
```

## Logging

```json5
{
  logging: {
    level: "info",
    file: "/tmp/openclaw/openclaw.log",
    consoleLevel: "info",
    consoleStyle: "pretty", // pretty | compact | json
    redactSensitive: "tools", // off | tools
    redactPatterns: ["sk-.*", "xoxb-.*"],
  },
}
```

## Memory

```json5
{
  memory: {
    backend: "sqlite", // sqlite | qmd
    citations: "auto", // auto | on | off
    qmd: {
      command: "qmd",
      searchMode: "query", // query | search | vsearch
      includeDefaultMemory: true,
      paths: [{ name: "docs", path: "~/notes", pattern: "**/*.md" }],
      sessions: {
        enabled: false,
        retentionDays: 30,
        exportDir: "~/.openclaw/memory/exports",
      },
      update: {
        interval: "1h",
        debounceMs: 5000,
        onBoot: true,
        waitForBootSync: false,
        embedInterval: "4h",
        commandTimeoutMs: 30000,
        updateTimeoutMs: 60000,
        embedTimeoutMs: 120000,
      },
      limits: {
        maxResults: 10,
        maxSnippetChars: 700,
        maxInjectedChars: 5000,
        timeoutMs: 10000,
      },
      scope: {
        default: "deny",
        rules: [{ action: "allow", match: { chatType: "direct" } }],
      },
    },
  },
}
```

- `backend`: `sqlite` (default, built-in) or `qmd` (external QMD command).
- `citations`: controls citation footers in memory search results.

## Wizard

Metadata written by `openclaw onboard` / `openclaw configure`. Read-only; do not edit manually.

```json5
{
  wizard: {
    lastRunAt: "2026-02-01T12:00:00.000Z",
    lastRunVersion: "2026.2.1",
    lastRunCommit: "abc1234",
    lastRunCommand: "onboard",
    lastRunMode: "interactive",
  },
}
```

## Update

```json5
{
  update: {
    checkOnStart: true, // false to suppress update-available hints on gateway startup
  },
}
```

## Meta

System-managed metadata. Updated automatically by OpenClaw.

```json5
{
  meta: {
    lastTouchedVersion: "2026.1.29",
  },
}
```

## Bridge (Removed)

The TCP bridge listener (`bridge.*`) has been removed. Legacy `bridge.*` config keys are no longer part of the schema -- validation fails until removed. Run `openclaw doctor --fix` to strip unknown keys.

## Config Includes

Split config into multiple files:

```json5
{
  gateway: { port: 18789 },
  agents: { $include: "./agents.json5" },
  broadcast: { $include: ["./clients/a.json5", "./clients/b.json5"] },
}
```

- Single file: replaces containing object.
- Array: deep-merged in order (later wins).
- Sibling keys: merged after includes.
- Nested: up to 10 levels deep.
- Paths: relative to including file.
