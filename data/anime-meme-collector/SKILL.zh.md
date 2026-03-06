---
name: anime-meme-collector
description: 每日自动收集和管理中文互联网的动漫/ACG梗和流行语。自动从Bilibili等平台获取数据，构建梗数据库以增强AI对宅文化的理解。当用户希望了解动漫社区趋势或提升AI的动漫/梗知识时使用。
---

# 动漫梗收集器 (Anime Meme Collector)

中文互联网平台动漫/ACG梗的自动每日收集。

## 概述

维护最新数据库，包含：
- Bilibili热门视频梗
- Bilibili热搜关键词
- Galgame术语（柚子社、Key、型月等）
- 主播/游戏文化（电棍、山泥若、炫狗等）
- 346+ 精选梗

## 快速开始

### 手动收集

```bash
python scripts/collect_memes.py
```

### 自动每日更新

设置定时任务在午夜运行（北京时间）：

```bash
0 0 * * * cd /path/to/skill && python scripts/collect_memes.py
```

或使用 OpenClaw cron：
```json
{
  "action": "add",
  "job": {
    "name": "daily-anime-meme-collect",
    "schedule": { "kind": "cron", "expr": "0 0 * * *", "tz": "Asia/Shanghai" },
    "payload": {
      "kind": "systemEvent",
      "command": "python scripts/collect_memes.py"
    }
  }
}
```

## 使用数据库

在动漫/梗语境下回复时：
1. 查看 `references/anime_memes_db.json` 了解最新趋势
2. 参考 `references/anime_memes_manual.md` 获取经典梗
3. 自然地将梗融入回复

## 数据来源

- **Bilibili API**: 热门视频和热搜
- **人工整理**: 经典和 timeless 梗
- **Galgame术语**: 柚子社、Key、型月等
- **主播文化**: 电棍、山泥若、炫狗等

## 参考文件

- [anime_memes_db.json](references/anime_memes_db.json) - 自动生成数据库（300+条目）
- [anime_memes_manual.md](references/anime_memes_manual.md) - 精选经典梗

## 注意事项

- 脚本遵守速率限制并包含超时
- 失败的请求会被记录但不会停止收集
- 数据库限制为300条目以防止膨胀
- 每个条目包含来源追踪
