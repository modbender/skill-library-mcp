# Agents Schema（智能体配置）

## Agents Defaults（默认配置）

```json5
{
  agents: {
    defaults: {
      workspace: "~/.openclaw/workspace",
      model: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: ["minimax/MiniMax-M2.1"],
      },
      thinkingDefault: "low",
      heartbeat: {
        every: "30m",
        model: "openai/gpt-5.2-mini",
      },
      sandbox: {
        mode: "non-main",
        scope: "agent",
      },
    }
  }
}
```

### 核心字段

| 字段 | 类型 | 有效值 | 默认值 | 说明 |
|---|---|---|---|---|
| `workspace` | string | 文件路径 | `~/.openclaw/workspace` | 工作区路径 |
| `model.primary` | string | `provider/model` | - | 主模型 |
| `model.fallbacks` | array | 模型列表 | `[]` | 故障转移模型 |
| `thinkingDefault` | string | `off` \| `minimal` \| `low` \| `medium` \| `high` | `low` | 默认思考级别 |
| `heartbeat.every` | string | 持续时间 (`30m`, `1h`) | `30m` | 心跳间隔 |
| `sandbox.mode` | string | `off` \| `non-main` \| `all` | `non-main` | 沙箱模式 |
| `sandbox.scope` | string | `session` \| `agent` \| `shared` | `agent` | 沙箱范围 |

### Thinking 级别详解

| 级别 | 说明 |
|---|---|
| `off` | 关闭思考 |
| `minimal` | 最小思考 ("think") |
| `low` | 低思考 ("think hard") |
| `medium` | 中等思考 ("think harder") |
| `high` | 高思考 ("ultrathink") |

### Sandbox 模式详解

| 模式 | 说明 |
|---|---|
| `off` | 禁用沙箱 |
| `non-main` | 非主智能体使用沙箱 |
| `all` | 所有智能体使用沙箱 |

### Sandbox 范围详解

| 范围 | 说明 |
|---|---|
| `session` | 每会话一个容器 |
| `agent` | 每智能体一个容器 |
| `shared` | 共享容器 |

---

## Agents List（智能体列表）

```json5
{
  agents: {
    list: [
      {
        id: "main",
        default: true,
        name: "Main Agent",
        workspace: "~/.openclaw/workspace",
        model: "anthropic/claude-opus-4-6",
        identity: {
          name: "Samantha",
          emoji: "🦥",
          avatar: "avatars/samantha.png",
        },
        groupChat: { mentionPatterns: ["@openclaw"] },
        sandbox: { mode: "off" },
      }
    ]
  }
}
```

### 字段详解

| 字段 | 类型 | 有效值 | 默认值 | 说明 |
|---|---|---|---|---|
| `id` | string | 唯一标识符 | - | 智能体 ID（必需） |
| `default` | boolean | `true` \| `false` | `false` | 是否为默认智能体 |
| `name` | string | 任意字符串 | - | 智能体名称 |
| `workspace` | string | 文件路径 | - | 工作区路径 |
| `model` | string\|object | 模型配置 | - | 模型覆盖 |
| `identity.name` | string | 任意字符串 | - | 身份名称 |
| `identity.emoji` | string | Emoji | - | 身份表情 |
| `identity.avatar` | string | 路径或 URL | - | 头像 |
| `groupChat.mentionPatterns` | array | 字符串列表 | - | 群组提及模式 |
| `sandbox.mode` | string | `off` \| `non-main` \| `all` | - | 沙箱模式覆盖 |

---

## Heartbeat（心跳配置）

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m",
        model: "openai/gpt-5.2-mini",
        includeReasoning: false,
        session: "main",
        to: "+15555550123",
        directPolicy: "allow",
        target: "none",
        prompt: "Read HEARTBEAT.md if exists...",
      }
    }
  }
}
```

### 字段详解

| 字段 | 类型 | 有效值 | 默认值 | 说明 |
|---|---|---|---|---|
| `every` | string | 持续时间 | `30m` | 心跳间隔 (`0m` 禁用) |
| `model` | string | `provider/model` | - | 心跳使用的模型 |
| `includeReasoning` | boolean | `true` \| `false` | `false` | 包含推理 |
| `session` | string | 会话 ID | `main` | 会话键 |
| `to` | string | 渠道特定的 ID | - | 发送目标 |
| `directPolicy` | string | `allow` \| `block` | `allow` | DM 策略 |
| `target` | string | `none` \| `last` \| `whatsapp` \| `telegram` \| ... | `none` | 目标渠道 |
| `prompt` | string | 任意字符串 | - | 心跳提示词 |

### Target 有效值

| 值 | 说明 |
|---|---|
| `none` | 不发送到特定渠道 |
| `last` | 最后活跃的渠道 |
| `whatsapp` | WhatsApp |
| `telegram` | Telegram |
| `discord` | Discord |
| `slack` | Slack |

---

## Compaction（压缩配置）

```json5
{
  agents: {
    defaults: {
      compaction: {
        mode: "safeguard",
        reserveTokensFloor: 24000,
        memoryFlush: {
          enabled: true,
          softThresholdTokens: 6000,
        },
      }
    }
  }
}
```

### 字段详解

| 字段 | 类型 | 有效值 | 默认值 | 说明 |
|---|---|---|---|---|
| `mode` | string | `default` \| `safeguard` | `safeguard` | 压缩模式 |
| `reserveTokensFloor` | number | Token 数 | `24000` | 保留 Token 下限 |
| `memoryFlush.enabled` | boolean | `true` \| `false` | `true` | 启用内存刷新 |

---

## Context Pruning（上下文修剪）

```json5
{
  agents: {
    defaults: {
      contextPruning: {
        mode: "cache-ttl",
        ttl: "1h",
        keepLastAssistants: 3,
        softTrimRatio: 0.3,
        hardClearRatio: 0.5,
      }
    }
  }
}
```

### 字段详解

| 字段 | 类型 | 有效值 | 默认值 | 说明 |
|---|---|---|---|---|
| `mode` | string | `off` \| `cache-ttl` | `cache-ttl` | 修剪模式 |
| `ttl` | string | 持续时间 | `1h` | 缓存 TTL |
| `keepLastAssistants` | number | 数量 | `3` | 保留最后 N 个助手消息 |
| `softTrimRatio` | number | `0.0` - `1.0` | `0.3` | 软修剪比例 |
| `hardClearRatio` | number | `0.0` - `1.0` | `0.5` | 硬清除比例 |

---

## Block Streaming（块流式输出）

```json5
{
  agents: {
    defaults: {
      blockStreamingDefault: "off",
      blockStreamingBreak: "text_end",
      blockStreamingChunk: { minChars: 800, maxChars: 1200 },
      humanDelay: { mode: "natural" },
    }
  }
}
```

### 字段详解

| 字段 | 类型 | 有效值 | 默认值 | 说明 |
|---|---|---|---|---|
| `blockStreamingDefault` | string | `on` \| `off` | `off` | 默认块流式 |
| `blockStreamingBreak` | string | `text_end` \| `message_end` | `text_end` | 断点 |
| `humanDelay.mode` | string | `off` \| `natural` \| `custom` | `natural` | 人类延迟模式 |

### Human Delay 模式

| 模式 | 说明 |
|---|---|
| `off` | 无延迟 |
| `natural` | 自然延迟 (800-2500ms) |
| `custom` | 自定义延迟 |

---

## Typing Indicators（输入指示器）

```json5
{
  agents: {
    defaults: {
      typingMode: "instant",
      typingIntervalSeconds: 6,
    }
  }
}
```

### 字段详解

| 字段 | 类型 | 有效值 | 默认值 | 说明 |
|---|---|---|---|---|
| `typingMode` | string | `never` \| `instant` \| `thinking` \| `message` | `instant` | 输入指示模式 |
| `typingIntervalSeconds` | number | 秒数 | `6` | 指示间隔 |

### Typing Mode 详解

| 模式 | 说明 |
|---|---|
| `never` | 从不显示 |
| `instant` | 立即显示 |
| `thinking` | 思考时显示 |
| `message` | 消息到达时显示 |

---

## Multi-Agent Routing（多智能体路由）

```json5
{
  agents: {
    list: [
      { id: "home", default: true },
      { id: "work" },
    ],
  },
  bindings: [
    { agentId: "home", match: { channel: "whatsapp", accountId: "personal" } },
    { agentId: "work", match: { channel: "whatsapp", accountId: "biz" } },
  ],
}
```

### Binding Match 字段

| 字段 | 类型 | 有效值 | 说明 |
|---|---|---|---|
| `match.channel` | string | 渠道名称 | 必需 |
| `match.accountId` | string | 账户 ID 或 `*` | 可选 |
| `match.peer` | object | `{ kind, id }` | 可选 |
| `match.guildId` | string | Discord 服务器 ID | 可选 |

---

## 常见错误

| 错误 | 原因 | 修复 |
|---|---|---|
| `"thinkingDefault": "hard"` | 不是有效枚举值 | 改为 `low` \| `medium` \| `high` |
| `"sandbox.mode": "container"` | 无效值 | 改为 `off` \| `non-main` \| `all` |
| `"heartbeat.every": "30"` | 缺少单位 | 改为 `30m` \| `1800s` |
| 缺少 `agents.list[].id` | 必需字段 | 添加唯一 ID |

---

## 官方文档

- https://docs.openclaw.ai/gateway/configuration-reference#agent-defaults
- https://docs.openclaw.ai/zh-CN/gateway/configuration
