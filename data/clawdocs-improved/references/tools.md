# Tools Configuration Reference

## Table of Contents

- [Tool Profiles](#tool-profiles)
- [Tool Groups](#tool-groups)
- [Allow / Deny](#allow--deny)
- [By Provider](#by-provider)
- [Elevated Access](#elevated-access)
- [Exec](#exec)
- [Web Search and Fetch](#web-search-and-fetch)
- [Media](#media)
- [Agent-to-Agent](#agent-to-agent)
- [Subagents](#subagents)

## Tool Profiles

`tools.profile` sets a base allowlist:

| Profile | Includes |
|---------|----------|
| `minimal` | `session_status` only |
| `coding` | `group:fs`, `group:runtime`, `group:sessions`, `group:memory`, `image` |
| `messaging` | `group:messaging`, `sessions_list`, `sessions_history`, `sessions_send`, `session_status` |
| `full` | No restriction (same as unset) |

## Tool Groups

| Group | Tools |
|-------|-------|
| `group:runtime` | `exec`, `process` (`bash` is alias for `exec`) |
| `group:fs` | `read`, `write`, `edit`, `apply_patch` |
| `group:sessions` | `sessions_list`, `sessions_history`, `sessions_send`, `sessions_spawn`, `session_status` |
| `group:memory` | `memory_search`, `memory_get` |
| `group:web` | `web_search`, `web_fetch` |
| `group:ui` | `browser`, `canvas` |
| `group:automation` | `cron`, `gateway` |
| `group:messaging` | `message` |
| `group:nodes` | `nodes` |
| `group:openclaw` | All built-in tools (excludes provider plugins) |

## Allow / Deny

Global tool allow/deny policy (deny wins). Case-insensitive, supports `*` wildcards.

**Tool policy precedence chain:** Profile > Provider profile > Global policy > Provider policy > Agent policy > Provider agent policy > Sandbox policy > Subagent policy. Each level restricts further; earlier denials cannot be overridden.

```json5
{
  tools: {
    allow: ["exec", "process", "read", "write", "edit", "apply_patch"],
    deny: ["browser", "canvas"],
  },
}
```

## By Provider

Restrict tools for specific providers or models. Order: base profile > provider profile > allow/deny.

```json5
{
  tools: {
    profile: "coding",
    byProvider: {
      "google-antigravity": { profile: "minimal" },
      "openai/gpt-5.2": { allow: ["group:fs", "sessions_list"] },
    },
  },
}
```

## Elevated Access

Controls elevated (host) exec access:

```json5
{
  tools: {
    elevated: {
      enabled: true,
      allowFrom: {
        whatsapp: ["+15555550123"],
        discord: ["steipete", "1234567890123"],
      },
    },
  },
}
```

- Per-agent override can only further restrict.
- `/elevated on|off|ask|full` stores state per session.

## Exec

```json5
{
  tools: {
    exec: {
      backgroundMs: 10000,
      timeoutSec: 1800,
      cleanupMs: 1800000,
      notifyOnExit: true,
      applyPatch: {
        enabled: false,
        allowModels: ["gpt-5.2"],
      },
    },
  },
}
```

## Web Search and Fetch

```json5
{
  tools: {
    web: {
      search: {
        enabled: true,
        apiKey: "${BRAVE_API_KEY}",
        maxResults: 5,
        timeoutSeconds: 30,
        cacheTtlMinutes: 15,
      },
      fetch: {
        enabled: true,
        maxChars: 50000,
        maxCharsCap: 200000,
        timeoutSeconds: 30,
        cacheTtlMinutes: 15,
        userAgent: "custom-ua",
      },
    },
  },
}
```

## Media

Configures inbound media understanding (image/audio/video):

```json5
{
  tools: {
    media: {
      concurrency: 2,
      audio: {
        enabled: true,
        maxBytes: 20971520,
        scope: {
          default: "deny",
          rules: [{ action: "allow", match: { chatType: "direct" } }],
        },
        models: [
          { provider: "openai", model: "gpt-4o-mini-transcribe" },
          { type: "cli", command: "whisper", args: ["--model", "base", "{{MediaPath}}"] },
        ],
      },
      video: {
        enabled: true,
        maxBytes: 52428800,
        models: [{ provider: "google", model: "gemini-3-flash-preview" }],
      },
    },
  },
}
```

**Provider entry fields:** `provider`, `model`, `profile`, `capabilities` (image/audio/video).
**CLI entry fields:** `command`, `args`, `timeoutSeconds`, `maxChars`.

Failures fall back to the next entry.

### Media model template variables

| Variable | Description |
|----------|-------------|
| `{{MediaPath}}` | Local temp file path of the inbound media |
| `{{MediaDir}}` | Directory containing the media file |
| `{{MediaUrl}}` | Pseudo-URL for the inbound media |
| `{{MediaUrls}}` | All media URLs (multi-attachment) |
| `{{MediaPaths}}` | All media file paths (multi-attachment) |
| `{{MediaTypes}}` | MIME types of all media attachments |
| `{{Prompt}}` | The prompt/caption sent with the media |
| `{{MaxChars}}` | Maximum characters for output |
| `{{OutputDir}}` | Scratch directory created for this run |
| `{{OutputBase}}` | Scratch file base path (no extension) |
| `{{Transcript}}` | Transcription output (audio only) |

When sandbox is enabled, `MediaPath`/`MediaUrl` are rewritten to sandbox-relative paths like `media/inbound/<filename>`.

### Per-media-type config

Each media type (`image`, `audio`, `video`) supports:

| Key | Type | Description |
|-----|------|-------------|
| `enabled` | boolean | Enable/disable this media type |
| `prompt` | string | Default prompt for understanding |
| `maxChars` | number | Max output characters |
| `maxBytes` | number | Max file size in bytes |
| `timeoutSeconds` | number | Processing timeout |
| `language` | string | Language hint |
| `baseUrl` | string | Custom API base URL |
| `headers` | object | Custom HTTP headers |
| `providerOptions` | object | Provider-specific options (e.g., `deepgram`) |
| `attachments.mode` | string | `first` or `all` |
| `attachments.maxAttachments` | number | Max attachments to process |
| `attachments.prefer` | string | `first`, `last`, `path`, or `url` |
| `scope.default` | string | `allow` or `deny` |
| `scope.rules[]` | array | `{action, match}` rules (match by `chatType`: `direct`, `group`) |

**Model entry types:** `provider` (API) or `cli` (local command).

**Supported providers:** `openai`, `anthropic`, `google`, `groq`, `deepgram`, `minimax`.

## Agent-to-Agent

```json5
{
  tools: {
    agentToAgent: {
      enabled: false,
      allow: ["home", "work"],
    },
  },
}
```

## Subagents

```json5
{
  agents: {
    defaults: {
      subagents: {
        model: "minimax/MiniMax-M2.1",
        maxConcurrent: 1,
        archiveAfterMinutes: 60,
      },
    },
  },
}
```

- `model`: default model for spawned sub-agents. If omitted, inherits caller's model.
- Per-subagent tool policy: `tools.subagents.tools.allow` / `tools.subagents.tools.deny`.
- Per-agent sandbox tools: `agents.list[].tools.sandbox.tools` replaces global `tools.sandbox.tools`.
