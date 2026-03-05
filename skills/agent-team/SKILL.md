# agent-team - 多 Agent 团队管理系统

管理和调用具有不同"灵魂"的子 Agent 团队，每个 Agent 拥有独特的身份定义和专用模型。

## 使用方法

### 基础命令
```bash
agent-team list                      # 列出所有 Agent
agent-team show <name>              # 查看 Agent 详情
agent-team spawn <name> [task]      # 启动 Agent 执行任务
agent-team chat <name>              # 与 Agent 交互对话
```

### 示例
```bash
# 查看团队所有成员
agent-team list

# 查看 Coder 的详细信息
agent-team show coder

# 让 Coder 帮你写代码
agent-team spawn coder "写一个快速排序算法"

# 与 Writer 对话讨论写作
agent-team chat writer
```

## 内置 Agent 团队

| Agent | 角色 | 主模型 | 专长 |
|:---:|:---|:---|:---|
| 🧑‍💻 **coder** | 代码专家 | qwen3-coder-next | 编程、重构、测试 |
| ✍️ **writer** | 写作专家 | qwen3.5-plus | 文档、博客、创意写作 |
| 📊 **analyst** | 数据专家 | qwen3.5-plus | 数据分析、可视化 |
| 🔍 **researcher** | 调研专家 | gemini-3.1-pro | 文献调研、竞品分析 |
| 👀 **reviewer** | 审查专家 | qwen3-max | 代码审查、质量把关 |

## 创建新 Agent

### 1. 创建目录
```bash
mkdir -p ~/.openclaw/workspace/agents/<agent-name>
```

### 2. 定义 SOUL.md
```markdown
# SOUL.md - <Agent Name>

## 身份
你是...

## 性格特质
- ...

## 专业领域
- ...

## 沟通风格
- ...
```

### 3. 创建 config.json
```json
{
  "name": "AgentName",
  "role": "角色描述",
  "emoji": "🤖",
  "model": {
    "primary": "dashscope/qwen3.5-plus",
    "fallback": "google/gemini-3-flash-preview"
  },
  "capabilities": ["能力 1", "能力 2"]
}
```

## 模型配置说明

每个 Agent 可以配置不同的模型：

- **dashscope/qwen3-coder-next**: 编码专用
- **dashscope/qwen3.5-plus**: 通用中文优化
- **dashscope/qwen3-max**: 最强推理
- **google/gemini-3.1-pro**: 深度研究
- **google/gemini-3-flash-preview**: 快速响应

## 工作模式

### 1. 任务模式 (spawn)
```bash
agent-team spawn coder "优化这个函数"
```
- 创建独立子代理会话
- 执行指定任务
- 完成后返回结果

### 2. 对话模式 (chat)
```bash
agent-team chat analyst
```
- 进入交互式对话
- 保持角色一致性
- 适合复杂协作

## 高级用法

### 并行多 Agent
```bash
# 同时启动多个 Agent
agent-team spawn coder "写代码" &
agent-team spawn writer "写文档" &
agent-team spawn reviewer "审查代码" &
wait
```

### 链式调用
```bash
# Coder 写代码 → Reviewer 审查 → Writer 写文档
agent-team spawn coder "实现功能"
agent-team spawn reviewer "审查代码"
agent-team spawn writer "编写文档"
```

## 文件结构

```
~/.openclaw/workspace/
├── agents/
│   ├── coder/
│   │   ├── SOUL.md       # 身份定义
│   │   └── config.json   # 模型配置
│   ├── writer/
│   └── ...
└── skills/
    └── agent-team/
        ├── agent-team.py  # 管理脚本
        └── SKILL.md       # 本文档
```

## 故障排除

1. **Agent 未找到**: 检查 `~/.openclaw/workspace/agents/` 目录
2. **模型不可用**: 确认模型配置正确且 API Key 有效
3. **会话无法创建**: 检查 OpenClaw 网关状态

## 相关技能

- `sessions_spawn`: OpenClaw 原生子代理创建
- `self-improving`: 自我进化记忆系统
