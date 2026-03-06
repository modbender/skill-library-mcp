---
name: skill-manager-all-in-one
description: "One-stop skill management for OpenClaw. 一站式技能管理，引导式使用，嵌套搜索、审计、创建、发布、批量更新等必要 skill。Use when reviewing installed skills, searching ClawHub, checking updates, auditing security, creating or publishing skills. Triggers: skill, 技能, ClawHub, clawhub, 安装技能, install skill, 搜索技能, search skill, 更新技能, update skill, 创建技能, create skill, 发布技能, publish skill, 卸载技能, uninstall skill, 管理技能, manage skills, 技能管理, skill manager, 技能更新, 技能审计, audit skill, 查看已发布, view published, 宣传技能, promote skills, 技能帮助, skill help, 技能问题, skill problem, 批量更新, bulk update, 技能搜索, 技能安装, 技能发布, ClawHub发布, ClawHub搜索, ClawHub安装, 技能体系, skill system, 技能目录, skill directory, 找技能, find skill, 新技能, new skill, 技能版本, skill version."
---

# Skill Manager | 技能管理器

全面的 OpenClaw 技能管理工具。一站式解决 skill 管理问题。

**⚠️ 系统兼容性 / System Compatibility**
本技能在 **Linux 系统**上测试通过。其他系统（Windows/macOS）可能需要适配。

---

## 核心原则

1. **先本地，后网络** — 优先使用本地已有资源
2. **决定权交给用户** — 任何操作都需讲解给用户并等待确认
3. **命名规范化** — 统一格式，便于管理

---

## 🚨 最高原则：必须先获得用户同意

**任何操作都必须先汇报给用户，获得明确同意后方可执行！**

**特别是以下操作：**
- ❌ 发布技能到 ClawHub
- ❌ 更新/升版技能
- ❌ 发布宣传帖
- ❌ 修改技能内容

**流程：** 汇报 → 用户审核 → 明确同意 → 执行

**❌ 严禁未经同意擅自执行任何操作！**

---

## 快速导航 | Quick Navigation

| 场景 | 参考 |
|------|------|
| 了解术语、目录结构、命名规范 | [terminology.md](references/terminology.md) |
| 搜索、对比、审计技能 | [search-audit.md](references/search-audit.md) |
| 创建、发布、更新技能 | [create-publish-update.md](references/create-publish-update.md) |
| 查看已发布技能、宣传 | [dashboard-promote.md](references/dashboard-promote.md) |

---

## CLI 命令速查

```bash
# 搜索
npx clawhub@latest search <query>

# 查看详情
npx clawhub@latest inspect <slug>

# 安装
npx clawhub@latest install <slug>

# 发布
npx clawhub@latest publish <path> --slug <slug> --name "<name>" --version <version> --changelog "<changelog>"

# 浏览最新
npx clawhub@latest explore
```

---

## 嵌套引用

本 skill 通过**路径引用**其他 skills，不嵌入全文：

| 场景 | 引用路径 |
|------|----------|
| 搜索 skills | `~/.openclaw/skills/<搜索skill名>/SKILL.md` |
| 创建 skill | `~/.npm-global/lib/node_modules/openclaw/skills/skill-creator/SKILL.md` |
| 安全审计 | `~/.openclaw/skills/<审计skill名>/SKILL.md` |

**好处：** 被引用 skill 更新时，自动获得最新版本。

---

## ⚠️ 安全与隐私须知

**在技能生成、整理和上传过程中，严禁包含以下个人隐私内容：**

- ❌ 验证码 / Verification codes
- ❌ 个人账号信息 / Personal account information
- ❌ 联系人代码 / Contact codes
- ❌ 机器型号 / Machine models
- ❌ 其他敏感个人信息 / Other sensitive personal information

**违反此原则可能导致隐私泄露！**
