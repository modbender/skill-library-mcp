---
name: openclaw-agent-builder
description: Use when creating OpenClaw agents, configuring workspaces, multi-agent routing, session isolation, or channel bindings.
metadata:
  openclaw:
    emoji: "🦞"
    homepage: https://docs.openclaw.ai/concepts/agent.md
---

# OpenClaw Agent Builder

为 OpenClaw 创建和配置 AI Agent 的完整指南。OpenClaw 使用基于工作空间的 Agent 架构，每个 Agent 拥有独立的会话、配置和上下文文件。

## 核心架构

```
~/.openclaw/
├── openclaw.json          # 主配置文件
├── agents/                # Agent 会话存储
│   ├── <agentId>/
│   │   ├── agent/         # Agent 配置
│   │   └── sessions/      # 会话历史 (JSONL)
│   └── main/              # 默认主 Agent
├── workspace/             # 主工作空间
│   ├── AGENTS.md          # 工作流指令
│   ├── SOUL.md            # 角色人格定义
│   ├── TOOLS.md           # 工具使用说明
│   ├── USER.md            # 用户配置
│   ├── MEMORY.md          # 长期记忆 (仅主会话)
│   ├── memory/            # 每日记忆文件
│   └── .learnings/        # 学习日志
└── skills/                # 技能目录
```

## 何时使用

| 场景 | 方案 |
|------|------|
| 需要专用 Agent 处理特定领域任务 | 创建新 Agent |
| 需要隔离会话历史 | 使用多 Agent 路由 |
| 不同任务需要不同模型/工具配置 | 配置 Agent 专属设置 |
| 团队协作需要独立上下文 | 创建团队 Agent |
| 多人共用 Gateway 但需要私密对话 | 配置 `dmScope: per-channel-peer` |
| 同一用户跨频道保持会话连续 | 配置 `identityLinks` |
| 飞书/钉钉群需要绑定特定 Agent | 配置 `bindings` + `requireMention` |

## 可选机制选择器

**不是每个 Agent 都需要以下所有机制**。根据实际需求选择：

| 机制 | 使用时机 | 配置位置 |
|------|---------|---------|
| **Bindings** | 需要精确控制消息路由到哪个 Agent | `bindings[]` |
| **dmScope** | 多人使用同一个聊天账号，需要隔离私密对话 | `session.dmScope` |
| **identityLinks** | 同一用户在多个频道联系你，希望共享会话 | `session.identityLinks` |
| **sendPolicy** | 阻止某些会话类型的消息发送（如 cron 任务不回复） | `session.sendPolicy` |
| **session.maintenance** | 高频率会话，需要自动清理过期会话 | `session.maintenance` |
| **threadBindings** | Discord/Slack 线程需要独立会话 | `session.threadBindings` |
| **sandbox** | 运行不受信代码或需要安全隔离 | `agents[].sandbox` |
| **tools allow/deny** | 限制 Agent 可使用的工具（如家庭 Agent 不允许写文件） | `agents[].tools` |
| **Feishu 群绑定** | 飞书特定群组需要特定 Agent 响应 | `channels.feishu.groups` |

### 机制配置示例

#### 1. Bindings - 消息路由

```json5
{
  agents: {
    list: [
      { id: "home", workspace: "~/.openclaw/workspace-home" },
      { id: "work", workspace: "~/.openclaw/workspace-work" },
    ],
  },
  bindings: [
    // 飞书特定用户 → work Agent
    { agentId: "work", match: { channel: "feishu", peer: { kind: "direct", id: "ou_xxx" } } },
    // 飞书特定群组 → work Agent
    { agentId: "work", match: { channel: "feishu", peer: { kind: "group", id: "oc_xxx" } } },
    // WhatsApp 默认 → home Agent
    { agentId: "home", match: { channel: "whatsapp" } },
  ],
}
```

#### 2. dmScope - DM 会话隔离

```json5
{
  session: {
    // 多人共用一个 WhatsApp 号，每人独立会话
    dmScope: "per-channel-peer",
    // 同一用户跨频道合并会话
    identityLinks: {
      alice: ["telegram:123456789", "feishu:ou_xxx"],
    },
  },
}
```

#### 3. 飞书群组配置

```json5
{
  channels: {
    feishu: {
      dmPolicy: "pairing",
      groupPolicy: "allowlist",
      groupAllowFrom: ["oc_group1", "oc_group2"],
      groups: {
        "oc_group1": {
          requireMention: true,  // 需要 @机器人
          allowFrom: ["ou_user1", "ou_user2"],  // 允许控制命令的用户
        },
      },
    },
  },
}
```

#### 4. Agent 工具限制

```json5
{
  agents: {
    list: [
      {
        id: "family",
        workspace: "~/.openclaw/workspace-family",
        sandbox: { mode: "all", scope: "agent" },
        tools: {
          allow: ["read", "exec"],
          deny: ["write", "edit", "apply_patch", "browser"],
        },
      },
    ],
  },
}
```

#### 5. 会话维护

```json5
{
  session: {
    maintenance: {
      mode: "enforce",
      pruneAfter: "30d",       // 30 天后清理
      maxEntries: 500,         // 最多 500 个会话
      rotateBytes: "10mb",     // sessions.json 超过 10MB 时轮转
    },
  },
}
```

## 快速参考

### 创建新 Agent 流程

1. **创建工作空间**
   ```bash
   mkdir -p ~/openclaw-workspaces/<agent-name>
   cd ~/openclaw-workspaces/<agent-name>
   openclaw setup --workspace .
   ```

2. **创建 Bootstrap 文件**
   ```bash
   # 必需文件
   touch AGENTS.md SOUL.md TOOLS.md USER.md
   # 可选：初次运行引导
   touch BOOTSTRAP.md
   ```

3. **注册 Agent**
   ```bash
   openclaw agents create <agent-name> --workspace ~/openclaw-workspaces/<agent-name>
   ```

4. **配置模型**
   ```bash
   openclaw agents config <agent-name> --model anthropic/claude-sonnet-4-5-20250929
   ```

## 核心配置文件

### AGENTS.md - 工作流指令

定义 Agent 的行为规范、工作流程和自动化规则。

```markdown
# 你的工作空间

## 每次会话前
1. 阅读 SOUL.md — 你是谁
2. 阅读 USER.md — 你帮助谁
3. 阅读 memory/YYYY-MM-DD.md — 最近上下文

## 安全规则
- 不泄露私密数据
- 破坏性操作前必须询问
- 使用 `trash` 而非 `rm`

## 工具使用
- 检查技能的 SKILL.md
- 本地配置写在 TOOLS.md
```

### SOUL.md - 角色人格

定义 Agent 的身份、语气、边界和原则。

```markdown
# 你的身份

## 你是谁
- 名称：[Agent 名称]
- 角色：[专业领域]
- 语气：[专业/友好/简洁]

## 原则
- 主动但不打扰
- 准确优于快速
- 不确定时询问
```

### TOOLS.md - 工具说明

记录工具的使用细节、集成要点和本地配置。

```markdown
# 工具配置

## 本地工具
- 浏览器：`browser.enabled: true`
- 沙箱：`sandbox.enabled: false`

## 集成细节
- 数据库连接字符串
- API 端点配置
- 认证凭据位置
```

### USER.md - 用户配置

定义用户偏好、联系方式和特殊需求。

```markdown
# 用户信息

## 联系方式
- 首选频道：WhatsApp / Telegram / Discord
- 时区：Asia/Shanghai
- 语言：中文

## 偏好
- 回复风格：简洁/详细
- 主动检查：每日 2-4 次
```

## Agent 目录结构

### 主 Agent (main)

```
~/.openclaw/agents/main/
├── agent/
│   ├── auth.json          # 认证令牌
│   └── models.json        # 模型配置
└── sessions/
    └── <sessionId>.jsonl  # 会话历史
```

### 专用 Agent

```
~/.openclaw/agents/<agent-id>/
├── agent/
│   ├── auth.json
│   └── models.json
└── sessions/
    └── <sessionId>.jsonl
```

## 多 Agent 路由

OpenClaw 支持为不同任务创建隔离的 Agent 会话：

```json5
// ~/.openclaw/openclaw.json
{
  agents: {
    defaults: {
      workspace: "~/.openclaw/workspace",
      model: "anthropic/claude-sonnet-4-5-20250929",
      timeoutSeconds: 600,
    },
    // 多 Agent 配置
    entries: {
      "finance": {
        workspace: "~/openclaw-workspaces/finance",
        model: "anthropic/claude-sonnet-4-5-20250929",
      },
      "supervisor": {
        workspace: "~/openclaw-workspaces/supervisor",
        model: "anthropic/claude-opus-4-5-20250929",
      },
    },
  },
}
```

## 会话管理

### 会话存储

会话历史以 JSONL 格式存储：

```
~/.openclaw/agents/<agentId>/sessions/<sessionId>.jsonl
```

### 会话工具

```bash
# 列出所有会话
openclaw sessions list

# 查看会话历史
openclaw sessions history <sessionId>

# 创建新会话
openclaw sessions new --agent <agent-name>

# 删除会话
openclaw sessions delete <sessionId>
```

## 技能系统

### 技能加载顺序

1. **工作空间技能** (`<workspace>/skills`) - 最高优先级
2. **本地技能** (`~/.openclaw/skills`)
3. **捆绑技能** (安装包自带) - 最低优先级

### 技能配置

```json5
// ~/.openclaw/openclaw.json
{
  skills: {
    entries: {
      "skill-name": {
        enabled: true,
        apiKey: "YOUR_API_KEY",
        env: {
          "API_KEY": "value",
        },
        config: {
          "customSetting": "value",
        },
      },
    },
    load: {
      watch: true,        // 自动刷新技能
      watchDebounceMs: 250,
    },
  },
}
```

### 创建自定义技能

```bash
mkdir -p ~/.openclaw/skills/<skill-name>
touch ~/.openclaw/skills/<skill-name>/SKILL.md
```

SKILL.md 格式：

```markdown
---
name: skill-name
description: 使用当...（具体触发条件）
metadata:
  {
    "openclaw": {
      "requires": { "bins": ["uv"], "env": ["API_KEY"] },
    },
  }
---

# Skill Name

## 概述
核心原则简述

## 何时使用
- 触发条件 1
- 触发条件 2

## 快速参考
| 场景 | 操作 |
|------|------|
| 情况 A | 执行 X |

## 示例
代码示例或工作流程
```

## Agent Loop 流程

OpenClaw Agent 执行循环：

```
1. 接收消息 → 2. 加载会话 → 3. 组装上下文 → 
4. 构建 Prompt → 5. 模型推理 → 6. 执行工具 → 
7. 流式响应 → 8. 持久化会话
```

### Hook 点

```json5
{
  hooks: {
    // Agent 生命周期
    "agent:bootstrap": ["script.sh"],
    "agent_end": ["script.sh"],
    
    // 工具执行
    "before_tool_call": ["script.sh"],
    "after_tool_call": ["script.sh"],
    
    // 消息处理
    "message_received": ["script.sh"],
    "message_sending": ["script.sh"],
  },
}
```

## 模型配置

### 配置模型

```bash
# 为 Agent 配置模型
openclaw agents config <agent-name> --model <provider>/<model>

# 可用模型
openclaw models list
```

### 模型故障转移

```json5
{
  agents: {
    defaults: {
      models: [
        "anthropic/claude-sonnet-4-5-20250929",
        "openai/gpt-4o",
        "openrouter/anthropic/claude-3.5-sonnet",
      ],
    },
  },
}
```

## 沙箱模式

### 启用沙箱

```json5
{
  agents: {
    defaults: {
      sandbox: {
        enabled: true,
        docker: {
          image: "node:22-alpine",
          setupCommand: "apk add --no-cache git python3",
        },
        workspaceRoot: "~/.openclaw/sandboxes",
      },
    },
  },
}
```

### 沙箱技能要求

技能需要在沙箱内外都存在：

1. 主机：检查二进制文件
2. 沙箱：通过 `setupCommand` 安装依赖

## 记忆系统

### 每日记忆

```bash
mkdir -p ~/.openclaw/workspace/memory
touch ~/.openclaw/workspace/memory/$(date +%Y-%m-%d).md
```

### 长期记忆

`MEMORY.md` 仅在主会话加载，用于存储：
- 重要决策
- 用户偏好
- 项目上下文
- 学习总结

### 记忆升级

当学习具有广泛适用性时，升级到相应文件：

| 学习类型 | 升级到 |
|---------|--------|
| 行为模式 | `SOUL.md` |
| 工作流改进 | `AGENTS.md` |
| 工具技巧 | `TOOLS.md` |

## 心跳机制

### 配置心跳

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        enabled: true,
        intervalMinutes: 30,
        prompt: "HEARTBEAT.md",
      },
    },
  },
}
```

### 心跳检查清单

创建 `HEARTBEAT.md`：

```markdown
# 心跳检查

- [ ] 检查紧急邮件
- [ ] 查看 24 小时内日历事件
- [ ] 检查天气（如有外出计划）
- [ ] 无重要事项回复 HEARTBEAT_OK
```

## 常见问题

### Agent 无法启动

1. 检查工作空间是否存在
2. 验证 `openclaw.json` 配置
3. 查看日志：`openclaw logs`

### 技能未加载

1. 检查技能名称匹配
2. 验证 `enabled: true`
3. 确认环境变量/二进制文件存在

### 会话历史丢失

1. 检查 `agents/<agentId>/sessions/` 目录
2. 验证 JSONL 文件格式
3. 确认 Agent ID 正确

## 最佳实践

1. **为专用任务创建独立 Agent** - 财务、监控、开发等
2. **使用工作空间技能覆盖捆绑技能** - 自定义行为
3. **定期清理会话历史** - 避免存储膨胀
4. **记录学习日志** - 使用 `.learnings/` 目录
5. **配置心跳主动检查** - 而非被动响应
6. **使用沙箱运行不受信代码** - 安全第一

## 配置请求（交互式）

创建新 Agent 前，向用户请求以下信息：

### 必填项

```
1. Agent 名称/ID（用于标识，如：finance, supervisor, dev）
2. 工作空间路径（默认：~/openclaw-workspaces/<name>）
3. 使用场景（如：财务管理、代码开发、群组机器人）
```

### 可选项（根据场景询问）

```
4. 是否需要绑定特定频道/群组？
   → 是：询问频道类型 (feishu/whatsapp/telegram) 和 ID
   
5. 是否需要多 Agent 路由？
   → 是：询问 bindings 配置
   
6. 是否需要安全沙箱？
   → 是：配置 sandbox.mode: "all"
   
7. 是否需要限制工具权限？
   → 是：配置 tools.allow/deny
   
8. 多人使用同一个聊天账号？
   → 是：配置 dmScope: "per-channel-peer"
   
9. 同一用户需要跨频道共享会话？
   → 是：配置 identityLinks
```

### 请求模板

```markdown
**创建 Agent 配置请求**

请提供以下信息：

**必填：**
- Agent 名称：[用于标识，如 finance/supervisor]
- 用途：[简要描述，如"财务管理"或"飞书群组机器人"]

**可选：**
- [ ] 需要绑定特定飞书群/用户
- [ ] 需要多 Agent 路由（多个聊天账号）
- [ ] 需要安全沙箱隔离
- [ ] 需要限制工具权限
- [ ] 多人共用聊天账号（需要 dmScope 隔离）

请回复或逐项提供，我将生成完整配置。
```

## 部署检查清单

创建新 Agent 后验证：

- [ ] 工作空间目录存在
- [ ] Bootstrap 文件已创建
- [ ] Agent 配置已注册
- [ ] 模型配置正确
- [ ] 技能已加载
- [ ] 会话可以创建
- [ ] 工具可以执行

---

**参考文档：**
- [OpenClaw Docs](https://docs.openclaw.ai/)
- [Agent Runtime](https://docs.openclaw.ai/concepts/agent.md)
- [Skills](https://docs.openclaw.ai/tools/skills.md)
- [Workspace](https://docs.openclaw.ai/concepts/agent-workspace.md)
