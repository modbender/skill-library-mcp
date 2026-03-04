---
name: openclaw-config-backuper
description: "Backup OpenClaw config files, Skills, Workspace files, and Memory records for migration or disaster recovery. 备份 OpenClaw 配置文件、技能、工作区文件和记忆记录，用于迁移或灾难恢复。Triggers: 备份, backup, 备份配置, backup config, 配置备份, config backup, 备份OpenClaw, backup openclaw, 迁移配置, migrate config, 恢复配置, restore config, 导出配置, export config, 配置迁移, config migration, 灾难恢复, disaster recovery, 备份技能, backup skills, 备份工作区, backup workspace, 备份记忆, backup memory, OpenClaw备份, openclaw backup, 配置导出, config export, 系统备份, system backup, 配置文件备份, config files backup."
---

# OpenClaw Config Backuper | OpenClaw 配置备份

Backup all OpenClaw configurations for migration or disaster recovery. 备份所有 OpenClaw 配置，用于迁移或灾难恢复。

## Usage | 使用方法

Run `~/.openclaw/skills/openclaw-config-backuper/scripts/backup.sh` to create a timestamped backup folder. 运行 `~/.openclaw/skills/openclaw-config-backuper/scripts/backup.sh` 创建带时间戳的备份文件夹。

## Backup Contents | 备份内容

| Source | Target |
|--------|--------|
| `~/.openclaw/*.json` | `config/` |
| `~/.openclaw/skills/*` | `skills/` |
| `~/.openclaw/workspace/*.md` | `workspace/` |
| `~/.openclaw/workspace/memory/*` | `memory/` |

## Backup Location | 备份位置

`~/.openclaw/workspace/backup/YYYYMMDD_HHMMSS/`

## Workflow | 工作流程

1. Create backup directory with timestamp. 创建带时间戳的备份目录。
2. Copy JSON configs (openclaw.json, exec-approvals.json, etc.). 复制 JSON 配置文件。
3. Copy all local Skills from `~/.openclaw/skills/`. 复制所有本地技能。
4. Copy workspace MD files (AGENTS.md, MEMORY.md, etc.). 复制工作区 MD 文件。
5. Copy memory logs. 复制记忆日志。
6. Report file count and location. 报告文件数量和位置。
7. If more than 5 backups exist, delete the oldest one. 若存在超过 5 个备份，则删除最早的一个。

## Notes | 注意事项

- Does NOT backup built-in skills (only `~/.openclaw/skills/`). 不备份内置技能（仅备份 `~/.openclaw/skills/`）。
- Does NOT create compressed archive. 不创建压缩包。
