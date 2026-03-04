# Agents Configuration Reference

## Table of Contents

- [Agent Defaults](#agent-defaults)
- [Model Configuration](#model-configuration)
- [CLI Backends](#cli-backends)
- [Heartbeat](#heartbeat)
- [Compaction](#compaction)
- [Memory Search](#memory-search)
- [Context Pruning](#context-pruning)
- [Block Streaming](#block-streaming)
- [Typing Indicators](#typing-indicators)
- [Sandbox](#sandbox)
- [Per-Agent Overrides](#per-agent-overrides)
- [Multi-Agent Routing](#multi-agent-routing)
- [Per-Agent Access Profiles](#per-agent-access-profiles)

## Agent Defaults

### Workspace

Default: `~/.openclaw/workspace`.

```json5
{ agents: { defaults: { workspace: "~/.openclaw/workspace" } } }
```

### repoRoot

Optional repository root shown in system prompt's Runtime line. Auto-detects if unset.

### skipBootstrap

Disables automatic creation of workspace bootstrap files (`AGENTS.md`, `SOUL.md`, `TOOLS.md`, `IDENTITY.md`, `USER.md`, `HEARTBEAT.md`, `BOOTSTRAP.md`).

### bootstrapMaxChars

Max characters per workspace bootstrap file before truncation. Default: `20000`.

### userTimezone

Timezone for system prompt context (not message timestamps). Falls back to host timezone.

### timeFormat

`auto` (default) | `12` | `24`.

## Model Configuration

```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-opus-4-6": { alias: "opus" },
        "minimax/MiniMax-M2.1": { alias: "minimax" },
      },
      model: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: ["minimax/MiniMax-M2.1"],
      },
      imageModel: {
        primary: "openrouter/qwen/qwen-2.5-vl-72b-instruct:free",
        fallbacks: ["openrouter/google/gemini-2.0-flash-vision:free"],
      },
      thinkingDefault: "low",
      verboseDefault: "off",
      elevatedDefault: "on",
      timeoutSeconds: 600,
      mediaMaxMb: 5,
      contextTokens: 200000,
      maxConcurrent: 3,
    },
  },
}
```

- `model.primary`: format `provider/model` (e.g. `anthropic/claude-opus-4-6`).
- `models`: configured model catalog and allowlist for `/model`. Entries can include `alias` and `params` (`temperature`, `maxTokens`).
- `imageModel`: only used if primary model lacks image input.
- `maxConcurrent`: max parallel agent runs across sessions. Default: 1.

**Built-in alias shorthands** (only when model is in `agents.defaults.models`):

| Alias | Model |
|-------|-------|
| `opus` | `anthropic/claude-opus-4-6` |
| `sonnet` | `anthropic/claude-sonnet-4-5` |
| `gpt` | `openai/gpt-5.2` |
| `gpt-mini` | `openai/gpt-5-mini` |
| `gemini` | `google/gemini-3-pro-preview` |
| `gemini-flash` | `google/gemini-3-flash-preview` |

Your configured aliases always win over defaults.

- Model refs are normalized to lowercase. Parsing: first `/` splits provider from model; IDs with multiple slashes require full provider prefix.
- "Model is not allowed" error: returned when a model isn't in the allowlist.
- **Deprecation:** Omitting provider prefix in model refs (e.g. `"claude-opus-4-6"` instead of `"anthropic/claude-opus-4-6"`) currently assumes `anthropic`; this will be removed in a future version.

## CLI Backends

Optional CLI backends for text-only fallback runs (no tool calls).

```json5
{
  agents: {
    defaults: {
      cliBackends: {
        "claude-cli": { command: "/opt/homebrew/bin/claude" },
        "my-cli": {
          command: "my-cli",
          args: ["--json"],
          output: "json",
          modelArg: "--model",
          sessionArg: "--session",
          sessionMode: "existing",
          systemPromptArg: "--system",
          systemPromptWhen: "first",
          imageArg: "--image",
          imageMode: "repeat",
        },
      },
    },
  },
}
```

## Heartbeat

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m", // 0m disables
        model: "openai/gpt-5.2-mini",
        includeReasoning: false,
        suppressToolErrorWarnings: false,
        session: "main",
        to: "+15555550123",
        target: "last", // last | whatsapp | telegram | discord | ... | none
        accountId: "default",
        prompt: "Read HEARTBEAT.md if it exists...",
        ackMaxChars: 300,
        activeHours: {
          start: "08:00", // HH:MM format ("24:00" allowed for end)
          end: "22:00",
          timezone: "user", // user | local | IANA timezone string (IANA validated with fallback)
        },
      },
    },
  },
}
```

- `every`: duration string (ms/s/m/h). Default: `30m`.
- Per-agent: `agents.list[].heartbeat`. When any agent defines heartbeat, **only those agents** run heartbeats.
- Configuration hierarchy (5 levels): per-agent > agent defaults > per-channel-account > per-channel > channel defaults.
- HEARTBEAT.md: empty/header-only file skips heartbeat run.
- `HEARTBEAT_OK` response token: stripped from start/end of response only (middle occurrences have no special meaning).
- Manual trigger: `openclaw system event --text "..." --mode now` or `--mode next-heartbeat`.

## Compaction

```json5
{
  agents: {
    defaults: {
      compaction: {
        mode: "safeguard", // default | safeguard
        reserveTokensFloor: 24000,
        memoryFlush: {
          enabled: true,
          softThresholdTokens: 6000,
          systemPrompt: "Session nearing compaction. Store durable memories now.",
          prompt: "Write any lasting notes to memory/YYYY-MM-DD.md; reply with NO_REPLY if nothing to store.",
        },
      },
    },
  },
}
```

- Compaction is **on by default**.
- `safeguard`: chunked summarization for long histories.
- `memoryFlush`: silent agentic turn before auto-compaction to store durable memories.
- `/compact` command triggers manual compaction.
- See also: Context Pruning (complementary feature for in-memory tool result management).

## Memory Search

Configures semantic search over workspace memory files.

```json5
{
  agents: {
    defaults: {
      memorySearch: {
        enabled: true,
        provider: "local", // local | openai | gemini | voyage
        model: "text-embedding-3-small",
        fallback: "local", // openai | gemini | local | none
        local: {
          modelPath: "hf:ggml-org/embeddinggemma-300M-GGUF/embeddinggemma-300M-Q8_0.gguf",
          modelCacheDir: "~/.cache/openclaw/models",
        },
        remote: {
          baseUrl: "https://api.openai.com/v1/",
          apiKey: "${OPENAI_API_KEY}",
          headers: {},
          batch: {
            enabled: false,
            wait: true,
            pollIntervalMs: 5000,
            timeoutMinutes: 30,
            concurrency: 2,
          },
        },
        query: {
          hybrid: {
            enabled: true,
            vectorWeight: 0.7,
            textWeight: 0.3,
            candidateMultiplier: 4,
          },
        },
        store: {
          path: "~/.openclaw/memory/{agentId}.sqlite",
          vector: { enabled: true, extensionPath: "" },
        },
        cache: { enabled: true, maxEntries: 50000 },
        sync: {
          watch: true,
          sessions: { deltaBytes: 100000, deltaMessages: 50 },
        },
        sources: ["memory"], // memory | sessions
        extraPaths: [],
        experimental: { sessionMemory: false },
      },
    },
  },
}
```

- `provider`: `local` (GGUF embeddings), `openai`, `gemini`, or `voyage`.
- `store.path`: supports `{agentId}` token. Uses sqlite-vec for vector acceleration.
- `query.hybrid`: BM25 + vector fusion. `vectorWeight` + `textWeight` normalized to 1.0.
- `sources`: `["memory"]` (default) or `["memory", "sessions"]` for session transcript indexing.

## Context Pruning

Prunes **old tool results** from in-memory context. Does **not** modify session history on disk.

```json5
{
  agents: {
    defaults: {
      contextPruning: {
        mode: "cache-ttl", // off | cache-ttl
        ttl: "1h",
        keepLastAssistants: 3,
        softTrimRatio: 0.3,
        hardClearRatio: 0.5,
        minPrunableToolChars: 50000,
        softTrim: { maxChars: 4000, headChars: 1500, tailChars: 1500 },
        hardClear: { enabled: true, placeholder: "[Old tool result content cleared]" },
        tools: { deny: ["browser", "canvas"] },
      },
    },
  },
}
```

- **Soft-trim**: keeps beginning + end, inserts `...` in middle.
- **Hard-clear**: replaces entire tool result with placeholder.
- Image blocks are never trimmed/cleared.
- **Only active for Anthropic API calls** (and OpenRouter Anthropic models).
- Smart TTL defaults: `"1h"` for OAuth/setup-token, `"30m"` for API key profiles.
- Recommend matching `ttl` to your model's `cacheControlTtl`.
- `contextTokens` (under Model Configuration) acts as a cap on resolved context window and affects pruning thresholds.
- `models.providers.*.models[].contextWindow` overrides context window estimation for pruning calculations.
- `tools.deny` and `tools.allow` support wildcards and case-insensitive matching.

## Block Streaming

```json5
{
  agents: {
    defaults: {
      blockStreamingDefault: "off", // on | off
      blockStreamingBreak: "text_end", // text_end | message_end
      blockStreamingChunk: {
        minChars: 800,
        maxChars: 1200,
        breakPreference: "paragraph", // paragraph | newline | sentence | whitespace | hard-break
      },
      blockStreamingCoalesce: {
        idleMs: 1000,
        minChars: 1500, // default 1500 for Signal/Slack/Discord
        maxChars: 3000,
      },
      humanDelay: { mode: "natural" }, // off | natural | custom
    },
  },
}
```

- `humanDelay`: `natural` = 800-2500ms randomized pause between block replies. Per-agent override: `agents.list[].humanDelay`.
- Per-channel `blockStreaming` toggle (`true`/`false`) enables/disables block streaming per channel.
- Per-channel `streaming` field: `"off"`, `"partial"`, `"block"`, `"progress"` for preview streaming mode.
- Break preference hierarchy: Paragraph > newline > sentence > whitespace > hard break. Code fences never split internally.
- `channels.slack.nativeStreaming`: `true` (default) uses Slack native streaming API.
- `chunkMode` values: `"length"` (split by char count) or `"newline"` (split at newline boundaries).

## Typing Indicators

```json5
{
  agents: {
    defaults: {
      typingMode: "instant", // never | instant | thinking | message
      typingIntervalSeconds: 6,
    },
  },
}
```

- Session-level overrides: `session.typingMode` and `session.typingIntervalSeconds`.
- `thinking` mode requires `reasoningLevel: "stream"` or it won't fire.
- `message` mode won't activate for silent-only replies.
- Heartbeat runs never display typing indicators.
- Defaults: `instant` for direct chats/mentions, `message` for unmentioned group chats.

## Sandbox

Docker sandboxing for the embedded agent.

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main", // off | non-main | all
        scope: "agent", // session | agent | shared
        workspaceAccess: "none", // none | ro | rw
        workspaceRoot: "~/.openclaw/sandboxes",
        docker: {
          image: "openclaw-sandbox:bookworm-slim",
          containerPrefix: "openclaw-sbx-",
          workdir: "/workspace",
          readOnlyRoot: true,
          tmpfs: ["/tmp", "/var/tmp", "/run"],
          network: "none",
          user: "1000:1000",
          capDrop: ["ALL"],
          env: { LANG: "C.UTF-8" },
          setupCommand: "apt-get update && apt-get install -y git curl jq",
          pidsLimit: 256,
          memory: "1g",
          memorySwap: "2g",
          cpus: 1,
          ulimits: { nofile: { soft: 1024, hard: 2048 }, nproc: 256 },
          dns: ["1.1.1.1", "8.8.8.8"],
          binds: ["/home/user/source:/source:rw"],
          seccompProfile: "default",
          apparmorProfile: "",
          extraHosts: ["host.docker.internal:host-gateway"],
        },
        browser: {
          enabled: false,
          image: "openclaw-sandbox-browser:bookworm-slim",
          network: "openclaw-sandbox-browser", // dedicated Docker network (default)
          cdpPort: 9222,
          cdpSourceRange: "172.16.0.0/12", // CIDR allowlist for CDP connections
          vncPort: 5900,
          noVncPort: 6080,
          headless: false,
          enableNoVnc: true,
          autoStart: true,
          autoStartTimeoutMs: 30000,
          allowHostControl: false,
          allowedControlUrls: [], // gating for target: "custom" allowlists
          allowedControlHosts: [],
          allowedControlPorts: [],
          binds: [], // when set (including []), replaces docker.binds for browser; when omitted, falls back to docker.binds
        },
        prune: { idleHours: 24, maxAgeDays: 7 },
      },
    },
  },
}
```

**Workspace access:** `none` (sandbox workspace), `ro` (agent workspace read-only at `/agent`), `rw` (agent workspace at `/workspace`).

**Scope:** `session` (per-session), `agent` (per-agent, default), `shared` (no isolation). `"shared"` scope: per-agent binds are ignored.

Containers default to `network: "none"` — set `"bridge"` for outbound access.

Build images: `scripts/sandbox-setup.sh` and `scripts/sandbox-browser-setup.sh`.

**Blocked bind sources:** `docker.sock`, `/etc`, `/proc`, `/sys`, `/dev`, parent mounts.

**Caveats:**
- `docker.setupCommand` with default `network: "none"` prevents package installs. Set `network: "bridge"` or use `setupCommand` before setting `network: "none"`.
- `docker.readOnlyRoot: true` prevents writes outside tmpfs/binds.
- `docker.user` must be `"0:0"` (root) for package installs.
- `tools.elevated` bypasses sandboxing.
- Inbound media is copied to sandbox workspace `media/inbound/*`.
- Skills with `workspaceAccess: "none"` are mirrored to `.../skills`; with `"rw"`, readable from `/workspace/skills`.
- Group/channel sessions are treated as non-main and sandboxed automatically.
- `"non-main"` mode is based on `session.mainKey`, not agent ID.
- Debug: `openclaw sandbox explain` shows sandbox resolution for current context.

## Per-Agent Overrides

```json5
{
  agents: {
    list: [
      {
        id: "main",
        default: true,
        name: "Main Agent",
        workspace: "~/.openclaw/workspace",
        agentDir: "~/.openclaw/agents/main/agent",
        model: "anthropic/claude-opus-4-6",
        identity: {
          name: "Samantha",
          theme: "helpful sloth",
          emoji: "🦥",
          avatar: "avatars/samantha.png",
        },
        groupChat: { mentionPatterns: ["@openclaw"] },
        sandbox: { mode: "off" },
        subagents: { allowAgents: ["*"] },
        tools: {
          profile: "coding",
          allow: ["browser"],
          deny: ["canvas"],
          elevated: { enabled: true },
        },
      },
    ],
  },
}
```

- `model`: string overrides `primary` only; object `{ primary, fallbacks }` overrides both.
- `identity.avatar`: workspace-relative path, URL, or `data:` URI.
- `identity` derives defaults: `ackReaction` from `emoji`, `mentionPatterns` from `name`/`emoji`.

## Multi-Agent Routing

```json5
{
  agents: {
    list: [
      { id: "home", default: true, workspace: "~/.openclaw/workspace-home" },
      { id: "work", workspace: "~/.openclaw/workspace-work" },
    ],
  },
  bindings: [
    { agentId: "home", match: { channel: "whatsapp", accountId: "personal" } },
    { agentId: "work", match: { channel: "whatsapp", accountId: "biz" } },
  ],
}
```

### Binding Match Fields

- `match.channel` (required)
- `match.accountId` (optional; `*` = any account)
- `match.peer` (optional; `{ kind: direct|group|channel, id }`)
- `match.parentPeer` (optional; thread inheritance matching)
- `match.guildId` / `match.teamId` (optional)
- `match.roles` (optional; Discord role-based binding filters)

**Match order (8 levels):** peer > parentPeer > guildId+roles > guildId > teamId > accountId (exact) > channel > default agent.

**Caveats:**
- Never reuse `agentDir` across agents.
- `OPENCLAW_PROFILE` env var: workspace profile suffix.
- Credentials are NOT shared between agents.

## Per-Agent Access Profiles

### Full access (no sandbox)
```json5
{ id: "personal", sandbox: { mode: "off" } }
```

### Read-only
```json5
{
  id: "family",
  sandbox: { mode: "all", scope: "agent", workspaceAccess: "ro" },
  tools: {
    allow: ["read", "sessions_list", "sessions_history", "sessions_send", "sessions_spawn", "session_status"],
    deny: ["write", "edit", "apply_patch", "exec", "process", "browser"],
  },
}
```

### No filesystem (messaging only)
```json5
{
  id: "public",
  sandbox: { mode: "all", scope: "agent", workspaceAccess: "none" },
  tools: {
    allow: ["sessions_list", "sessions_history", "sessions_send", "sessions_spawn", "session_status", "whatsapp", "telegram", "slack", "discord", "gateway"],
    deny: ["read", "write", "edit", "apply_patch", "exec", "process", "browser", "canvas", "nodes", "cron", "gateway", "image"],
  },
}
```
