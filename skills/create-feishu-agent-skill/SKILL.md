# 创建飞书 Agent 技能

快速创建新的 OpenClaw Agent 并连接到飞书机器人。

## 触发条件

- 用户要求"创建新的 agent"
- 用户要求"添加飞书机器人"
- 用户要求"创建健康助手/技术专家/xxx助手"

## 完整流程

### 第一步：创建 Agent 目录结构

```bash
# 在 workspace/agents/ 下创建新 agent
mkdir -p ~/.openclaw/workspace/agents/<agent_name>

# 必需文件
touch ~/.openclaw/workspace/agents/<agent_name>/SOUL.md      # 人设文件
touch ~/.openclaw/workspace/agents/<agent_name>/IDENTITY.md  # 身份文件
touch ~/.openclaw/workspace/agents/<agent_name>/AGENTS.md    # 继承主workspace规则
touch ~/.openclaw/workspace/agents/<agent_name>/MEMORY.md    # 长期记忆
```

### 第二步：编写 SOUL.md（人设文件）

```markdown
# SOUL.md - <Agent名称>

## Core Truths
- 核心原则1
- 核心原则2

## What You Do
- 职责1
- 职责2

## Boundaries
- 边界1
- 边界2

## Vibe
性格描述
```

### 第三步：创建飞书应用

1. 访问 [飞书开放平台](https://open.feishu.cn/)
2. 创建企业自建应用
3. 记录 `App ID` 和 `App Secret`
4. 配置权限：
   - `im:message` - 获取和发送消息
   - `im:message.group_msg` - 获取群消息
   - `im:chat:read` - 读取群聊信息
   - 其他按需添加

5. 配置事件订阅：
   - `im.message.receive_v1` - 接收消息

6. 发布应用并添加到企业

### 第四步：配置 OpenClaw

编辑 `~/.openclaw/openclaw.json`：

```json5
{
  // 1. 添加飞书账户
  channels: {
    feishu: {
      accounts: {
        "<account-name>": {
          appId: "cli_xxxx",        // 飞书 App ID
          appSecret: "xxx",          // 飞书 App Secret
          name: "<显示名称>",
          enabled: true,
          connectionMode: "websocket",
          domain: "feishu",
          groupPolicy: "open",       // 允许群聊触发
          requireMention: false      // 不需要@也能触发
        }
      }
    }
  },

  // 2. 添加 Agent 配置
  agents: {
    entries: [
      {
        id: "<agent_name>",
        name: "<Agent显示名称>",
        workspace: "/Users/<user>/.openclaw/workspace/agents/<agent_name>",
        model: "zai/glm-5"  // 或其他模型
      }
    ],
    // ...
  },

  // 3. 添加绑定规则
  bindings: [
    {
      agentId: "<agent_name>",
      match: {
        channel: "feishu",
        accountId: "<account-name>"
      }
    }
  ]
}
```

### 第五步：重启 Gateway

```bash
openclaw gateway restart
```

### 第六步：验证配置

```bash
# 检查 agent 列表
openclaw agents list

# 检查 gateway 状态
openclaw gateway status

# 检查日志
tail -f /tmp/openclaw/openclaw-$(date +%Y-%m-%d).log
```

### 第七步：测试

1. 将机器人添加到飞书群聊
2. 在群里发送消息
3. 检查日志是否收到消息
4. 检查机器人是否回复

## 常见问题

### Q1: 群消息收不到

**检查：**
1. 飞书应用是否已发布
2. 机器人是否已添加到群
3. 事件订阅是否正确配置
4. `groupPolicy: "open"` 和 `requireMention: false` 是否设置

### Q2: 机器人发的消息不触发回调

**原因：** 飞书限制机器人发送的消息不会触发自己的回调事件

**解决：** 需要在代码层面手动触发（参见双机互聊实现）

### Q3: 模型调用失败

**检查：**
1. API Key 是否正确配置
2. 模型名称是否正确（如 `zai/glm-5`）
3. 网络是否可达

## 文件模板

### SOUL.md 模板

```markdown
# SOUL.md - <Agent名称>

_一句话描述_

## Core Truths

**原则1。** 解释...

**原则2。** 解释...

## What You Do

### 功能1
- 具体说明

### 功能2
- 具体说明

## Boundaries

- 边界1
- 边界2

## Vibe

性格描述
```

### AGENTS.md 模板

```markdown
# AGENTS.md - <Agent名称> Workspace

继承主 workspace 规则，并根据 agent 特性调整。

## 职责

- 职责1
- 职责2

## 触发条件

- 条件1
- 条件2
```

## Health Manager 创建案例

### 目录结构

```
~/.openclaw/workspace/agents/health_manager/
├── AGENTS.md
├── IDENTITY.md
├── SOUL.md          # 健康守护者人设
├── MEMORY.md        # 长期记忆
├── TOOLS.md
├── USER.md
├── HEARTBEAT.md
└── memory/          # 记忆存储
```

### 配置摘要

| 项目 | 值 |
|------|-----|
| Agent ID | health_manager |
| 飞书账户 | health-manager |
| App ID | cli_a912246713789bb5 |
| 模型 | minimax-portal/MiniMax-M2.5 |
| 群聊策略 | open |
| 需要@ | false |

### SOUL.md 核心内容

- 角色：健康守护者
- 风格：关心但不啰嗦，基于数据
- 职责：监控在线时长、分析心率、干预过劳
- 边界：健康数据私密，建议不强制

---

*文档版本: 1.0*
*最后更新: 2026-02-21*
