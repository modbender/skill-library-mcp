---
name: clawdog-backup
version: 1.0.0
description: 狗蛋备份恢复技能。备份 OpenClaw 核心文件（SOUL.md, AGENTS.md, IDENTITY.md, USER.md, TOOLS.md）和记忆层（memory/）到 OneDrive，支持实时监控备份和定时备份，可从云端恢复。
---

# ClawDog Backup
Version: 1.0.1

**狗蛋备份恢复技能** — 备份和恢复 OpenClaw 的核心文件和记忆到 OneDrive。

## 功能

- **核心层备份**：实时监控 `SOUL.md`, `AGENTS.md`, `IDENTITY.md`, `USER.md`, `TOOLS.md`，文件修改时自动备份
- **记忆层备份**：每周定时备份 `memory/` 目录
- **云端同步**：备份自动同步到 OneDrive `/备份/OpenClaw/`
- **恢复功能**：从 OneDrive 恢复备份到指定目录

## 备份内容

| 类型 | 内容 | 触发方式 |
|------|------|----------|
| 核心层 | SOUL.md, AGENTS.md, IDENTITY.md, USER.md, TOOLS.md | 文件修改实时触发 |
| 记忆层 | memory/ | 每周日 UTC 23:00 |

## 使用方法

### 备份

核心层文件修改后自动备份（需要启动 inotify 监控）：
```bash
# 启动核心层监控（后台运行）
nohup /root/.openclaw/workspace/skills/clawdog-backup/scripts/backup-core.sh > /root/.openclaw/backup/inotify.log 2>&1 &
```

手动触发记忆层备份：
```bash
/root/.openclaw/workspace/skills/clawdog-backup/scripts/backup-memory.sh
```

### 恢复（从 OneDrive）

```bash
# 测试恢复（不覆盖）
/root/.openclaw/workspace/skills/clawdog-backup/scripts/restore.sh --all --dry-run

# 恢复核心层到工作区
/root/.openclaw/workspace/skills/clawdog-backup/scripts/restore.sh --core

# 恢复所有到工作区
/root/.openclaw/workspace/skills/clawdog-backup/scripts/restore.sh --all
```

### 恢复（从本地文件 - 新机器）

新机器无需 rclone，直接用备份文件恢复：

```bash
# 从本地文件夹恢复所有
./restore.sh --source /path/to/backup-files --all

# 从本地文件恢复核心层到指定目录
./restore.sh --source ./backup-files --core --target /tmp/restore
```

### 选项

| 选项 | 说明 |
|------|------|
| `--source PATH` | 本地备份文件夹（不指定则从 OneDrive 恢复） |
| `--core` | 只恢复核心层 |
| `--memory` | 只恢复记忆层 |
| `--all` | 恢复所有（默认） |
| `--date DATE` | 指定日期 (YYYYMMDD) |
| `--target DIR` | 目标目录（默认: workspace） |
| `--dry-run` | 测试模式，不实际恢复 |

## OneDrive 位置

- 路径：`OneDrive:/备份/OpenClaw/`
- 文件：
  - `goudan-core-YYYYMMDD-HHMMSS.tar.gz`
  - `goudan-memory-YYYYMMDD.tar.gz`

## 定时任务

记忆层备份已配置为每周日 UTC 23:00 执行（通过 OpenClaw cron）。

## 日志

- 核心层备份日志：`/root/.openclaw/backup/core-backup.log`
- 记忆层备份日志：`/root/.openclaw/backup/memory-backup.log`
- 恢复日志：`/root/.openclaw/backup/restore.log`
- inotify 监控日志：`/root/.openclaw/backup/inotify.log`

## 依赖

- rclone（已配置 OneDrive）
- inotify-tools（核心层实时监控）
- tar

## 注意事项

- 首次使用需要配置 rclone 和 OneDrive
- 核心层监控需要后台运行
- 恢复时默认不覆盖已存在的文件（用 `cp -n`）
