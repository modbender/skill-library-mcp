# A2A-Lite 协议参考

## 协议版本

当前版本：`a2a-lite/1.0`

## 消息类型完整列表

| 类型 | 用途 | 必需参数 | 可选参数 |
|------|------|----------|----------|
| `discover` | 查询对方能力 | - | - |
| `card` | 返回能力卡片 | - | - |
| `task` | 发起任务请求 | `id` | `skill`, `priority` |
| `status` | 任务状态更新 | `task`, `state` | `progress`, `eta` |
| `result` | 任务结果 | `task`, `state` | `artifacts` |
| `cancel` | 取消任务 | `task` | `reason` |
| `ack` | 确认收到 | `task` | - |

## 状态值 (state)

| 状态 | 含义 | 终态? |
|------|------|-------|
| `accepted` | 任务已接受 | 否 |
| `working` | 处理中 | 否 |
| `input-required` | 需要更多输入 | 否 |
| `completed` | 成功完成 | 是 |
| `failed` | 执行失败 | 是 |
| `cancelled` | 已取消 | 是 |
| `rejected` | 拒绝执行 | 是 |

## Agent Card Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["protocol", "agent", "skills"],
  "properties": {
    "protocol": {
      "type": "string",
      "pattern": "^a2a-lite/[0-9]+\\.[0-9]+$"
    },
    "agent": {
      "type": "object",
      "required": ["id", "name", "framework"],
      "properties": {
        "id": { "type": "string" },
        "name": { "type": "string" },
        "framework": { 
          "type": "string",
          "enum": ["clawdbot", "openclaw", "other"]
        },
        "version": { "type": "string" }
      }
    },
    "description": { "type": "string" },
    "skills": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "name", "description"],
        "properties": {
          "id": { "type": "string" },
          "name": { "type": "string" },
          "description": { "type": "string" },
          "inputModes": {
            "type": "array",
            "items": { 
              "type": "string",
              "enum": ["text", "file", "image", "audio", "video"]
            }
          },
          "outputModes": {
            "type": "array",
            "items": { 
              "type": "string",
              "enum": ["text", "file", "image", "audio", "video"]
            }
          }
        }
      }
    },
    "capabilities": {
      "type": "object",
      "properties": {
        "streaming": { "type": "boolean" },
        "fileTransfer": { "type": "boolean" },
        "asyncTasks": { "type": "boolean" },
        "pushNotifications": { "type": "boolean" }
      }
    },
    "limits": {
      "type": "object",
      "properties": {
        "maxFileSize": { "type": "string" },
        "maxConcurrentTasks": { "type": "integer" }
      }
    },
    "channels": {
      "type": "array",
      "items": { "type": "string" }
    },
    "contact": {
      "type": "object",
      "properties": {
        "human": { "type": "string" },
        "timezone": { "type": "string" }
      }
    }
  }
}
```

## 与 Google A2A 的对比

| 特性 | Google A2A | A2A-Lite |
|------|------------|----------|
| 传输层 | HTTP/JSON-RPC | 现有消息通道 |
| 发现机制 | /.well-known/agent.json | 显式 discover 消息 |
| 消息格式 | 纯 JSON | 自然语言 + 标记 |
| 流式传输 | SSE | 不支持 |
| 推送通知 | Webhook | 不支持 |
| 认证 | OAuth/API Key | 依赖通道认证 |
| 复杂度 | 企业级 | 轻量级 |

## 设计决策

### 为什么用自然语言 + 标记？

1. **人类可读** — 调试时人类能直接看懂
2. **优雅降级** — 对方不支持时仍可理解
3. **灵活性** — 消息体可包含任意上下文
4. **简单** — 不需要序列化/反序列化库

### 为什么不实现 HTTP 服务？

1. **部署复杂** — 需要暴露端口、配置域名
2. **网络限制** — 很多环境无法接收入站连接
3. **已有通道** — Discord/Telegram 等已提供可靠传输
4. **安全性** — 复用已认证的通道更安全

### 为什么不支持流式传输？

1. **复杂度** — 在消息通道上实现流式困难
2. **必要性低** — 大多数 agent 任务不需要实时流
3. **可扩展** — 未来版本可添加

## 扩展点

协议预留以下扩展点供未来版本使用：

- `capabilities` 对象可添加新字段
- `skills` 数组可添加新属性
- 消息类型可扩展（保持向后兼容）
- 状态值可扩展

扩展时应保持向后兼容：旧版本 agent 应能忽略新字段。
