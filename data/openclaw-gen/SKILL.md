---
name: openclaw-gen
description: OpenClaw Agent tool that generates OpenClaw project configurations (AGENTS.md, workflows, MEMORY.md) using OpenClaw's unified llm-task interface. 15 built-in templates.
user-invocable: true
metadata:
  openclaw:
    emoji: 🛠️
    requires:
      bins: ["node"]
---

# OpenClaw Template Generator

OpenClaw Agent 工具：使用 `llm-task` 统一接口，自动生成 OpenClaw 项目配置。

## 🎯 核心特点

- **🤖 纯 Agent 模式**：只在 OpenClaw Agent 内运行
- **🔌 统一接口**：使用 `llm-task`，无额外 API 配置
- **📦 15 个模板**：覆盖常见场景

## 🏗️ 工作流程

```
用户需求
    ↓
OpenClaw Agent
    ↓
llm-task (OpenClaw 统一接口)
    ↓
生成 AGENTS.md + workflows + MEMORY.md
```

## 🤖 Agent 使用方式

当用户需要创建新项目时，Agent 执行：

```json
{
  "tool": "llm-task",
  "parameters": {
    "prompt": "用户需求描述",
    "model": "MiniMax-M2.1"
  }
}
```

### 示例对话

```
用户："创建一个天气助手"
Agent："好的，我会使用 llm-task 生成配置..."
```

## 📦 内置模板 (15个)

| 模板 | 描述 |
|------|------|
| daily-assistant | 每日任务助手 |
| weather-bot | 天气摘要机器人 |
| github-monitor | GitHub 仓库监控 |
| email-assistant | 邮件助手 |
| social-media-manager | 社交媒体管理 |
| research-assistant | 研究助手 |
| finance-tracker | 财务追踪 |
| devops-monitor | DevOps 监控 |
| personal-assistant | 个人助手 |
| fitness-tracker | 健身追踪 |
| language-learner | 语言学习 |
| meeting-assistant | 会议助手 |
| reading-companion | 阅读伴侣 |
| travel-planner | 旅行规划 |
| content-creator | 内容创作 |

## 📁 生成文件结构

```
[项目名]/
├── AGENTS.md          → Agent 角色定义
├── workflows/        → 工作流配置
│   └── *.yaml
├── MEMORY.md          → 记忆配置
└── README.md          → 使用说明
```

## ⚙️ 统一接口

### llm-task 配置

在 `~/.openclaw/openclaw.json` 中启用：

```json
{
  "plugins": {
    "entries": {
      "llm-task": { "enabled": true }
    }
  }
}
```

**优点**：
- ✅ 屏蔽模型差异
- ✅ 复用 OpenClaw 配置
- ✅ 无需额外 API Key

## 📄 配置文件

- **README.md**：快速使用说明
- **AGENT.md**：Agent 配置示例
- **templates/**：内置模板目录

## 📚 相关链接

- GitHub: https://github.com/marie6789040106650/openclaw-template-generator
- ClawHub: `clawhub install openclaw-gen`

## 📄 许可证

MIT
