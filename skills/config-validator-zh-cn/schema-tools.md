# Tools Schema（工具配置）

## 基础配置

```json5
{
  tools: {
    elevated: {
      enabled: true,
      allowFrom: {
        "*": ["user1"],
        telegram: ["5203187663"],
      },
    },
    sandbox: {
      tools: {
        allow: ["exec", "read", "write"],
        deny: ["browser", "canvas"],
      },
    },
  }
}
```

### 核心字段

| 字段 | 类型 | 有效值 | 默认值 | 说明 |
|---|---|---|---|---|
| `elevated.enabled` | boolean | `true` \| `false` | `false` | 启用提升权限 |
| `elevated.allowFrom` | object | 渠道 → 用户列表 | - | 允许的用户 |
| `sandbox.tools.allow` | array | 工具列表 | - | 允许的工具 |
| `sandbox.tools.deny` | array | 工具列表 | - | 禁止的工具 |

---

## Elevated Tools（提升权限工具）

```json5
{
  tools: {
    elevated: {
      enabled: true,
      allowFrom: {
        "*": ["user1", "user2"],
        telegram: ["5203187663"],
        discord: ["123456789012345678"],
      },
    }
  }
}
```

### 字段详解

| 字段 | 类型 | 有效值 | 默认值 | 说明 |
|---|---|---|---|---|
| `enabled` | boolean | `true` \| `false` | `false` | 启用提升权限 |
| `allowFrom.<channel>` | array | 用户 ID 列表 | - | 渠道特定的允许列表 |
| `allowFrom["*"]` | array | 用户 ID 列表 | - | 全局允许列表 |

### 允许的用户格式

| 渠道 | 用户 ID 格式 |
|---|---|
| Telegram | 数字 ID (`5203187663`) |
| WhatsApp | 电话号码 (`+15555550123`) |
| Discord | 用户 ID (`123456789012345678`) |
| Slack | 用户 ID (`U123456`) |
| 通用 | 用户名 |

---

## Sandbox Tools（沙箱工具）

```json5
{
  tools: {
    sandbox: {
      tools: {
        allow: [
          "exec",
          "process",
          "read",
          "write",
          "edit",
          "apply_patch",
        ],
        deny: [
          "browser",
          "canvas",
          "nodes",
          "cron",
        ],
      }
    }
  }
}
```

### 允许的工具列表

| 工具 | 说明 | 沙箱安全 |
|---|---|---|
| `exec` | 执行 shell 命令 | ⚠️ 需要沙箱 |
| `process` | 管理后台进程 | ⚠️ 需要沙箱 |
| `read` | 读取文件 | ✅ 安全 |
| `write` | 写入文件 | ⚠️ 需要沙箱 |
| `edit` | 编辑文件 | ⚠️ 需要沙箱 |
| `apply_patch` | 应用补丁 | ⚠️ 需要沙箱 |
| `sessions_list` | 列出会话 | ✅ 安全 |
| `sessions_history` | 会话历史 | ✅ 安全 |
| `sessions_send` | 发送消息 | ✅ 安全 |
| `sessions_spawn` | 生成子智能体 | ✅ 安全 |
| `session_status` | 会话状态 | ✅ 安全 |

### 通常禁止的工具

| 工具 | 原因 |
|---|---|
| `browser` | 需要浏览器访问 |
| `canvas` | 需要 GUI |
| `nodes` | 需要节点访问 |
| `cron` | 需要系统权限 |
| `gateway` | 需要网关权限 |
| `discord` | 需要 Discord 访问 |

---

## 工具配置文件

```json5
{
  agents: {
    list: [
      {
        id: "main",
        tools: {
          profile: "coding",
          allow: ["browser"],
          deny: ["canvas"],
          elevated: { enabled: true },
        }
      }
    ]
  }
}
```

### 字段详解

| 字段 | 类型 | 有效值 | 默认值 | 说明 |
|---|---|---|---|---|
| `profile` | string | `coding` \| `writing` \| `research` ... | - | 工具配置文件 |
| `allow` | array | 工具列表 | - | 允许的工具（覆盖） |
| `deny` | array | 工具列表 | - | 禁止的工具（覆盖） |
| `elevated.enabled` | boolean | `true` \| `false` | - | 启用提升权限 |

---

## 常见错误

| 错误 | 原因 | 修复 |
|---|---|---|
| `elevated.allowFrom: ["user1"]` | 应该是对象 | 改为 `{ "*": ["user1"] }` |
| 工具名称拼写错误 | `broswer` | 改为 `browser` |
| 在沙箱中允许危险工具 | `allow: ["gateway"]` | 从允许列表中移除 |

---

## 官方文档

- https://docs.openclaw.ai/gateway/configuration-reference#tools
- https://docs.openclaw.ai/zh-CN/gateway/sandboxing
