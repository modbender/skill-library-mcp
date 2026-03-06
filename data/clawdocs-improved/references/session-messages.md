# Session & Messages Configuration Reference

## Table of Contents

- [Session](#session)
- [Messages](#messages)
- [Commands](#commands)
- [TTS](#tts)
- [Talk Mode](#talk-mode)

## Session

```json5
{
  session: {
    scope: "per-sender",
    dmScope: "main", // main | per-peer | per-channel-peer | per-account-channel-peer
    identityLinks: {
      alice: ["telegram:123456789", "discord:987654321012345678"],
    },
    reset: {
      mode: "daily", // daily | idle
      atHour: 4,
      idleMinutes: 60,
    },
    resetByType: {
      thread: { mode: "daily", atHour: 4 },
      direct: { mode: "idle", idleMinutes: 240 },
      group: { mode: "idle", idleMinutes: 120 },
    },
    resetByChannel: {
      whatsapp: { mode: "idle", idleMinutes: 120 },
      discord: { mode: "daily", atHour: 4 },
    },
    resetTriggers: ["/new", "/reset"],
    store: "~/.openclaw/agents/{agentId}/sessions/sessions.json",
    maintenance: {
      mode: "warn", // warn | enforce
      pruneAfter: "30d",
      maxEntries: 500,
      rotateBytes: "10mb",
    },
    agentToAgent: { maxPingPongTurns: 5 },
    sendPolicy: {
      rules: [{ action: "deny", match: { channel: "discord", chatType: "group" } }],
      default: "allow",
    },
  },
}
```

- `mainKey`: legacy field with default `"main"`. Runtime ignores it for session routing, but sandbox `mode: "non-main"` still references this value to determine main vs non-main sessions.

### dmScope

| Value | Behavior |
|-------|----------|
| `main` | All DMs share the main session |
| `per-peer` | Isolate by sender id across channels |
| `per-channel-peer` | Isolate per channel + sender (recommended for multi-user) |
| `per-account-channel-peer` | Isolate per account + channel + sender (recommended for multi-account) |

### identityLinks

Map canonical ids to provider-prefixed peers for cross-channel session sharing.

### reset

`daily` resets at `atHour` local time; `idle` resets after `idleMinutes`. When both `atHour` and `idleMinutes` are set in the same reset block, whichever expires first wins.

- **Deprecation:** `resetByType.dm` is an alias for `resetByType.direct`; prefer `direct`.

### sendPolicy

Match by `channel`, `chatType` (`direct|group|channel`), `keyPrefix`, or `rawKeyPrefix` (matches the full key including `agent:<id>:` prefix). First deny wins.

### Session key formats

| Pattern | Used for |
|---------|----------|
| `agent:<agentId>:main` | Main direct-chat session |
| `cron:<job.id>` | Cron job sessions |
| `hook:<uuid>` | Webhook-triggered sessions |
| `node-<nodeId>` | Node sessions |

### Security note

If your agent can receive DMs from **multiple people**, you should strongly consider enabling secure DM mode: set `dmScope` to `"per-channel-peer"` or `"per-account-channel-peer"`.

### Session transcripts

Stored at `~/.openclaw/agents/{agentId}/sessions/<SessionId>.jsonl`. Telegram topic variant: `<SessionId>-topic-<threadId>.jsonl`.

## Messages

```json5
{
  messages: {
    responsePrefix: "auto", // string, "auto", or ""
    ackReaction: "👀",
    ackReactionScope: "group-mentions", // group-mentions | group-all | direct | all
    removeAckAfterReply: false,
    queue: {
      mode: "collect", // steer | followup | collect | steer-backlog | steer+backlog | queue | interrupt
      debounceMs: 1000,
      cap: 20,
      drop: "summarize", // old | new | summarize
      byChannel: {
        whatsapp: "collect",
        telegram: "collect",
      },
    },
    inbound: {
      debounceMs: 2000,
      byChannel: {
        whatsapp: 5000,
        slack: 1500,
      },
    },
  },
}
```

### Response prefix template variables

| Variable | Description |
|----------|-------------|
| `{model}` | Short model name |
| `{modelFull}` | Full model identifier |
| `{provider}` | Provider name |
| `{thinkingLevel}` | Current thinking level |
| `{identity.name}` | Agent identity name |

### Inbound debounce

Batches rapid text-only messages from same sender. Media/attachments flush immediately. Control commands bypass debouncing.

- **Deprecation:** Legacy `messages.ackReaction` is superseded by per-channel `channels.<provider>.ackReaction`; the global key is still honored as fallback.

## Commands

```json5
{
  commands: {
    native: "auto",
    text: true,
    bash: false,
    bashForegroundMs: 2000,
    config: false,
    debug: false,
    restart: false,
    allowFrom: {
      "*": ["user1"],
      discord: ["user:123"],
    },
    useAccessGroups: true,
  },
}
```

- `native: "auto"` turns on native commands for Discord/Telegram, leaves Slack off.
- `bash: true` enables `! <cmd>` for host shell (requires `tools.elevated.enabled`).
- `config: true` enables `/config` (reads/writes `openclaw.json`).

## TTS

```json5
{
  messages: {
    tts: {
      auto: "always", // off | always | inbound | tagged
      mode: "final", // final | all
      provider: "elevenlabs",
      summaryModel: "openai/gpt-5.2-mini",
      maxTextLength: 4000,
      timeoutMs: 30000,
      prefsPath: "~/.openclaw/tts-prefs.json",
      modelOverrides: { enabled: false },
      elevenlabs: {
        apiKey: "${ELEVENLABS_API_KEY}",
        baseUrl: "https://api.elevenlabs.io",
        voiceId: "voice_id",
        modelId: "eleven_multilingual_v2",
        seed: 0,
        applyTextNormalization: "auto",
        languageCode: "",
        voiceSettings: {
          stability: 0.5,
          similarityBoost: 0.75,
          speed: 1.0,
          style: 0,
          useSpeakerBoost: true,
        },
      },
      openai: {
        apiKey: "${OPENAI_API_KEY}",
        model: "gpt-4o-mini-tts",
        voice: "alloy",
      },
    },
  },
}
```

## Talk Mode

```json5
{
  talk: {
    voiceId: "elevenlabs_voice_id",
    voiceAliases: {
      Clawd: "EXAVITQu4vr4xnSDxMaL",
      Roger: "CwhRBWXzGAHq8TQ4Fs17",
    },
    modelId: "eleven_v3",
    outputFormat: "mp3_44100_128",
    apiKey: "${ELEVENLABS_API_KEY}",
    interruptOnSpeech: true,
  },
}
```
