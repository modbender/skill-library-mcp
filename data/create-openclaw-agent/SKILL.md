---
name: create-agent
description: 或手动安装：
---

# create-agent

**version:** 1.0.0  
**author:** 大总管  
**description:** 一键创建新的 OpenClaw agent，包含完整的身份定义、团队集成和配置

---

## 功能

- ✅ 创建 agent 目录结构
- ✅ 生成身份文件模板（IDENTITY.md/SOUL.md/AGENTS.md/USER.md）
- ✅ 自动更新 `openclaw.json`（agents.list + bindings）
- ✅ 自动更新 `TEAM.md`（团队架构）
- ✅ 支持多种预设角色（开发/测试/运维/写作/产品等）
- ✅ 支持自定义模型和 Channel 配置

---

## 安装

```bash
clawhub install create-agent
```

或手动安装：

```bash
git clone <repo> ~/.openclaw/workspace/skills/create-agent
```

---

## 使用方法

### 交互式模式（推荐）

```bash
python3 ~/.openclaw/workspace/skills/create-agent/scripts/create_agent.py
# 或
python3 ~/.openclaw/workspace/skills/create-agent/scripts/create_agent.py --interactive
```

按提示输入：
1. **Agent ID**（如 `dev-fe`）
2. **Agent 名称**（如 `前端工程师`）
3. **选择预设角色**（8 个模板可选）
4. **选择模型**（4 个常用模型）
5. **选择 Channel**（telegram/飞书）
6. **选择 Emoji**
7. **确认工作区路径**
8. **预览或执行**

### 命令行模式

```bash
openclaw skill create-agent \
  --id "dev-fe" \
  --name "前端工程师" \
  --role "frontend" \
  --model "openai-codex/gpt-5.3-codex" \
  --channel "feishu" \
  --emoji "💻"
```

### 创建写作 Agent（示例）

```bash
openclaw skill create-agent \
  --id "inkflow" \
  --name "写作与分享助手" \
  --role "writer" \
  --model "bailian/qwen3.5-plus" \
  --channel "telegram" \
  --emoji "🖋️" \
  --workspace "/root/.openclaw/workspace-writing"
```

---

## 参数说明

| 参数 | 必填 | 说明 | 默认值 |
|------|------|------|--------|
| `--id` | ✅ | Agent ID（字母 + 数字 + 连字符） | - |
| `--name` | ✅ | Agent 显示名称 | - |
| `--role` | ❌ | 预设角色模板 | `custom` |
| `--model` | ❌ | 使用的模型 | `bailian/qwen3.5-plus` |
| `--channel` | ❌ | 通信渠道 | `telegram` |
| `--emoji` | ❌ | Agent emoji | `🤖` |
| `--workspace` | ❌ | 工作区路径 | `/root/.openclaw/workspace-<id>` |
| `--dry-run` | ❌ | 预览不执行 | `false` |

---

## 预设角色模板

### 开发团队角色

| Role | 说明 | 默认模型 |
|------|------|----------|
| `dev-tl` | 技术负责人 + 产品设计 | `openai-codex/gpt-5.3-codex` |
| `dev-fs` | 全栈工程师 | `openai-codex/gpt-5.3-codex` |
| `dev-qa` | 测试工程师 | `openai-codex/gpt-5.3-codex` |
| `dev-ops` | 运维工程师 | `openai-codex/gpt-5.3-codex` |
| `dev-fe` | 前端工程师 | `openai-codex/gpt-5.3-codex` |
| `dev-be` | 后端工程师 | `openai-codex/gpt-5.3-codex` |

### 其他角色

| Role | 说明 | 默认模型 |
|------|------|----------|
| `writer` | 写作与分享助手 | `bailian/qwen3.5-plus` |
| `analyst` | 数据分析师 | `bailian/qwen3.5-plus` |
| `researcher` | 研究员 | `bailian/qwen3.5-plus` |
| `custom` | 自定义角色 | `bailian/qwen3.5-plus` |

---

## 生成的文件

### Agent 目录结构

```
~/.openclaw/agents/<id>/agent/
├── IDENTITY.md    # 身份定义
├── SOUL.md        # 角色定位和工作原则
├── AGENTS.md      # 工作流程（引用 TEAM.md）
├── USER.md        # 用户偏好
├── auth.json      # 认证信息（自动生成）
└── models.json    # 模型配置（自动生成）
```

### 工作区目录

```
~/.openclaw/workspace-<id>/
├── AGENTS.md      # 引用 TEAM.md
├── SOUL.md        # 同步自 agent 目录
├── USER.md        # 同步自 agent 目录
├── IDENTITY.md    # 同步自 agent 目录
├── memory/        # 记忆文件
└── .openclaw/     # 会话存储
```

---

## 自动配置

### 1. 更新 `openclaw.json`

自动添加：

```json
{
  "agents": {
    "list": [
      {
        "id": "<id>",
        "name": "<name>",
        "workspace": "<workspace>",
        "agentDir": "~/.openclaw/agents/<id>/agent",
        "model": "<model>",
        "identity": {
          "name": "<name>",
          "theme": "<role>",
          "emoji": "<emoji>"
        }
      }
    ]
  },
  "bindings": [
    {
      "agentId": "<id>",
      "match": {
        "channel": "<channel>",
        "accountId": "<id>"
      }
    }
  ]
}
```

### 2. 更新 `TEAM.md`

自动添加新 agent 信息到团队架构文档。

### 3. 创建 Channel 账号

如需要，自动在 `channels.<channel>.accounts` 中添加账号配置。

---

## 示例输出

```bash
$ openclaw skill create-agent --id "dev-fe" --name "前端工程师" --role "dev-fe"

🔧 正在创建 agent: dev-fe

[1/6] 创建目录结构...
  ✓ ~/.openclaw/agents/dev-fe/agent/
  ✓ ~/.openclaw/workspace-dev-fe/

[2/6] 生成身份文件...
  ✓ IDENTITY.md
  ✓ SOUL.md
  ✓ AGENTS.md
  ✓ USER.md

[3/6] 更新 openclaw.json...
  ✓ 添加 agent 到 agents.list
  ✓ 添加 binding 规则
  ✓ 添加 telegram 账号配置

[4/6] 更新 TEAM.md...
  ✓ 添加 dev-fe 到团队架构

[5/6] 设置文件权限...
  ✓ 认证文件权限：600

[6/6] 验证配置...
  ✓ 配置语法检查通过

✅ Agent "dev-fe" 创建完成！

下一步：
1. 配置 Channel Token（如需要）
2. 重启 Gateway: openclaw gateway restart
3. 验证 agent: openclaw agents list --bindings
```

---

## 后续步骤

### 配置 Channel

根据选择的 Channel，配置相应的 Token：

**Telegram:**
```bash
# 在 BotFather 创建 bot，获取 token
# 编辑 openclaw.json:
channels.telegram.accounts.<id>.botToken = "<token>"
```

**飞书:**
```bash
# 在飞书开放平台创建应用
# 设置环境变量：
export DEV_FE_APP_ID="cli_xxx"
export DEV_FE_APP_SECRET="xxx"
```

### 重启 Gateway

```bash
openclaw gateway restart
```

### 验证

```bash
openclaw agents list --bindings
openclaw channels status
```

---

## 删除 Agent

```bash
openclaw skill delete-agent --id "dev-fe"
```

会：
1. 从 `openclaw.json` 移除配置
2. 从 `TEAM.md` 移除信息
3. 删除 agent 目录（可选备份）
4. 删除工作区目录（可选备份）

---

## 注意事项

### 安全

- 认证文件权限自动设置为 `600`
- Token 建议使用环境变量
- 敏感信息不要提交到版本控制

### 命名规范

- Agent ID：小写字母 + 数字 + 连字符（如 `dev-fe`）
- Agent 名称：中文或英文（如 `前端工程师`）
- 工作区：`~/.openclaw/workspace-<id>`

### 模型选择

| 场景 | 推荐模型 |
|------|----------|
| 代码/配置操作 | `openai-codex/gpt-5.3-codex` |
| 复杂推理 | `anthropic/claude-sonnet-4-6` |
| 日常任务 | `bailian/qwen3.5-plus` |
| 长文本分析 | `bailian/kimi-k2.5` |

---

## 故障排查

### 问题：Gateway 启动失败

```bash
# 检查配置语法
openclaw doctor

# 查看详细日志
openclaw logs --follow
```

### 问题：Agent 不响应

```bash
# 检查路由配置
openclaw agents list --bindings

# 检查 Channel 状态
openclaw channels status
```

### 问题：TEAM.md 更新失败

手动编辑 `/root/.openclaw/workspace/TEAM.md`，添加新 agent 信息。

---

## 变更历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 1.0.0 | 2026-02-28 | 初始版本 |

---

## 许可证

MIT License

---

**来源：** 基于 2026-02-28 创建 InkFlow agent 的实战经验总结
