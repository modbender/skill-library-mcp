# Quick Reference（常用字段快速参考）

## 50 个核心配置字段

---

## Channels（渠道）

### Telegram

| 字段 | 有效值 | 默认值 | 说明 |
|---|---|---|---|
| `botToken` | Telegram Bot Token | - | 机器人令牌 |
| `dmPolicy` | `pairing` \| `allowlist` \| `open` \| `disabled` | `pairing` | DM 策略 |
| `streaming` | `off` \| `partial` \| `block` \| `progress` | `off` | 流式输出 |
| `replyToMode` | `off` \| `first` \| `all` | `first` | 回复模式 |

### WhatsApp

| 字段 | 有效值 | 默认值 | 说明 |
|---|---|---|---|
| `dmPolicy` | `pairing` \| `allowlist` \| `open` \| `disabled` | `pairing` | DM 策略 |
| `sendReadReceipts` | `true` \| `false` | `true` | 已读回执 |

### Discord

| 字段 | 有效值 | 默认值 | 说明 |
|---|---|---|---|
| `token` | Discord Bot Token | - | 机器人令牌 |
| `streaming` | `off` \| `partial` \| `block` \| `progress` | `off` | 流式输出 |
| `allowBots` | `true` \| `false` | `false` | 允许机器人 |

### Slack

| 字段 | 有效值 | 默认值 | 说明 |
|---|---|---|---|
| `botToken` | `xoxb-...` | - | 机器人令牌 |
| `appToken` | `xapp-...` | - | Socket mode 令牌 |
| `streaming` | `off` \| `partial` \| `block` \| `progress` | `partial` | 流式输出 |

---

## Agents（智能体）

### 核心配置

| 字段 | 有效值 | 默认值 | 说明 |
|---|---|---|---|
| `workspace` | 文件路径 | `~/.openclaw/workspace` | 工作区 |
| `model.primary` | `provider/model` | - | 主模型 |
| `thinkingDefault` | `off` \| `minimal` \| `low` \| `medium` \| `high` | `low` | 思考级别 |

### Heartbeat

| 字段 | 有效值 | 默认值 | 说明 |
|---|---|---|---|
| `heartbeat.every` | `30m` \| `1h` \| `0m` | `30m` | 心跳间隔 |
| `heartbeat.target` | `none` \| `last` \| `telegram` \| ... | `none` | 目标渠道 |

### Sandbox

| 字段 | 有效值 | 默认值 | 说明 |
|---|---|---|---|
| `sandbox.mode` | `off` \| `non-main` \| `all` | `non-main` | 沙箱模式 |
| `sandbox.scope` | `session` \| `agent` \| `shared` | `agent` | 沙箱范围 |

---

## Gateway（网关）

| 字段 | 有效值 | 默认值 | 说明 |
|---|---|---|---|
| `port` | `1024` - `65535` | `18789` | 端口 |
| `bind` | `loopback` \| `lan` \| `tailnet` \| `any` | `loopback` | 绑定 |
| `auth.mode` | `token` \| `password` \| `none` | `token` | 认证 |
| `reload.mode` | `hybrid` \| `hot` \| `restart` \| `off` | `hybrid` | 热重载 |

---

## Session（会话）

| 字段 | 有效值 | 默认值 | 说明 |
|---|---|---|---|
| `dmScope` | `main` \| `per-peer` \| `per-channel-peer` | `per-peer` | DM 范围 |
| `reset.mode` | `off` \| `daily` \| `idle` \| `manual` | `off` | 重置模式 |

---

## Tools（工具）

| 字段 | 有效值 | 默认值 | 说明 |
|---|---|---|---|
| `elevated.enabled` | `true` \| `false` | `false` | 提升权限 |
| `sandbox.tools.allow` | 工具列表 | - | 允许的工具 |
| `sandbox.tools.deny` | 工具列表 | - | 禁止的工具 |

---

## Models（模型）

### 内置别名

| 别名 | 模型 |
|---|---|
| `opus` | `anthropic/claude-opus-4-6` |
| `sonnet` | `anthropic/claude-sonnet-4-5` |
| `gpt` | `openai/gpt-5.2` |
| `gpt-mini` | `openai/gpt-5-mini` |
| `gemini` | `google/gemini-3-pro-preview` |

### 思考级别

| 级别 | 说明 |
|---|---|
| `off` | 关闭思考 |
| `minimal` | 最小思考 |
| `low` | 低思考（默认） |
| `medium` | 中等思考 |
| `high` | 高思考 |

---

## 常见错误速查

### 无效枚举值

| 错误值 | 正确值 |
|---|---|
| `"streaming": "on"` | `"off"` \| `"partial"` \| `"block"` \| `"progress"` |
| `"dmPolicy": "allow"` | `"allowlist"` |
| `"thinking": "hard"` | `"high"` |
| `"reload.mode": "auto"` | `"hybrid"` |

### 类型错误

| 错误 | 正确 |
|---|---|
| `"port": "18789"` | `"port": 18789` |
| `fallbacks: "gpt"` | `fallbacks: ["openai/gpt-5.2"]` |

### 格式错误

| 错误 | 正确 |
|---|---|
| `"telegram:5203187663"` (identityLinks) | `"主人": ["telegram:5203187663"]` |
| `allowFrom: ["user1"]` | `allowFrom: { "*": ["user1"] }` |

---

## 快速验证命令

```bash
# 验证配置
openclaw doctor

# 自动修复
openclaw doctor --fix

# 查看配置
openclaw config get <path>

# 设置配置
openclaw config set <path> <value>
```

---

## 官方文档

- https://docs.openclaw.ai/gateway/configuration-reference
- https://docs.openclaw.ai/zh-CN/gateway/configuration
