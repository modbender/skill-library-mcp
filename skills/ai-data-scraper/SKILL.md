---
name: SKILL.md
description: 自动化数据抓取和清洗服务。
---

# SKILL.md

# Data Scraping Service

自动化数据抓取和清洗服务。

## 能力

- Web 网页抓取
- API 数据提取
- 数据清洗和格式化
- 批量抓取任务
- 定时监控

## 使用方式

```bash
# 抓取网页数据
openclaw run scraper --url "https://example.com" --format "json"

# 抓取 API
openclaw run scraper --api "https://api.example.com/data" --output "data.json"

# 定时抓取
openclaw run scraper --cron "0 */6 * * *" --target "stocks"
```

## 收费模式

- **单次抓取:** $5-20
- **月度订阅:** $50-200
- **API 集成:** 按项目收费

## 特性

- ✅ 支持 HTML/JSON/XML
- ✅ 代理池支持
- ✅ 自动重试
- ✅ 数据去重
- ✅ 实时监控

## 开发者

OpenClaw AI Agent
License: MIT
Version: 1.0.0
