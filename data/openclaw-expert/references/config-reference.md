# Config-Referenz — openclaw.json vollständig

## Datei & Format

- Pfad: `~/.openclaw/openclaw.json`
- Format: **JSON5** (Kommentare `//`, trailing commas erlaubt)
- Hot-Reload: Gateway beobachtet die Datei und wendet Änderungen automatisch an
  - Ausnahme: `gateway.reload` und `gateway.remote` triggern KEINEN Restart
- Validierung: `openclaw config validate`

---

## Alle Top-Level Sections

```
meta / wizard / update / auth / models / agents / tools / messages /
commands / session / hooks / channels / canvasHost / gateway / skills / plugins
```

---

## meta

Automatisch verwaltet — nicht manuell editieren.

```json5
{
  meta: {
    lastTouchedVersion: "2026.2.26",
    lastTouchedAt: "2026-02-28T06:10:52.119Z",
  },
}
```

---

## wizard

Tracking des Setup-Wizards — nicht manuell editieren.

```json5
{
  wizard: {
    lastRunAt: "...",
    lastRunVersion: "2026.2.26",
    lastRunCommand: "configure",    // "setup" | "configure" | "onboard"
    lastRunMode: "local",           // "local" | "remote"
  },
}
```

---

## update

```json5
{
  update: {
    channel: "stable",    // "stable" | "beta" | "nightly"
    auto: { enabled: true },
  },
}
```

`beta` für neue Features, `stable` für Produktion.

---

## auth — Provider-Authentifizierung

Auth-Profile pro LLM-Provider. Key-Format: `provider:label`.

```json5
{
  auth: {
    profiles: {
      // API-Key (häufigster Fall)
      "deepseek:default": { provider: "deepseek", mode: "api_key" },
      "mistral:default":  { provider: "mistral",  mode: "api_key" },
      "google:default":   { provider: "google",   mode: "api_key" },
      "nvidia:default":   { provider: "nvidia",   mode: "api_key" },
      "deepgram:default": { provider: "deepgram", mode: "api_key" },

      // OAuth/Token
      "github-copilot:github":  { provider: "github-copilot",  mode: "token" },
      "openai-codex:default":   { provider: "openai-codex",    mode: "oauth" },
      "anthropic:default":      { provider: "anthropic",        mode: "token" },
      "google-antigravity:user@gmail.com": {
        provider: "google-antigravity", mode: "oauth", email: "user@gmail.com",
      },

      // Lokal (Ollama — Key meist leer/dummy)
      "ollama:default": { provider: "ollama", mode: "api_key" },
    },
  },
}
```

### Bekannte Provider

| Provider | API-Typ | Auth | Modelle |
|---|---|---|---|
| `anthropic` | anthropic-messages | api_key/token | Claude Sonnet/Opus/Haiku |
| `openai-codex` | openai | oauth | GPT-5.x Codex |
| `github-copilot` | openai | token | GPT-5.x, GPT-4.1 |
| `google` | google-generative-ai | api_key | Gemini 3 Pro/Flash |
| `google-antigravity` | google-generative-ai | oauth | Antigravity-Modelle |
| `deepseek` | openai-completions | api_key | V3, R1, V3.2, V3.2-Speciale |
| `moonshot` | openai-completions | api_key | Kimi K2.5 |
| `mistral` | openai-completions | api_key | Mistral Large |
| `nvidia` | openai-completions | api_key | NIM: Kimi, Qwen, DeepSeek |
| `ollama` | openai-completions | api_key | Lokal + Cloud (`:cloud` Suffix) |
| `deepgram` | deepgram | api_key | Audio: Nova-3 |

---

## models — LLM-Provider & Modelle

```json5
{
  models: {
    mode: "merge",    // "merge" = mit Defaults zusammenführen | "replace" = nur eigene
    providers: {
      "<provider-name>": {
        baseUrl: "https://...",       // API-Endpoint
        api: "openai-completions",    // API-Typ (siehe Tabelle)
        // apiKey: "<key>",           // Optional direkt hier (besser: credentials/)
        // auth: "api-key",           // Explizite Auth-Methode
        models: [
          {
            id: "model-id",            // Unique ID
            name: "Anzeigename",       // Für Dashboard/Chat
            reasoning: false,           // true = CoT/Reasoning-Modell
            input: ["text"],            // ["text"] | ["text", "image"]
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 200000,
            maxTokens: 8192,
            api: "openai-completions",  // Kann pro Modell überschrieben werden
          },
        ],
      },
    },
  },
}
```

### API-Typen

| api | Für |
|---|---|
| `anthropic-messages` | Anthropic (Claude) |
| `openai-completions` | OpenAI-kompatibel (DeepSeek, Mistral, NVIDIA, Ollama, Moonshot) |
| `google-generative-ai` | Google (Gemini, Antigravity) |

### Trick: Gleiche baseUrl, verschiedene API-Keys

Wenn verschiedene NVIDIA-Modelle verschiedene Keys brauchen:

```json5
"nvidia":          { baseUrl: "https://integrate.api.nvidia.com/v1", models: [...] },
"nvidia-deepseek": { baseUrl: "https://integrate.api.nvidia.com/v1", models: [...] },
"nvidia-qwen":     { baseUrl: "https://integrate.api.nvidia.com/v1", models: [...] },
```

### Trick: Ollama Cloud-Modelle

Ollama kann Cloud-Modelle proxyen — kostenfrei, kein eigener API-Key:

```json5
"ollama": {
  baseUrl: "http://localhost:11434/v1",
  models: [
    { id: "kimi-k2.5:cloud", name: "Kimi K2.5 (Cloud)", reasoning: true, contextWindow: 262144 },
    { id: "deepseek-v3.2:cloud", name: "DeepSeek V3.2 (Cloud)", reasoning: true },
    { id: "qwen3.5:397b-cloud", name: "Qwen 3.5 397B (Cloud)", reasoning: true },
    // Vision-Modell
    { id: "qwen3-vl:235b-instruct-cloud", input: ["text", "image"] },
  ],
}
```

---

## agents — Agent-Konfiguration

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "openai-codex/gpt-5.3-codex",   // Standard-Modell
      },

      // Modelle mit Aliases (für /model <alias>)
      models: {
        "anthropic/claude-sonnet-4-6":  { alias: "Sonnet" },
        "deepseek/deepseek-reasoner":   { alias: "R1" },
        "ollama/kimi-k2.5:cloud":       { alias: "Ollama-Kimi" },
        "google/gemini-3-pro-preview":  { alias: "gemini" },
        // Ohne alias: /model google/gemini-3-pro-high (voller Pfad)
      },

      workspace: "/home/admin/.openclaw/workspace",

      // Context-Pruning: alte Tool-Ergebnisse entfernen
      contextPruning: {
        mode: "cache-ttl",    // "cache-ttl" | "none"
        ttl: "1h",            // Cache-Lebensdauer
      },

      // Compaction
      compaction: {
        mode: "safeguard",    // "safeguard" | "aggressive" | "manual"
      },

      timeoutSeconds: 1800,   // LLM-Timeout (30 Min)

      heartbeat: { every: "1h" },   // "30m" | "1h" | "4h" | "12h" | "24h"

      maxConcurrent: 4,              // Max parallele Tool-Aufrufe
      subagents: { maxConcurrent: 8 },
    },
  },
}
```

### Compaction-Modi

| Modus | Verhalten | Kosten |
|---|---|---|
| `safeguard` | Auto bei ~80% Context-Limit | Moderat |
| `aggressive` | Häufiger compacten | Spart Tokens |
| `manual` | Nur mit `/compact` | Volle Kontrolle |

---

## tools

```json5
{
  tools: {
    web: {
      search: { enabled: false, apiKey: "<brave/tavily-key>" },
      fetch: { enabled: true },
    },
    media: {
      audio: {
        enabled: true,
        maxBytes: 20971520,   // 20 MB
        providerOptions: {
          deepgram: { detect_language: true, punctuate: true, smart_format: true },
        },
        models: [{ provider: "deepgram", model: "nova-3" }],
      },
    },
    sessions: { visibility: "all" },  // "all" | "own" | "none"
  },
}
```

---

## messages — TTS & Reaktionen

```json5
{
  messages: {
    tts: {
      provider: "edge",    // "edge" | "elevenlabs" | "openai"
      edge: { enabled: true, voice: "de-DE-ConradNeural", lang: "de-DE" },
    },
    ackReactionScope: "group-mentions",  // "all" | "group-mentions" | "none"
  },
}
```

Deutsche Edge-TTS-Stimmen: `de-DE-ConradNeural` (m), `de-DE-KatjaNeural` (w),
`de-DE-AmalaNeural` (w), `de-DE-FlorianMultilingualNeural` (m).

---

## commands / session / hooks

```json5
{
  commands: {
    native: "auto",          // Slash-Commands
    nativeSkills: "auto",    // Skill-Commands
    restart: true,           // /restart erlauben
    ownerDisplay: "raw",     // "raw" | "masked" | "hidden"
  },
  session: {
    dmScope: "per-channel-peer",  // "per-channel-peer" | "global" | "per-channel"
  },
  hooks: {
    internal: {
      enabled: true,
      entries: {
        "boot-md": { enabled: true },
        "bootstrap-extra-files": { enabled: true },
        "command-logger": { enabled: true },
        "session-memory": { enabled: true },
      },
    },
  },
}
```

---

## channels — Messaging-Kanäle

```json5
{
  channels: {
    whatsapp: {
      enabled: true,
      dmPolicy: "allowlist",
      selfChatMode: true,
      allowFrom: ["+4915568920209"],   // E.164-Format MIT +
      groupPolicy: "allowlist",
      debounceMs: 0,
      mediaMaxMb: 50,
    },
    telegram: {
      enabled: true,
      dmPolicy: "allowlist",
      botToken: "<von-BotFather>",
      allowFrom: [7403482253],         // Telegram User-ID (ZAHL, kein String!)
      groupPolicy: "allowlist",
      streaming: "partial",            // "partial" | "full" | "off"
      mediaMaxMb: 50,
    },
  },
}
```

### dmPolicy

| Wert | Bedeutung | Produktion? |
|---|---|---|
| `allowlist` | Nur `allowFrom` | ✅ Immer |
| `open` | Jeder | ⚠️ Nur Tests |
| `closed` | Keine DMs | Gruppen-only |

**ACHTUNG**: WhatsApp dmPolicy gilt **GLOBAL** für den Account!

---

## gateway

```json5
{
  gateway: {
    port: 18789,
    mode: "local",           // "local" | "remote"
    bind: "loopback",        // "loopback" | "lan" | "tailnet" | "custom"
    controlUi: {
      // enabled: true,
      allowedOrigins: ["https://hostname.taildcb944.ts.net"],  // CORS!
    },
    auth: {
      mode: "token",
      token: "<token>",              // Besser: OPENCLAW_GATEWAY_TOKEN env
      allowTailscale: true,
    },
    trustedProxies: ["100.64.0.0/10"],  // Tailscale CGNAT — PFLICHT für allowTailscale!
    tailscale: {
      mode: "serve",         // "off" | "serve" | "funnel"
      resetOnExit: false,
    },
  },
}
```

---

## skills / plugins

```json5
{
  skills: {
    entries: {
      "gh-issues": { apiKey: "<github-token>" },
      "peekaboo": { enabled: true },
    },
  },
  plugins: {
    entries: {
      telegram: { enabled: true },
      whatsapp: { enabled: true },
    },
  },
}
```

---

## Häufige Config-Fehler

| Fehler | Symptom | Fix |
|---|---|---|
| `allowFrom` als String statt Array | Channel startet nicht | `["+49..."]` (Array!) |
| Telegram allowFrom als String | Keine Nachrichten | `[7403482253]` (Zahl!) |
| WhatsApp ohne Ländercode | Keine Nachrichten | `"+4915568920209"` (E.164) |
| `bind: "lan"` ohne Auth | Gateway-Start verweigert | Auth setzen |
| Doppelte Modell-IDs | Unvorhersehbar | Jede ID nur 1x |
| `trustedProxies` fehlt | allowTailscale ignoriert | `["100.64.0.0/10"]` |
| `allowedOrigins` fehlt | CORS im Dashboard | Tailscale-Domain eintragen |
| Provider ≠ auth.profiles Key | Auth fehlschlag | Namen abgleichen |
| `cost: 0` bei Ollama Cloud | Falsche Kostenanzeige | Korrekt — Cloud-Modelle sind gratis |

---

## Validierung

```bash
openclaw config validate       # Syntax + Struktur prüfen
openclaw config get <pfad>     # Einzelnen Wert lesen
openclaw config edit           # Im Editor öffnen
openclaw doctor                # Gesundheitscheck nach Änderung
```
