# Channels Configuration Reference

All channel config lives under `channels.<provider>`. Each channel starts automatically when its config section exists (unless `enabled: false`).

## Table of Contents

- [DM and Group Access Policies](#dm-and-group-access-policies)
- [WhatsApp](#whatsapp)
- [Telegram](#telegram)
- [Discord](#discord)
- [Google Chat](#google-chat)
- [Slack](#slack)
- [Mattermost](#mattermost)
- [Signal](#signal)
- [iMessage](#imessage)
- [BlueBubbles](#bluebubbles)
- [MS Teams](#ms-teams)
- [Multi-Account](#multi-account)
- [Group Chat Mention Gating](#group-chat-mention-gating)
- [DM History Limits](#dm-history-limits)
- [Self-Chat Mode](#self-chat-mode)
- [Channel Heartbeat Overrides](#channel-heartbeat-overrides)

## DM and Group Access Policies

All channels support these policies:

| DM Policy | Behavior |
|-----------|----------|
| `pairing` (default) | Unknown senders get a one-time pairing code; owner must approve |
| `allowlist` | Only senders in `allowFrom` (or paired allow store) |
| `open` | Allow all inbound DMs (requires `allowFrom: ["*"]`) |
| `disabled` | Ignore all inbound DMs |

| Group Policy | Behavior |
|-------------|----------|
| `allowlist` (default) | Only groups matching the configured allowlist |
| `open` | Bypass group allowlists (mention-gating still applies) |
| `disabled` | Block all group/room messages |

`channels.defaults.groupPolicy` sets the default when a provider's `groupPolicy` is unset. Pairing codes expire after 1 hour. Pending DM pairing requests are capped at 3 per channel.

## WhatsApp

Runs through the gateway's web channel (Baileys Web). Starts automatically when a linked session exists.

```json5
{
  channels: {
    whatsapp: {
      dmPolicy: "pairing",
      allowFrom: ["+15555550123", "+447700900123"],
      configWrites: true,
      debounceMs: 2000,
      historyLimit: 50,
      dmHistoryLimit: 30,
      textChunkLimit: 4000,
      chunkMode: "length", // length | newline
      mediaMaxMb: 50,
      sendReadReceipts: true,
      selfChatMode: false,
      gifPlayback: false, // animate GIFs via video sends
      ackReaction: {
        emoji: "👀",
        direct: true, // boolean: true | false (not string enum)
        group: "mentions", // always | mentions | never
      },
      actions: { reactions: true, polls: true },
      session: { dmScope: "main" },
      groups: {
        "*": { requireMention: true },
      },
      groupPolicy: "allowlist",
      groupAllowFrom: ["+15551234567"],
    },
  },
  web: {
    enabled: true,
    heartbeatSeconds: 60,
    reconnect: {
      initialMs: 2000,
      maxMs: 120000,
      factor: 1.4,
      jitter: 0.2,
      maxAttempts: 0,
    },
  },
}
```

**Caveats:**
- Baileys-only: no separate Twilio WhatsApp messaging channel in built-in registry.
- **Node.js required.** Bun runtime is incompatible.
- Quote replies satisfy mention gating but do not grant sender authorization.
- `web.*` fields (`web.enabled`, `web.heartbeatSeconds`, `web.reconnect.*`) are top-level, NOT under `channels.whatsapp`.

### Multi-account WhatsApp

```json5
{
  channels: {
    whatsapp: {
      accounts: {
        default: { enabled: true, authDir: "~/.openclaw/credentials/whatsapp/default/" },
        personal: { enabled: true },
        biz: { enabled: true },
      },
    },
  },
}
```

- Outbound commands default to account `default` if present; otherwise the first configured account id (sorted).
- Per-account overrides: `sendReadReceipts`, `authDir`, `dmPolicy`, `allowFrom`.
- Default `authDir`: `~/.openclaw/credentials/whatsapp/<accountId>/`.

## Telegram

```json5
{
  channels: {
    telegram: {
      enabled: true,
      botToken: "your-bot-token",
      dmPolicy: "pairing",
      allowFrom: ["tg:123456789"],
      groupPolicy: "allowlist",
      groupAllowFrom: ["tg:123456789"],
      capabilities: { inlineButtons: "allowlist" }, // off | dm | group | all | allowlist
      timeoutSeconds: 60,
      webhookHost: "127.0.0.1",
      blockStreaming: false,
      reactionLevel: "minimal", // off | ack | minimal | extensive
      groups: {
        "*": { requireMention: true, enabled: true, groupPolicy: "allowlist" },
        "-1001234567890": {
          allowFrom: ["@admin"],
          systemPrompt: "Keep answers brief.",
          skills: ["search"],
          topics: {
            "99": {
              enabled: true, // per-topic enable/disable
              requireMention: false,
              skills: ["search"],
              systemPrompt: "Stay on topic.",
            },
          },
        },
      },
      customCommands: [
        { command: "backup", description: "Git backup" },
        { command: "generate", description: "Create an image" },
      ],
      streaming: "partial", // off | partial | block | progress ("progress" maps to "partial" on Telegram)
      configWrites: true,
      dmHistoryLimit: 30,
      historyLimit: 50,
      textChunkLimit: 4000,
      chunkMode: "length", // length | newline
      replyToMode: "first", // off | first | all
      linkPreview: true,
      streamMode: "partial", // off | partial | block (legacy; prefer "streaming")
      draftChunk: {
        minChars: 200,
        maxChars: 800,
        breakPreference: "paragraph", // paragraph | newline | sentence
      },
      actions: { reactions: true, sendMessage: true, editMessage: true, deleteMessage: true, sticker: false },
      reactionNotifications: "own", // off | own | all
      mediaMaxMb: 5,
      retry: {
        attempts: 3,
        minDelayMs: 400,
        maxDelayMs: 30000,
        jitter: 0.1,
      },
      network: { autoSelectFamily: false },
      proxy: "socks5://localhost:9050",
      webhookUrl: "https://example.com/telegram-webhook",
      webhookSecret: "secret",
      webhookPath: "/telegram-webhook",
    },
  },
}
```

- Bot token: `channels.telegram.botToken` or `channels.telegram.tokenFile` (reads token from file), with `TELEGRAM_BOT_TOKEN` as env fallback.
- `configWrites: false` blocks Telegram-initiated config writes.
- Legacy `capabilities: ["inlineButtons"]` maps to `inlineButtons: "all"`; prefer explicit scope.
- `ackReaction`: channel-level ack emoji (unicode string). Resolution: account-specific > channel > `messages` global > agent emoji fallback. Set `""` to disable.
- `dms["<user_id>"].historyLimit`: per-user DM history override.
- Topic sessions: general topic (`threadId=1`) omits `message_thread_id` on sends. Topic session keys append `:topic:<threadId>`.
- Template context variables: `IsForum` (boolean), `MessageThreadId` (thread ID in topic messages).
- `[[audio_as_voice]]` tag forces voice-note send; `asVideoNote: true` sends video notes.
- `[[reply_to_current]]` and `[[reply_to:<id>]]` tags are honored even when `replyToMode: "off"`.
- Command normalization: strip `/`, lowercase, pattern `a-z0-9_`, length 1-32.
- Sticker cache: `~/.openclaw/telegram/sticker-cache.json`.

**Caveats:**
- Privacy mode must be disabled or bot must be admin for non-mention group messages.
- Node 22+ `AbortSignal` type mismatches can cause immediate abort behavior.
- IPv6 egress issues may cause intermittent API failures.
- `/reasoning stream` sends reasoning tokens to live preview during streaming.

## Discord

```json5
{
  channels: {
    discord: {
      enabled: true,
      token: "your-bot-token",
      status: "Listening to messages",
      activity: "OpenClaw",
      activityType: 2, // 0=Playing|1=Streaming|2=Listening|3=Watching|4=Custom|5=Competing
      activityUrl: "",
      proxy: "socks5://localhost:9050",
      intents: [],
      dmPolicy: "pairing", // modern field; legacy dm.policy also honored
      allowFrom: ["1234567890", "steipete"], // modern top-level; legacy dm.allowFrom also honored
      groupPolicy: "allowlist", // defaults to "open" if only token provided; "allowlist" if config block exists
      streaming: "off", // off | partial | block | progress
      ackReaction: "👀", // unicode emoji or custom emoji name; "" to disable
      configWrites: true,
      responsePrefix: "auto",
      mediaMaxMb: 8,
      allowBots: false,
      agentComponents: {},
      heartbeat: {},
      commands: { native: "auto", useAccessGroups: false },
      pluralkit: { enabled: false, token: "" },
      draftChunk: {
        minChars: 200,
        maxChars: 800,
        breakPreference: "paragraph", // paragraph | newline | sentence
      },
      blockStreaming: false,
      blockStreamingCoalesce: { idleMs: 1000 },
      voice: {
        enabled: false,
        autoJoin: false,
        tts: { provider: "openai", openai: { voice: "alloy" } },
      },
      threadBindings: {
        enabled: false,
        ttlHours: 24,
        spawnSubagentSessions: false,
      },
      slashCommand: { ephemeral: true },
      execApprovals: {
        enabled: false,
        approvers: ["987654321098765432"],
        agentFilter: "*",
        sessionFilter: "*",
        cleanupAfterResolve: true,
        target: "dm", // dm | channel | both
      },
      ui: { components: { accentColor: "#FF4500" } },
      actions: {
        reactions: true,
        stickers: true,
        polls: true,
        permissions: true,
        messages: true,
        threads: true,
        pins: true,
        search: true,
        memberInfo: true,
        roleInfo: true,
        roles: false,
        channelInfo: true,
        voiceStatus: true,
        events: true,
        moderation: false,
        channels: true,
        emojiUploads: false,
        stickerUploads: false,
        presence: true,
      },
      replyToMode: "off", // off | first | all
      dm: {
        enabled: true,
        policy: "pairing", // legacy; prefer top-level dmPolicy
        allowFrom: ["1234567890", "steipete"], // legacy; prefer top-level allowFrom
        groupEnabled: false, // group DM handling
        groupChannels: ["openclaw-dm"], // group DM channel allowlist
        historyLimit: 50,
      },
      dms: {
        "1234567890": { historyLimit: 100 },
      },
      guilds: {
        "123456789012345678": {
          slug: "friends-of-openclaw",
          requireMention: false,
          reactionNotifications: "own",
          users: ["987654321098765432"],
          roles: ["111222333444555666"],
          channels: {
            general: { allow: true },
            help: {
              allow: true,
              requireMention: true,
              users: ["987654321098765432"], // per-channel user allowlist
              skills: ["docs"], // per-channel skill filtering
              systemPrompt: "Short answers only.", // per-channel system prompt
            },
          },
        },
      },
      historyLimit: 20,
      textChunkLimit: 2000,
      chunkMode: "length",
      maxLinesPerMessage: 17,
      retry: {
        attempts: 3,
        minDelayMs: 500,
        maxDelayMs: 30000,
        jitter: 0.1,
      },
    },
  },
}
```

- Token: `channels.discord.token`, fallback `DISCORD_BOT_TOKEN`.
- Use `user:<id>` (DM) or `channel:<id>` (guild channel) for delivery targets.
- Guild slugs are lowercase with `-`; channel keys use slugged name (no `#`). Prefer guild IDs.
- `maxLinesPerMessage` (default 17) splits tall messages even under 2000 chars.
- Per-account overrides: `ackReaction`, `proxy`, `ui.components.accentColor`.
- Agent routing via bindings: `bindings[].match.channel`, `bindings[].match.guildId`, `bindings[].match.roles`.

**Caveats:**
- Forum channels only accept thread posts; use explicit thread creation APIs.
- Voice messages require `ffmpeg` and `ffprobe` for waveform generation.

**Reaction notification modes:** `off`, `own` (default), `all`, `allowlist` (from `guilds.<id>.users`).

## Google Chat

```json5
{
  channels: {
    googlechat: {
      enabled: true,
      serviceAccountFile: "/path/to/service-account.json",
      audienceType: "app-url", // app-url | project-number
      audience: "https://gateway.example.com/googlechat",
      webhookPath: "/googlechat",
      botUser: "users/1234567890",
      dm: {
        enabled: true,
        policy: "pairing",
        allowFrom: ["users/1234567890"],
      },
      groupPolicy: "allowlist",
      groups: {
        "spaces/AAAA": {
          allow: true,
          requireMention: true,
          users: ["users/1234567890"], // per-space user allowlist
          systemPrompt: "Be concise.", // per-space custom instructions
        },
      },
      actions: { reactions: true },
      typingIndicator: "message", // none | message | reaction ("reaction" requires user OAuth)
      mediaMaxMb: 20,
    },
  },
}
```

- Env fallbacks: `GOOGLE_CHAT_SERVICE_ACCOUNT` or `GOOGLE_CHAT_SERVICE_ACCOUNT_FILE`.
- `serviceAccount`: inline JSON object alternative to `serviceAccountFile`.
- `audienceType` value must match your Chat app configuration.
- `dm.allowFrom`: email addresses are "mutable principals"; prefer user IDs.
- Attachments are downloaded through the Chat API.
- `historyLimit`, `dmHistoryLimit`, `textChunkLimit`, `chunkMode`, `configWrites`: verify if supported for Google Chat.
- Use `spaces/<spaceId>` or `users/<userId|email>` for delivery targets.

## Slack

```json5
{
  channels: {
    slack: {
      enabled: true,
      mode: "socket", // socket | http
      botToken: "xoxb-...",
      appToken: "xapp-...",
      signingSecret: "signing-secret",
      userToken: "xoxp-...",
      userTokenReadOnly: true,
      webhookPath: "/slack/events", // default for HTTP mode
      configWrites: true,
      dmPolicy: "pairing", // modern field; legacy dm.policy also honored
      allowFrom: ["U123", "U456", "*"], // modern top-level; legacy dm.allowFrom also honored
      groupPolicy: "open", // defaults to "open" (with warning if unset)
      streaming: "partial", // off | partial | block | progress (default "partial" for Slack)
      nativeStreaming: true, // use Slack native streaming API
      ackReaction: "eyes", // emoji shortcode; falls back to agent identity emoji; "" to disable
      commands: { native: false }, // global commands.native: "auto" does NOT enable Slack native commands; must use channels.slack.commands.native: true
      dm: {
        enabled: true,
        policy: "pairing", // legacy; prefer top-level dmPolicy
        allowFrom: ["U123", "U456", "*"], // legacy; prefer top-level allowFrom
        groupEnabled: false, // MPIM (multi-person DM) support
        groupChannels: ["G123"], // MPIM channel allowlist
        replyToMode: "off", // legacy per-DM reply mode
      },
      channels: {
        C123: { allow: true, requireMention: true, allowBots: false },
        "#general": {
          allow: true,
          requireMention: true,
          users: ["U123"],
          skills: ["docs"],
          systemPrompt: "Short answers only.",
          tools: { allow: ["read"], deny: ["exec"] },
          toolsBySender: { "U123": { allow: ["exec"] } },
        },
      },
      historyLimit: 50,
      allowBots: false,
      reactionNotifications: "own",
      reactionAllowlist: ["U123"],
      replyToMode: "off",
      replyToModeByChatType: {},
      thread: {
        historyScope: "thread", // thread | channel
        inheritParent: false,
        initialHistoryLimit: 20,
      },
      actions: {
        reactions: true,
        messages: true,
        pins: true,
        memberInfo: true,
        emojiList: true,
      },
      slashCommand: {
        enabled: true,
        name: "openclaw",
        sessionPrefix: "slack:slash",
        ephemeral: true,
      },
      textChunkLimit: 4000,
      chunkMode: "length",
      mediaMaxMb: 20,
      accounts: {},
    },
  },
}
```

- **Socket mode** requires `botToken` + `appToken` (`SLACK_BOT_TOKEN` + `SLACK_APP_TOKEN` env fallback).
- **HTTP mode** requires `botToken` + `signingSecret`.
- Use `user:<id>` (DM) or `channel:<id>` for delivery targets.
- Per-channel `tools`: `{ allow: [...], deny: [...] }` structure for per-channel tool allowlists.
- Per-channel `toolsBySender`: per-sender tool filtering within a channel.
- `replyToModeByChatType`: per-chat-type reply override object.
- `thread.historyScope`: `"thread"` (default) scopes history to thread messages only.
- `thread.inheritParent`: inherit parent session context in threads.
- Required bot token scopes: `chat:write`, `channels:history`, `groups:history`, `im:history`, `mpim:history`, `users:read`, `app_mentions:read`, `reactions:read/write`, `pins:read/write`, `emoji:read`, `commands`, `files:read/write`, `assistant:write`.
- Streaming requires: Agents and AI Apps enabled, `assistant:write` scope, reply thread available.

## Mattermost

Plugin: `openclaw plugins install @openclaw/mattermost`.

```json5
{
  channels: {
    mattermost: {
      enabled: true,
      botToken: "mm-token", // env fallback: MATTERMOST_BOT_TOKEN
      baseUrl: "https://chat.example.com", // env fallback: MATTERMOST_URL
      dmPolicy: "pairing",
      allowFrom: ["*"], // DM allowlist; "*" for open DMs
      groupPolicy: "allowlist", // allowlist | open (default "allowlist")
      groupAllowFrom: ["@username", "user-id"], // user IDs or @username format
      chatmode: "oncall", // oncall | onmessage | onchar
      oncharPrefixes: [">", "!"],
      textChunkLimit: 4000,
      chunkMode: "length",
      actions: { reactions: true },
      accounts: {
        default: { name: "Main", botToken: "token", baseUrl: "https://chat.example.com" },
      },
    },
  },
}
```

- Env vars (`MATTERMOST_BOT_TOKEN`, `MATTERMOST_URL`) apply to default account only.
- Target formats: `channel:<id>`, `user:<id>`, `@username`. Bare IDs treated as channels.
- @mentions always trigger responses regardless of chatmode.
```

## Signal

```json5
{
  channels: {
    signal: {
      enabled: true,
      account: "+15551234567",
      cliPath: "signal-cli",
      httpUrl: "http://127.0.0.1:8080",
      httpHost: "127.0.0.1",
      httpPort: 8080,
      autoStart: true,
      startupTimeoutMs: 120000,
      dmPolicy: "pairing",
      allowFrom: ["+15551234567", "uuid:<id>"], // phone numbers or uuid:<id> format
      groupPolicy: "allowlist",
      groupAllowFrom: ["+15551234567"],
      receiveMode: "on-start", // on-start | manual
      textChunkLimit: 4000,
      chunkMode: "length",
      historyLimit: 50,
      dmHistoryLimit: 30,
      dms: {
        "+15559876543": { historyLimit: 50 },
      },
      mediaMaxMb: 8,
      ignoreAttachments: false,
      ignoreStories: false,
      sendReadReceipts: false, // default is false
      configWrites: true,
      actions: { reactions: true },
      reactionLevel: "minimal", // off | ack | minimal | extensive
      reactionNotifications: "own", // off | own | all | allowlist (verify if exists for Signal)
      reactionAllowlist: ["+15551234567"], // verify if exists for Signal
      accounts: {
        default: {
          historyLimit: 50, // per-account history override
          "actions.reactions": true, // per-account reaction enable
          reactionLevel: "minimal", // per-account reaction level
        },
      },
    },
  },
}
```

**Caveats:**
- Loop protection ignores messages from the bot's own number.
- Registering a number can de-authenticate the main Signal app session for that number.
- Account key storage: `~/.local/share/signal-cli/data/` — back up before migration.
- Group reactions require `targetAuthor` or `targetAuthorUuid`.
- DM phone numbers in `dms` keys should use `+` prefix (e.g. `"+15559876543"`).

## iMessage

OpenClaw spawns `imsg rpc` (JSON-RPC over stdio). No daemon or port required.

```json5
{
  channels: {
    imessage: {
      enabled: true,
      cliPath: "imsg",
      dbPath: "~/Library/Messages/chat.db",
      remoteHost: "user@gateway-host",
      dmPolicy: "pairing",
      allowFrom: ["+15555550123", "user@example.com", "chat_id:123", "chat_guid:*", "chat_identifier:*"],
      groupPolicy: "allowlist", // allowlist | open | disabled
      historyLimit: 50,
      groupAllowFrom: ["+15555550123"],
      attachmentRoots: ["/Users/*/Library/Messages/Attachments"], // local attachment path allowlist
      remoteAttachmentRoots: ["/Users/*/Library/Messages/Attachments"], // remote SCP attachment path allowlist
      groups: {},
      includeAttachments: false,
      mediaMaxMb: 16,
      textChunkLimit: 4000,
      chunkMode: "length",
      configWrites: true,
      service: "auto",
      region: "US",
      accounts: {},
    },
  },
}
```

- Requires Full Disk Access **and** Automation permissions to Messages DB.
- Remote SCP requires strict host-key checking; Mac host key must exist in `~/.ssh/known_hosts`.
- iMessage has no native mention metadata; relies on regex patterns.
- Prefer `chat_id:<id>` targets. Use `imsg chats --limit 20` to list chats.
- `service`: verify if this field exists (in example but not in docs).
- `region`: verify if this field exists (in example but not in docs).
- Per-account overrides: `cliPath`, `dbPath`, `allowFrom`, `groupPolicy`, `mediaMaxMb`, `historyLimit`, `attachmentRoots`.
- **Deprecation:** iMessage "imsg" integration is legacy and may be removed. Use BlueBubbles instead.

## BlueBubbles

```json5
{
  channels: {
    bluebubbles: {
      enabled: true,
      serverUrl: "http://192.168.1.100:1234",
      password: "${BLUEBUBBLES_PASSWORD}",
      webhookPath: "/bluebubbles-webhook",
      dmPolicy: "allowlist",
      allowFrom: ["+15555550123"],
      groupPolicy: "allowlist",
      groupAllowFrom: ["+15555550123"],
      groups: {
        "chat-guid": { requireMention: true }, // per-group config by group GUID
      },
      mediaLocalRoots: [], // allowlist for outbound local file paths
      sendReadReceipts: true,
      blockStreaming: false,
      textChunkLimit: 4000,
      chunkMode: "length", // length | newline
      mediaMaxMb: 8,
      historyLimit: 50,
      dmHistoryLimit: 30,
      actions: {
        reactions: true,
        edit: true,
        unsend: true,
        reply: true,
        sendWithEffect: true,
        renameGroup: true,
        setGroupIcon: true,
        addParticipant: true,
        removeParticipant: true,
        leaveGroup: true,
        sendAttachment: true,
      },
      accounts: {},
    },
  },
}
```

- Per-account overrides: `mediaLocalRoots`.
- `actions.unsend` requires macOS 13+.
- `setGroupIcon`: API may succeed but icon doesn't sync on macOS 26 Tahoe.
- **Note:** `edit` action currently broken on macOS 26 Tahoe.
- Short message IDs expire on restart; use full IDs (`MessageSidFull`, `ReplyToIdFull`) for durable automations.
- Webhook auth: compares `guid`/`password` query params or headers against configured password; localhost requests also accepted. Related: `gateway.trustedProxies` for reverse proxy authentication.

## MS Teams

Plugin: `openclaw plugins install @openclaw/msteams`.

```json5
{
  channels: {
    msteams: {
      enabled: true,
      appId: "${MSTEAMS_APP_ID}",
      appPassword: "${MSTEAMS_APP_PASSWORD}",
      tenantId: "${MSTEAMS_TENANT_ID}",
      webhook: { port: 3978, path: "/api/messages" },
      dmPolicy: "pairing",
      allowFrom: ["user@org.com"],
      groupPolicy: "allowlist",
      groupAllowFrom: ["user@org.com"],
      requireMention: true,
      replyStyle: "thread", // thread | top-level
      textChunkLimit: 2000,
      chunkMode: "length",
      mediaAllowHosts: ["*"],
      mediaAuthAllowHosts: ["graph.microsoft.com"],
      sharePointSiteId: "contoso.sharepoint.com,guid1,guid2",
      configWrites: true,
      historyLimit: 50,
      dmHistoryLimit: 10,
      mediaMaxMb: 20,
      dms: {
        "<user_id>": { historyLimit: 100 }, // per-user DM history override
      },
      teams: {
        "My Team": {
          replyStyle: "top-level",
          requireMention: false,
          tools: { allow: ["tool1"], deny: ["tool2"], alsoAllow: ["tool3"] },
          toolsBySender: { "*": { allow: ["exec"] } }, // per-sender tool policy; "*" wildcard
          channels: {
            "General": {
              requireMention: true,
              replyStyle: "thread",
              tools: { allow: ["tool1"], deny: ["tool2"] },
              toolsBySender: { "<user_id>": { allow: ["exec"] } }, // per-channel per-sender
            },
          },
        },
      },
    },
  },
}
```

- Env fallbacks: `MSTEAMS_APP_ID`, `MSTEAMS_APP_PASSWORD`, `MSTEAMS_TENANT_ID`.
- Per-team and per-channel overrides: `replyStyle`, `requireMention`, `tools`, `toolsBySender`.
- `replyStyle`: `thread` (default) or `top-level`.
- `allowFrom` formats: AAD object IDs, UPNs, or display names. Wizard resolves names to IDs.
- `groupAllowFrom` falls back to `channels.msteams.allowFrom`.
- `groupPolicy` falls back to `channels.defaults.groupPolicy`.
- Graph permissions required for channel/group image/file contents, message history, and per-user sharing links.

**Caveats:**
- Webhook timeout: long LLM responses may cause retries; OpenClaw mitigates by replying proactively.
- Private channels: limited bot support; real-time messages may not work.
- Manifest version: increment `version` field when updating; reinstall app and fully quit Teams to refresh.
- Team/channel ID extraction: extract from URL path (not `groupId` query parameter); URL-decode before use.

## Multi-Account

All channels support multiple accounts:

```json5
{
  channels: {
    telegram: {
      accounts: {
        default: {
          name: "Primary bot",
          botToken: "123456:ABC...",
        },
        alerts: {
          name: "Alerts bot",
          botToken: "987654:XYZ...",
        },
      },
    },
  },
}
```

- `default` is used when `accountId` is omitted.
- Env tokens only apply to the **default** account.
- Use `bindings[].match.accountId` to route each account to a different agent.

## Group Chat Mention Gating

Group messages default to **require mention**. Mention types:
- **Metadata mentions**: Native platform @-mentions.
- **Text patterns**: Regex patterns in `agents.list[].groupChat.mentionPatterns`.

```json5
{
  messages: {
    groupChat: { historyLimit: 50 },
  },
  agents: {
    list: [{ id: "main", groupChat: { mentionPatterns: ["@openclaw", "openclaw"] } }],
  },
}
```

## DM History Limits

```json5
{
  channels: {
    telegram: {
      dmHistoryLimit: 30,
      dms: {
        "123456789": { historyLimit: 50 },
      },
    },
  },
}
```

Resolution: per-DM override > provider default > no limit.

## Self-Chat Mode

Include your own number in `allowFrom` to enable (ignores native @-mentions, only responds to text patterns):

```json5
{
  channels: {
    whatsapp: {
      allowFrom: ["+15555550123"],
      groups: { "*": { requireMention: true } },
    },
  },
  agents: {
    list: [{ id: "main", groupChat: { mentionPatterns: ["reisponde", "@openclaw"] } }],
  },
}
```

## Retry Behavior

Retries apply **per individual request** (message send, media upload, reaction, poll, sticker), not across multi-step workflows.

**Per-channel retry specifics:**
- **Discord:** retries only on HTTP 429 (rate-limit). Uses `retry_after` response header for delay.
- **Telegram:** retries on 429, timeouts, connection errors, temporary unavailability. Markdown parse errors are NOT retried (falls back to plain text). Uses `retry_after` when available.

## Channel Heartbeat Overrides

Per-channel and per-account heartbeat delivery settings:

```json5
{
  channels: {
    defaults: {
      heartbeat: {
        showOk: false,
        showAlerts: true,
        useIndicator: true,
      },
    },
    whatsapp: {
      heartbeat: { showOk: true },
      accounts: {
        biz: { heartbeat: { showAlerts: false } },
      },
    },
  },
}
```
