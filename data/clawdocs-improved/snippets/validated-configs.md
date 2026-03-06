# Validated OpenClaw Config Snippets

All snippets verified against Context7 `/openclaw/openclaw` source and gateway runtime v2026.2.21-2.
Last validated: 2026-02-22.

---

## Agents & Models

### Model with Fallbacks
```json5
{
  agents: {
    defaults: {
      model: {
        primary: "anthropic/claude-sonnet-4-6",
        fallbacks: ["openai/gpt-5.3-codex"],
      },
      models: {
        "anthropic/claude-opus-4-6": { alias: "opus" },
        "anthropic/claude-haiku-4-5": { alias: "haiku" },
        "openai/gpt-5.3-codex": {},
      },
    },
  },
}
```

### Heartbeat
```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "1h",            // 0m disables
        target: "discord",      // last | discord | telegram | whatsapp | none
        model: "anthropic/claude-haiku-4-5",
        activeHours: {
          start: "08:00",
          end: "23:00",
          timezone: "America/New_York",
        },
      },
    },
  },
}
```

### Compaction + Memory Flush
```json5
{
  agents: {
    defaults: {
      compaction: {
        mode: "safeguard",
        reserveTokensFloor: 20000,
        memoryFlush: {
          enabled: true,
          softThresholdTokens: 4000,
          systemPrompt: "Session nearing compaction. Store durable memories now.",
          prompt: "Write any lasting notes to memory/YYYY-MM-DD.md; reply with NO_REPLY if nothing to store.",
        },
      },
    },
  },
}
```

### Context Pruning
```json5
{
  agents: {
    defaults: {
      contextPruning: {
        mode: "cache-ttl",
        ttl: "1h",
        tools: {
          allow: ["exec", "read"],       // only prune these tool results
          deny: ["*memory*", "*image*"], // never prune these
        },
      },
    },
  },
}
```

### Memory Search (OpenAI Embeddings)
```json5
{
  agents: {
    defaults: {
      memorySearch: {
        provider: "openai",
        model: "text-embedding-3-small",
        sync: { watch: true },
        cache: { enabled: true, maxEntries: 50000 },
        query: {
          hybrid: {
            enabled: true,
            vectorWeight: 0.7,
            textWeight: 0.3,
            candidateMultiplier: 4,
            mmr: { enabled: true, lambda: 0.7 },
            temporalDecay: { enabled: true, halfLifeDays: 30 },
          },
        },
      },
    },
  },
}
// Requires OPENAI_API_KEY env var. Anthropic OAuth does NOT cover embeddings.
```

---

## Session Management

### Session Reset + Per-Type Overrides
```json5
{
  session: {
    dmScope: "per-channel-peer",
    reset: { mode: "idle", idleMinutes: 240 },
    resetByType: {
      direct: { mode: "idle", idleMinutes: 240 },
      group: { mode: "idle", idleMinutes: 120 },
      thread: { mode: "daily", atHour: 4 },
    },
    resetTriggers: ["/new", "/reset"],
    threadBindings: { enabled: true, ttlHours: 24 },
    maintenance: {
      mode: "enforce",    // warn | enforce
      pruneAfter: "7d",
      maxEntries: 500,
      rotateBytes: "10mb",
    },
    identityLinks: {
      frank: ["bluebubbles:+13479072901", "discord:sallvain"],
    },
  },
}
```

---

## Channels

### Discord
```json5
{
  channels: {
    discord: {
      enabled: true,
      token: "${DISCORD_BOT_TOKEN}",
      groupPolicy: "open",         // open | allowlist | disabled
      replyToMode: "first",        // off | first | all
      dmPolicy: "pairing",
      allowFrom: ["178012755612139520"],
      guilds: {
        "*": { requireMention: false },
      },
      actions: {
        reactions: true, messages: true, threads: true, pins: true,
        search: true, memberInfo: true, roleInfo: true, channelInfo: true,
        polls: true, stickers: true, voiceStatus: true, events: true,
        roles: false, moderation: false,
      },
      execApprovals: {
        enabled: true,
        approvers: ["178012755612139520"],
        target: "dm",              // dm | channel | both
        cleanupAfterResolve: true,
      },
    },
  },
}
// NOTE: streaming is Telegram-only. threadBindings goes under session, not channels.discord.
```

### BlueBubbles (iMessage)
```json5
{
  channels: {
    bluebubbles: {
      enabled: true,
      serverUrl: "http://100.x.x.x:1234",
      password: "${BLUEBUBBLES_PASSWORD}",
      dmPolicy: "allowlist",
      allowFrom: ["+13479072901", "+15072611693"],
      groupPolicy: "allowlist",
    },
  },
}
```

---

## Gateway

### Local + Tailscale Funnel
```json5
{
  gateway: {
    port: 18789,
    mode: "local",
    bind: "loopback",
    auth: {
      mode: "password",           // token | password | trusted-proxy
      password: "${OPENCLAW_GATEWAY_PASSWORD}",
      allowTailscale: true,
      rateLimit: {
        maxAttempts: 10,
        windowMs: 60000,
        lockoutMs: 300000,
        exemptLoopback: true,
      },
    },
    tailscale: {
      mode: "funnel",             // off | serve | funnel
      resetOnExit: false,
    },
    controlUi: { enabled: true, basePath: "/openclaw" },
  },
}
// funnel mode requires auth.mode = "password"
```

---

## Tools

### Tool Allow/Deny + Loop Detection
```json5
{
  tools: {
    allow: ["exec", "process", "read", "write", "edit", "message",
            "sessions_send", "sessions_list", "sessions_history",
            "sessions_spawn", "session_status"],
    deny: ["browser"],
    exec: {
      backgroundMs: 10000,
      timeoutSec: 1800,
      cleanupMs: 1800000,
      notifyOnExit: true,
    },
    loopDetection: {
      enabled: true,
      historySize: 30,
      warningThreshold: 10,
      criticalThreshold: 20,
      globalCircuitBreakerThreshold: 30,
      detectors: {
        genericRepeat: true,
        knownPollNoProgress: true,
        pingPong: true,
      },
    },
    web: {
      search: { enabled: true, apiKey: "${BRAVE_API_KEY}" },
      fetch: { enabled: true },
    },
    elevated: {
      enabled: true,
      allowFrom: { discord: ["178012755612139520"] },
    },
  },
}
```

### Exec Approvals (top-level)
```json5
{
  approvals: {
    exec: {
      enabled: true,
      mode: "session",            // session | targets | both
      agentFilter: ["main"],
      sessionFilter: ["discord"],
    },
  },
}
```

---

## Automation

### Hooks + Gmail
```json5
{
  hooks: {
    enabled: true,
    token: "${OPENCLAW_HOOK_TOKEN}",
    path: "/hooks",
    defaultSessionKey: "hook:ingress",
    allowRequestSessionKey: false,
    allowedSessionKeyPrefixes: ["hook:"],
    presets: ["gmail"],
    mappings: [
      {
        match: { path: "gmail" },
        action: "agent",
        name: "Gmail",
        wakeMode: "next-heartbeat",
        sessionKey: "hook:gmail-personal",
        messageTemplate: "From: {{messages[0].from}}\nSubject: {{messages[0].subject}}\n{{messages[0].body}}",
        deliver: true,
        channel: "discord",
        to: "channel:1234567890",  // Discord channel ID with channel: prefix
      },
    ],
    gmail: {
      model: "anthropic/claude-haiku-4-5",
      thinking: "off",
      account: "user@gmail.com",
      label: "INBOX",
      topic: "projects/<project-id>/topics/gmail-watch",
      subscription: "gmail-push",
      pushToken: "<shared-push-token>",
      hookUrl: "http://127.0.0.1:18789/hooks/gmail",
      includeBody: true,
      maxBytes: 20000,
      renewEveryMinutes: 60,
      serve: { bind: "127.0.0.1", port: 8788, path: "/" },
      tailscale: { mode: "funnel", path: "/gmail" },
    },
  },
}
// Discord targets MUST use channel:<id> prefix — bare IDs fail silently.
// wakeMode "next-heartbeat" prevents iMessage spam from main session summaries.
```

### Cron
```json5
{
  cron: {
    enabled: true,
    maxConcurrentRuns: 2,
    sessionRetention: "7d",       // duration string or false
  },
}
```

### Cron Job (CLI)
```bash
openclaw cron add \
  --name "Morning briefing" \
  --cron "0 8 * * *" \
  --tz "America/New_York" \
  --session isolated \
  --message "Summarize overnight updates." \
  --model "anthropic/claude-haiku-4-5" \
  --announce \
  --channel discord \
  --to "channel:1234567890"
```

---

## Logging

```json5
{
  logging: {
    level: "info",               // info | debug | trace
    file: "/tmp/openclaw/openclaw.log",
    consoleLevel: "info",
    redactSensitive: "tools",    // off | tools
  },
}
```

---

## QMD Memory Backend (Experimental)

```json5
{
  memory: {
    backend: "qmd",
    citations: "auto",           // auto | on | off
    qmd: {
      includeDefaultMemory: true,
      update: { interval: "5m", debounceMs: 15000, onBoot: true, waitForBootSync: false },
      limits: { maxResults: 6, timeoutMs: 4000 },
      scope: {
        default: "deny",
        rules: [{ action: "allow", match: { chatType: "direct" } }],
      },
    },
  },
}
// Requires: bun + qmd CLI on PATH. Falls back to built-in SQLite if QMD fails.
```

---

## Known Gotchas

- `channels.discord.streaming` — **Telegram-only**. Rejected under Discord.
- `channels.discord.threadBindings` — goes under `session.threadBindings` (global), not per-channel.
- Discord `to` targets need `channel:<id>` prefix — bare IDs fail silently.
- `hooks.gmail` only supports one account. Additional accounts need separate `gog gmail watch serve` systemd services.
- `gateway.tailscale.mode: "funnel"` requires `gateway.auth.mode: "password"`.
- `GOG_KEYRING_PASSWORD` must be in gateway service env for Gmail watch to decrypt OAuth tokens.
- See `./snippets/errata.md` for full errata list.
