---
name: agent-telegram
description: Agent 团队 Telegram 通信规范。所有 Agent 向用户发送消息时必须遵循此规范，确保消息正确发送到 Telegram。
metadata: {"clawdbot":{"emoji":"📤","requiredFor":["architect","backend","frontend","product","content","crawler","qa"]}}
---

# Agent Telegram 通信规范

所有 Agent 向用户 (Legend) 发送 Telegram 消息时必须遵循此规范。

## 账号映射表

| Agent | accountId | Emoji |
|-------|-----------|-------|
| main (9527) | `default` | 🤖 |
| architect (亮亮) | `architect` | 🏗️ |
| backend (老崔) | `backend` | 🔧 |
| frontend (小白) | `frontend` | 🎨 |
| product (小黄) | `sproduct` | 🟡 |
| content (世龙) | `content` | ✍️ |
| crawler (湘君) | `crawler` | 🕷️ |
| qa (赵飞) | `qa` | 🧪 |

**用户 Telegram ID**: `5440561025`

## 发送消息

### 标准格式

```javascript
message({
  action: "send",
  channel: "telegram",
  accountId: "<你的accountId>",
  target: "5440561025",
  message: "<你的emoji> <内容>"
})
```

### 示例

**产品经理发送：**
```javascript
message({
  action: "send",
  channel: "telegram",
  accountId: "sproduct",
  target: "5440561025",
  message: "🟡 需求文档已完成，请查看：~/Desktop/project/docs/product/001-prd.md"
})
```

**后端工程师发送：**
```javascript
message({
  action: "send",
  channel: "telegram",
  accountId: "backend",
  target: "5440561025",
  message: "🔧 API 接口开发完成，接口文档：~/Desktop/project/docs/backend/api.md"
})
```

## 汇报时机

- ✅ **收到任务时** - 立即汇报"收到任务，开始执行"
- ✅ **每完成子任务** - 汇报完成情况和输出
- ✅ **遇到问题** - 汇报问题并请求决策
- ✅ **任务全部完成** - 汇报最终结果

## 常见错误

| 错误 | 后果 | 正确做法 |
|------|------|----------|
| 忘记 `accountId` | 消息发不出去 | 必须指定你的 accountId |
| 用 `sessions_send` | 消息不会发到 Telegram | 用 `message` 工具 |
| product 用 `accountId: "product"` | 账号不存在 | 应该是 `sproduct` |
| target 写错 | 发给错误的人 | 固定用 `5440561025` |

## 消息模板

### 任务开始
```
<emoji> 收到任务：<任务名>
📝 开始执行...
```

### 任务完成
```
<emoji> <任务名> 完成
✅ 已完成: <子任务>
📁 输出: <文件路径>
```

### 遇到问题
```
<emoji> <任务名> 遇到问题
❌ 问题: <描述>
💡 建议: <解决方案或请求决策>
```

## 配置位置

- **主配置**: `~/.openclaw/openclaw.json` → `channels.telegram.accounts`
- **此 Skill**: `~/.openclaw/workspace/skills/agent-telegram/SKILL.md`

---

**记住**：发送 Telegram 消息 = `message` 工具 + `accountId` + `target: "5440561025"`
