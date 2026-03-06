# Channels Schema（渠道配置）

## 通用字段

### DM Policy（所有渠道）

| 字段 | 类型 | 有效值 | 默认值 |
|---|---|---|---|
| `dmPolicy` | string | `pairing` \| `allowlist` \| `open` \| `disabled` | `pairing` |
| `allowFrom` | array | 渠道特定的 ID 格式 | `[]` |

### Group Policy（所有渠道）

| 字段 | 类型 | 有效值 | 默认值 |
|---|---|---|---|
| `groupPolicy` | string | `allowlist` \| `open` \| `disabled` | `allowlist` |
| `groups` | object | 渠道特定的配置 | `{}` |

---

## Telegram

```json5
{
  channels: {
    telegram: {
      enabled: true,
      botToken: "your-bot-token",
      dmPolicy: "pairing",
      allowFrom: ["tg:123456789"],
      groups: {
        "*": { requireMention: true },
      },
      customCommands: [
        { command: "backup", description: "Git backup" },
      ],
      historyLimit: 50,
      replyToMode: "first",  // off | first | all
      linkPreview: true,
      streaming: "partial",  // off | partial | block | progress
      actions: { reactions: true, sendMessage: true },
      reactionNotifications: "own",  // off | own | all
      mediaMaxMb: 5,
      proxy: "socks5://localhost:9050",
    }
  }
}
```

### 字段详解

| 字段 | 类型 | 有效值 | 默认值 | 说明 |
|---|---|---|---|---|
| `enabled` | boolean | `true` \| `false` | `true` | 启用渠道 |
| `botToken` | string | Telegram Bot Token | - | 机器人令牌 |
| `dmPolicy` | string | `pairing` \| `allowlist` \| `open` \| `disabled` | `pairing` | DM 策略 |
| `allowFrom` | array | `tg:<id>` 或数字 ID | `[]` | 允许的用户列表 |
| `historyLimit` | number | `0` - `1000` | `50` | 历史消息限制 |
| `replyToMode` | string | `off` \| `first` \| `all` | `first` | 回复模式 |
| `linkPreview` | boolean | `true` \| `false` | `true` | 链接预览 |
| `streaming` | string | `off` \| `partial` \| `block` \| `progress` | `off` | 流式输出 |
| `reactionNotifications` | string | `off` \| `own` \| `all` | `own` | 反应通知 |
| `mediaMaxMb` | number | `0` - `50` | `5` | 媒体大小限制 (MB) |
| `proxy` | string | SOCKS5/HTTP 代理 URL | - | 代理配置 |

---

## WhatsApp

```json5
{
  channels: {
    whatsapp: {
      dmPolicy: "pairing",
      allowFrom: ["+15555550123"],
      textChunkLimit: 4000,
      chunkMode: "length",  // length | newline
      mediaMaxMb: 50,
      sendReadReceipts: true,
      groups: {
        "*": { requireMention: true },
      },
      groupPolicy: "allowlist",
    }
  }
}
```

### 字段详解

| 字段 | 类型 | 有效值 | 默认值 | 说明 |
|---|---|---|---|---|
| `dmPolicy` | string | `pairing` \| `allowlist` \| `open` \| `disabled` | `pairing` | DM 策略 |
| `allowFrom` | array | 电话号码格式 | `[]` | 允许的用户 |
| `textChunkLimit` | number | `1000` - `10000` | `4000` | 文本分块限制 |
| `chunkMode` | string | `length` \| `newline` | `length` | 分块模式 |
| `mediaMaxMb` | number | `0` - `100` | `50` | 媒体大小限制 |
| `sendReadReceipts` | boolean | `true` \| `false` | `true` | 已读回执 |

---

## Discord

```json5
{
  channels: {
    discord: {
      enabled: true,
      token: "your-bot-token",
      mediaMaxMb: 8,
      allowBots: false,
      replyToMode: "off",  // off | first | all
      dmPolicy: "pairing",
      guilds: {
        "123456789012345678": {
          slug: "friends-of-openclaw",
          requireMention: false,
        }
      },
      streaming: "off",  // off | partial | block | progress
      threadBindings: {
        enabled: true,
        ttlHours: 24,
      },
    }
  }
}
```

### 字段详解

| 字段 | 类型 | 有效值 | 默认值 | 说明 |
|---|---|---|---|---|
| `enabled` | boolean | `true` \| `false` | `true` | 启用渠道 |
| `token` | string | Discord Bot Token | - | 机器人令牌 |
| `mediaMaxMb` | number | `0` - `25` | `8` | 媒体大小限制 |
| `allowBots` | boolean | `true` \| `false` | `false` | 允许机器人消息 |
| `replyToMode` | string | `off` \| `first` \| `all` | `off` | 回复模式 |
| `streaming` | string | `off` \| `partial` \| `block` \| `progress` | `off` | 流式输出 |
| `threadBindings.ttlHours` | number | `0` - `168` | `24` | 线程绑定 TTL |

---

## Slack

```json5
{
  channels: {
    slack: {
      enabled: true,
      botToken: "xoxb-...",
      appToken: "xapp-...",  // Socket mode 需要
      dmPolicy: "pairing",
      streaming: "partial",  // off | partial | block | progress
      nativeStreaming: true,
    }
  }
}
```

### 字段详解

| 字段 | 类型 | 有效值 | 默认值 | 说明 |
|---|---|---|---|---|
| `botToken` | string | Slack Bot Token (xoxb-) | - | 机器人令牌 |
| `appToken` | string | Slack App Token (xapp-) | - | Socket mode 令牌 |
| `streaming` | string | `off` \| `partial` \| `block` \| `progress` | `partial` | 流式输出 |
| `nativeStreaming` | boolean | `true` \| `false` | `true` | 使用 Slack 原生流式 |

---

## Google Chat

```json5
{
  channels: {
    googlechat: {
      enabled: true,
      serviceAccountFile: "/path/to/service-account.json",
      audienceType: "app-url",  // app-url | project-number
    }
  }
}
```

### 字段详解

| 字段 | 类型 | 有效值 | 默认值 | 说明 |
|---|---|---|---|---|
| `serviceAccountFile` | string | JSON 文件路径 | - | 服务账户文件 |
| `audienceType` | string | `app-url` \| `project-number` | `app-url` | 受众类型 |

---

## Signal

```json5
{
  channels: {
    signal: {
      reactionNotifications: "own",  // off | own | all | allowlist
      reactionAllowlist: ["+15551234567"],
      historyLimit: 50,
    }
  }
}
```

### 字段详解

| 字段 | 类型 | 有效值 | 默认值 | 说明 |
|---|---|---|---|---|
| `reactionNotifications` | string | `off` \| `own` \| `all` \| `allowlist` | `own` | 反应通知 |
| `historyLimit` | number | `0` - `200` | `50` | 历史消息限制 |

---

## iMessage

```json5
{
  channels: {
    imessage: {
      enabled: true,
      cliPath: "imsg",
      dbPath: "~/Library/Messages/chat.db",
      dmPolicy: "pairing",
      includeAttachments: false,
      mediaMaxMb: 16,
      service: "auto",
      region: "US",
    }
  }
}
```

### 字段详解

| 字段 | 类型 | 有效值 | 默认值 | 说明 |
|---|---|---|---|---|
| `cliPath` | string | `imsg` 命令路径 | `imsg` | CLI 路径 |
| `includeAttachments` | boolean | `true` \| `false` | `false` | 包含附件 |
| `mediaMaxMb` | number | `0` - `50` | `16` | 媒体大小限制 |
| `region` | string | `US` \| `CN` \| `JP` ... | `US` | 地区 |

---

## 多账户配置（所有渠道）

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
  }
}
```

### 字段详解

| 字段 | 类型 | 有效值 | 默认值 | 说明 |
|---|---|---|---|---|
| `accounts.<id>` | object | 账户配置对象 | - | 账户配置 |
| `accounts.<id>.name` | string | 任意字符串 | - | 账户名称 |
| `accounts.<id>.botToken` | string | 渠道特定的令牌 | - | 账户令牌 |

---

## 常见错误

| 错误 | 原因 | 修复 |
|---|---|---|
| `"streaming": "on"` | 不是有效枚举值 | 改为 `"off"` \| `"partial"` \| `"block"` \| `"progress"` |
| `"dmPolicy": "allow"` | 拼写错误 | 改为 `"allowlist"` |
| `"replyToMode": "all"` (Telegram) | Telegram 不支持 | 改为 `"first"` |
| 缺少 `botToken` | 必需字段 | 添加有效的令牌 |

---

## 官方文档

- https://docs.openclaw.ai/gateway/configuration-reference#channels
- https://docs.openclaw.ai/zh-CN/gateway/configuration
