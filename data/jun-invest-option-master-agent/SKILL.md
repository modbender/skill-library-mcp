---
name: jun-invest-option-master-agent
description: "OpenClaw Agent App Installer: install/upgrade & register the jun-invest-option-master-agent isolated agent workspace. Includes auto backup/versioning to ClawHub."
---

# jun-invest-option-master-agent — Agent App (Installer + Backup)

这是一个 OpenClaw **独立 agent（isolated workspace）** 的安装器 + 自动备份发布闭环。

## 约定（第一性原则）

- **运行环境（唯一真源）**：`/Users/lijunsheng/.openclaw/workspace-jun-invest-option-master-agent`
- **发布工件（用于发布到 ClawHub 的 skill 资产）**：本 skill 目录下的 `agent/`
- **skills 依赖**：安装在 OpenClaw 全局 skills 目录；不锁版本，始终 best-effort 拉最新。
- **提交/发布不打扰你**：Growth 负责 commit；commit 自动同步到发布工件；后台任务定时发布到 ClawHub。

## 使用（对话入口）

对我说：
- **“安装/升级 jun-invest-option-master-agent（不绑定channel）”**

## 命令行（可选）

```bash
bash scripts/auto-install.sh
```

它会：
1) `clawhub update jun-invest-option-master-agent --force`
2) 首次创建运行环境（若不存在）
3) 在运行环境启用本地 git + 安装 post-commit hook（commit 触发同步）
4) 安装/加载 macOS launchd 定时发布任务（每天一次 + 轮询重大更新标记）
5) `openclaw agents add jun-invest-option-master-agent ...`

## 重大更新立刻发布（Growth 用）

在运行环境创建空文件：

- `~/.openclaw/workspace-jun-invest-option-master-agent/.publish-now`

后台轮询会自动发布并清除标记。
