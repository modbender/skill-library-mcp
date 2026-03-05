---
name: skill-manager
description: Install and manage OpenClaw agent skills. Learn how to find, install, and configure new capabilities from ClawHub and GitHub.
---

# OpenClaw Skills 安装指南

本技能基于视频教程：https://www.bilibili.com/video/BV1PbFUzZEvN

## 概述

OpenClaw 是目前最流行的 AI 智能体。要让它变强，需要安装更多的技能包（Agent Skills）。

## 安装方法

### 方法1：使用 Vercel CLI

```bash
# 安装 Vercel Skills 工具
npm install -g @vercel/skills

# 查看可用技能
skills

# 安装技能
skills install <skill-name>

# 例如安装天气技能
skills install weather
```

### 方法2：使用 ClawHub

```bash
# 安装 clawdhub 工具
npm install -g clawdhub

# 搜索技能
clawdhub search <keyword>

# 安装技能
clawdhub install <owner/skill-name>

# 例如
clawdhub install steipete/weather
```

### 方法3：从 GitHub 直接安装

```bash
# 克隆技能仓库
git clone https://github.com/<owner>/<skill-repo>.git ~/.openclaw/workspace/skills/<skill-name>

# 或者使用 npx
npx clawdhub install <owner>/<skill-name>
```

## 常用技能推荐

### 必备
- weather - 天气查询
- brave-search / tavily-search - 网页搜索
- summarize - 内容总结

### 开发
- github - GitHub 操作
- openai-whisper - 语音转文字
- humanizer - 文字润色

### 生产力
- gog - Google Workspace
- notion - Notion 集成
- obsidian - 笔记管理

### 进阶
- self-improving-agent - 自我改进
- proactive-agent - 主动预判
- ontology - 知识图谱

## 技能存放位置

```
~/.openclaw/workspace/skills/
├── weather/
│   ├── SKILL.md
│   ├── install.sh
│   └── ...
├── brave-search/
│   └── ...
└── ...
```

## 验证安装

```bash
# 列出已安装技能
ls ~/.openclaw/workspace/skills/

# 查看技能详情
cat ~/.openclaw/workspace/skills/<skill-name>/SKILL.md
```

## 注意事项

1. 部分技能需要配置 API Key（如 Tavily、Brave、OpenAI 等）
2. 有些技能需要安装额外的 npm 包
3. 建议阅读每个技能的 SKILL.md 了解具体用法
