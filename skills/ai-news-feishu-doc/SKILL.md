---
name: ai-news-digest
description: 飞书AI情报
---

# AI News Digest - AI 早报生成器

自动生成 AI 行业早报，支持 RSS 订阅、智能摘要、多语言分类。

## 快速开始

```bash
# 生成今日早报
cd scripts
python generate-ai-news.py

# 或
python3 generate-ai-news.py

# 输出文件：AI早报_2026年2月28日.md
```

## 功能特性

- ✅ **RSS 订阅** - 自动抓取配置源的最新文章
- ✅ **智能摘要** - 提取文章要点，生成摘要
- ✅ **关键词过滤** - 按关键词匹配优先级排序
- ✅ **多语言分类** - 自动区分中文/英文内容
- ✅ **媒体预览** - 提取文章配图
- ✅ **Markdown 输出** - 结构化早报文档

## 配置说明

配置文件：`assets/ai-news-rss.yaml`

```yaml
feeds:
  - name: "36氪"
    url: "https://www.36kr.com/feed"
    category: "国内AI"
    language: "zh"

filters:
  keywords:
    - "GPT"
    - "Claude"
    - "AI"
    - "大模型"
    - "OpenAI"

output:
  max_articles_per_feed: 5
  total_max_articles: 15
```

## 自定义配置

1. **添加 RSS 源**：在 `feeds` 列表中添加新的源
2. **调整关键词**：修改 `filters.keywords` 匹配感兴趣的内容
3. **输出格式**：调整 `output` 参数控制文章数量

## 定时任务

添加到 OpenClaw cron 实现每日自动推送：

```json
{
  "name": "ai-morning-news",
  "schedule": "0 8 * * *",
  "command": "python skills/ai-news-digest/scripts/generate-ai-news.py"
}
```

## 输出示例

```markdown
# 📰 AI 早报 | 2026年2月28日

## 🔥 头版头条
### OpenAI 获得 1100 亿美元新投资...

## 🇨🇳 国内 AI 动态
...

## 🌍 海外 AI 动态
...
```

## 依赖

- Python 3.7+
- PyYAML: `pip install pyyaml`

---

🦞 Powered by OpenClaw | v1.0.0
