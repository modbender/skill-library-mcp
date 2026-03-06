---
name: AI新闻日报
description: 每日自动抓取国内AI领域重要新闻，智能过滤非AI内容，生成简洁摘要。
---

# AI新闻日报

每日自动抓取国内AI领域重要新闻，智能过滤非AI内容，生成简洁摘要。

## 功能

- **多源聚合**：从量子位、机器之心、InfoQ、36氪、雷锋网、钛媒体、新智元等科技媒体抓取
- **智能过滤**：只保留核心AI新闻，过滤综合早报、娱乐八卦等非相关内容
- **正文摘要**：抓取文章正文生成真实摘要，非RSS摘要
- **重要性排序**：按AI相关度评分，精选Top 10

## 安装

```bash
clawhub install ai-news-daily
```

## 使用

### 手动运行

```bash
# 抓取今日AI新闻
openclaw skills run ai-news-daily
```

### 设置定时任务

```bash
# 每天早上9点自动推送
openclaw skills cron ai-news-daily --schedule "0 9 * * *"
```

## 配置

在 `config.yaml` 中可配置：

```yaml
sources:
  - qbitai      # 量子位
  - jiqizhixin  # 机器之心
  - infoq       # InfoQ
  - 36kr        # 36氪
  - leiphone    # 雷锋网
  - tmtpost     # 钛媒体
  - aiera       # 新智元

max_news: 10
summary_length: 250
```

## 输出格式

Markdown格式，包含标题、来源、摘要（200-300字）、原文链接。

## 依赖

- Python 3.8+
- feedparser
- beautifulsoup4
- requests

## License

MIT
