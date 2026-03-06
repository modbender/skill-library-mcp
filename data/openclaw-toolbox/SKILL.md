---
name: "openclaw-toolbox"
description: "Integrated OpenClaw management suite for environment initialization, maintenance, and multi-mode backup (Full/Skills)."
author: "Wilsonsliu95 (https://github.com/WilsonLiu95)"
---

# OpenClaw Toolbox

OpenClaw 综合管理工具箱，集成环境初始化、系统维护及多模式备份功能。

## Quick Start

### 1. 环境初始化 (Setup)
```bash
# 适合新设备首次部署或环境修复
"~/.openclaw/workspace/skills/openclaw-toolbox/scripts/setup.sh"
```

### 2. 系统备份 (Backup)
```bash
# 备份整个 OpenClaw 仓库（系统配置、人设、记忆等）
"~/.openclaw/workspace/skills/openclaw-toolbox/scripts/backup-now.sh" --full "定期备份"

# 备份 Skills 开发仓库
"~/.openclaw/workspace/skills/openclaw-toolbox/scripts/backup-now.sh" --skills "更新技能库"

# 备份并升级（先拉取再备份）
"~/.openclaw/workspace/skills/openclaw-toolbox/scripts/backup-now.sh" --pull
```

## 常用命令与参数

### Setup 脚本参数
- `--update`: 拉取最新仓库（工作区干净时）
- `--verify-only`: 仅验证安装状态
- `--reset-env`: 重新生成 `.env`（自动备份旧文件）
- `--skip-node` / `--skip-packages` / `--skip-env` / `--skip-mcp`

### Backup 脚本参数
- `--full`: 备份整个 OpenClaw 仓库 (默认)
- `--skills`: 备份 `workspace/projects/openclaw-skills` 仓库
- `--pull`: 备份前先执行 `git pull --rebase` (升级同步)
- `--no-push`: 只提交，不推送
- `--dry-run`: 仅显示变更预览
- `-m, --message`: 自定义提交信息

## 环境要求

- 已设置 `OPENCLAW_SKILLS_GITHUB_URL` 环境变量（用于 Skills 备份）
- 已安装 Git 且配置好 GitHub 访问权限（SSH 或 PAT）

## 运行逻辑

- **Setup**: 自动化配置 Node.js、安装核心 CLI、生成配置文件模板并验证环境。
- **Backup**: 智能识别仓库类型，处理 Git 暂存、提交及远程推送。

---
*🦐 虾宝宝工具箱 —— 守护刘家 AI 环境*
