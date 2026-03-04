# create-agent Skill

**一键创建新的 OpenClaw Agent**

---

## 快速开始

### 安装

```bash
# 已手动安装到 ~/.openclaw/workspace/skills/create-agent/
```

### 使用

```bash
# 交互模式（推荐新手）
python3 ~/.openclaw/workspace/skills/create-agent/scripts/create_agent.py --help

# 创建写作 Agent
python3 ~/.openclaw/workspace/skills/create-agent/scripts/create_agent.py \
  --id "inkflow" \
  --name "写作与分享助手" \
  --role "writer" \
  --model "bailian/qwen3.5-plus" \
  --channel "telegram" \
  --emoji "🖋️"

# 创建前端工程师
python3 ~/.openclaw/workspace/skills/create-agent/scripts/create_agent.py \
  --id "dev-fe" \
  --name "前端工程师" \
  --role "dev-fe" \
  --emoji "💻"

# 预览不执行（dry-run）
python3 ~/.openclaw/workspace/skills/create-agent/scripts/create_agent.py \
  --id "dev-new" \
  --name "新 Agent" \
  --role "custom" \
  --dry-run
```

---

## 预设角色

| Role | 说明 | 默认模型 | Emoji |
|------|------|----------|-------|
| `dev-tl` | 技术负责人 + 产品设计 | `openai-codex/gpt-5.3-codex` | 🧭 |
| `dev-fs` | 全栈工程师 | `openai-codex/gpt-5.3-codex` | 🛠️ |
| `dev-qa` | 测试工程师 | `openai-codex/gpt-5.3-codex` | ✅ |
| `dev-ops` | 运维工程师 | `openai-codex/gpt-5.3-codex` | 🚦 |
| `writer` | 写作与分享助手 | `bailian/qwen3.5-plus` | 🖋️ |
| `analyst` | 数据分析师 | `bailian/qwen3.5-plus` | 📊 |
| `researcher` | 研究员 | `bailian/qwen3.5-plus` | 🔍 |
| `custom` | 自定义角色 | `bailian/qwen3.5-plus` | 🤖 |

---

## 自动化内容

### 创建的文件

```
~/.openclaw/agents/<id>/agent/
├── IDENTITY.md    # 身份定义
├── SOUL.md        # 角色定位
├── AGENTS.md      # 工作流程（引用 TEAM.md）
├── USER.md        # 用户偏好
└── auth.json      # 认证信息

~/.openclaw/workspace-<id>/
├── AGENTS.md      # 引用 TEAM.md
├── SOUL.md        # 同步自 agent 目录
├── USER.md        # 同步自 agent 目录
├── IDENTITY.md    # 同步自 agent 目录
└── memory/        # 记忆文件
```

### 自动配置

1. **openclaw.json**
   - 添加 agent 到 `agents.list`
   - 添加 binding 规则
   - 添加 channel 账号配置

2. **TEAM.md**
   - 添加新 agent 信息
   - 更新变更历史

---

## 创建后步骤

1. **配置 Channel Token**（如需要）
   ```bash
   # Telegram: 编辑 openclaw.json
   channels.telegram.accounts.<id>.botToken = "<token>"
   
   # 飞书：设置环境变量
   export DEV_XX_APP_ID="cli_xxx"
   export DEV_XX_APP_SECRET="xxx"
   ```

2. **重启 Gateway**
   ```bash
   openclaw gateway restart
   ```

3. **验证**
   ```bash
   openclaw agents list --bindings
   openclaw channels status
   ```

---

## 基于实战经验

本 skill 基于 2026-02-28 创建 InkFlow agent 的完整流程总结：

- ✅ 团队架构设计（单一事实来源）
- ✅ 身份文件模板
- ✅ 自动配置 openclaw.json
- ✅ 自动更新 TEAM.md
- ✅ Channel 账号管理

---

## 许可证

MIT License
