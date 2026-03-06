---
name: webdav-backup
version: 1.0.2
description: WebDAV 备份工具 - 将 OpenClaw 工作目录备份到 WebDAV 服务器（如坚果云、Nextcloud、阿里云盘等）。当用户需要备份数据、同步文件到云端、或配置自动备份计划时使用此技能。
metadata:
  webdav-backup:
    requires:
      env: [WEBDAV_URL, WEBDAV_USERNAME, WEBDAV_PASSWORD]
---

# WebDAV 备份工具

将 OpenClaw 工作目录备份到 WebDAV 服务器。

## 支持的 WebDAV 服务

- 坚果云 (jianguoyun.com)
- Nextcloud / ownCloud
- 阿里云盘（需 WebDAV 插件）
- 其他标准 WebDAV 服务

## 配置

首次使用前需要配置 WebDAV 连接信息。

### 方式一：openclaw.json（推荐）

编辑 `~/.openclaw/openclaw.json`，在 `skills.entries` 中添加：

```json
{
  "skills": {
    "entries": {
      "webdav-backup": {
        "enabled": true,
        "env": {
          "WEBDAV_URL": "https://dav.jianguoyun.com/dav/",
          "WEBDAV_USERNAME": "your-email@example.com",
          "WEBDAV_PASSWORD": "your-password"
        }
      }
    }
  }
}
```

### 方式二：环境变量

```bash
# 设置环境变量
export WEBDAV_URL="https://dav.jianguoyun.com/dav/"
export WEBDAV_USERNAME="your-email@example.com"
export WEBDAV_PASSWORD="your-password"

# 持久化到 ~/.bashrc
echo 'export WEBDAV_URL="https://dav.jianguoyun.com/dav/"' >> ~/.bashrc
echo 'export WEBDAV_USERNAME="your-email"' >> ~/.bashrc
echo 'export WEBDAV_PASSWORD="your-password"' >> ~/.bashrc
source ~/.bashrc
```

> **优先级**: 环境变量 > openclaw.json 配置

## 使用方法

### 手动备份

```bash
# 备份整个工作目录（自动检测路径）
python3 ~/.openclaw/workspace/skills/openclaw-webdav-backup/scripts/backup.py

# 备份指定目录
python3 ~/.openclaw/workspace/skills/openclaw-webdav-backup/scripts/backup.py --source /path/to/data

# 指定备份文件名
python3 ~/.openclaw/workspace/skills/openclaw-webdav-backup/scripts/backup.py --name my-backup-2025
```

### 自动备份

使用 cron 设置定时备份：

```bash
# 每天凌晨2点备份（注意：使用绝对路径）
cron add --schedule "0 2 * * *" --command "python3 ~/.openclaw/workspace/skills/openclaw-webdav-backup/scripts/backup.py"
```

### 查看备份列表

```bash
python3 ~/.openclaw/workspace/skills/openclaw-webdav-backup/scripts/backup.py --list
```

### 恢复备份

```bash
python3 ~/.openclaw/workspace/skills/openclaw-webdav-backup/scripts/backup.py --restore latest
```

## 默认备份内容

- `memory/` - 每日记忆文件
- `MEMORY.md` - 长期记忆
- `USER.md` - 用户信息
- `TOOLS.md` - 工具配置
- `media/` - 媒体文件（可选）

## 备份文件格式

备份文件以 tar.gz 压缩包形式存储，命名格式：
```
openclaw-backup-YYYYMMDD-HHMMSS.tar.gz
```

## 故障排除

详见 [references/config.md](references/config.md)
