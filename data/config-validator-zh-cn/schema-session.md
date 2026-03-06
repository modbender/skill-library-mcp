# Session Schema（会话配置）

## 基础配置

```json5
{
  session: {
    dmScope: "per-peer",
    identityLinks: {
      "主人": ["telegram:5203187663", "webchat:openclaw-tui"],
    },
    threadBindings: {
      enabled: true,
      ttlHours: 24,
    },
    reset: {
      mode: "daily",
      atHour: 4,
      idleMinutes: 120,
    },
  }
}
```

### 核心字段

| 字段 | 类型 | 有效值 | 默认值 | 说明 |
|---|---|---|---|---|
| `dmScope` | string | `main` \| `per-peer` \| `per-channel-peer` \| `per-account-channel-peer` | `per-peer` | DM 会话范围 |
| `identityLinks` | object | 身份映射 | - | 身份链接 |
| `threadBindings.enabled` | boolean | `true` \| `false` | `true` | 启用线程绑定 |
| `threadBindings.ttlHours` | number | `0` - `168` | `24` | 线程绑定 TTL |
| `reset.mode` | string | `off` \| `daily` \| `idle` \| `manual` | `off` | 重置模式 |
| `reset.atHour` | number | `0` - `23` | `4` | 每日重置时间 |
| `reset.idleMinutes` | number | 分钟数 | `120` | 空闲重置时间 |

### DM Scope 详解

| 值 | 说明 |
|---|---|
| `main` | 所有 DM 共享一个会话 |
| `per-peer` | 每个对话对象一个会话（推荐） |
| `per-channel-peer` | 每个渠道 + 对话对象一个会话 |
| `per-account-channel-peer` | 每个账户 + 渠道 + 对话对象一个会话 |

### Reset Mode 详解

| 模式 | 说明 |
|---|---|
| `off` | 禁用自动重置 |
| `daily` | 每日定时重置 |
| `idle` | 空闲时重置 |
| `manual` | 仅手动重置 |

---

## Identity Links（身份链接）

```json5
{
  session: {
    identityLinks: {
      "主人": [
        "telegram:5203187663",
        "whatsapp:+15555550123",
        "discord:123456789012345678",
        "webchat:openclaw-tui",
      ],
      "同事": [
        "telegram:987654321",
      ],
    }
  }
}
```

### 渠道 ID 格式

| 渠道 | ID 格式 | 示例 |
|---|---|---|
| Telegram | `telegram:<user_id>` | `telegram:5203187663` |
| WhatsApp | `whatsapp:<phone>` | `whatsapp:+15555550123` |
| Discord | `discord:<user_id>` | `discord:123456789012345678` |
| Slack | `slack:<user_id>` | `slack:U123456` |
| WebUI | `webchat:<client_id>` | `webchat:openclaw-tui` |

---

## Thread Bindings（线程绑定）

```json5
{
  session: {
    threadBindings: {
      enabled: true,
      ttlHours: 24,
      spawnSubagentSessions: false,
    }
  }
}
```

### 字段详解

| 字段 | 类型 | 有效值 | 默认值 | 说明 |
|---|---|---|---|---|
| `enabled` | boolean | `true` \| `false` | `true` | 启用线程绑定 |
| `ttlHours` | number | `0` - `168` | `24` | 绑定有效期（小时） |
| `spawnSubagentSessions` | boolean | `true` \| `false` | `false` | 生成子智能体会话 |

---

## Session Reset（会话重置）

```json5
{
  session: {
    reset: {
      mode: "daily",
      atHour: 4,
      idleMinutes: 120,
      preserveIdentity: true,
    }
  }
}
```

### 字段详解

| 字段 | 类型 | 有效值 | 默认值 | 说明 |
|---|---|---|---|---|
| `mode` | string | `off` \| `daily` \| `idle` \| `manual` | `off` | 重置模式 |
| `atHour` | number | `0` - `23` | `4` | 每日重置时间（小时） |
| `idleMinutes` | number | 分钟数 | `120` | 空闲重置阈值 |
| `preserveIdentity` | boolean | `true` \| `false` | `true` | 保留身份信息 |

---

## 常见错误

| 错误 | 原因 | 修复 |
|---|---|---|
| `"dmScope": "per-user"` | 不是有效枚举值 | 改为 `per-peer` |
| `"reset.mode": "auto"` | 不是有效枚举值 | 改为 `daily` \| `idle` |
| `"reset.atHour": 25` | 超出范围 | 改为 `0` - `23` |
| IdentityLinks 格式错误 | 缺少渠道前缀 | 添加 `telegram:` 等前缀 |

---

## 官方文档

- https://docs.openclaw.ai/gateway/configuration-reference#session
- https://docs.openclaw.ai/zh-CN/concepts/session
