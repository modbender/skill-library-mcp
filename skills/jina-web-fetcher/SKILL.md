---
name: jina-web-fetcher
description: 使用 Jina AI 抓取网页内容，绕过搜索引擎限制。支持任意URL，支持 Google 搜索结果抓取。
---

# Jina Web Fetcher

使用 Jina AI 服务抓取网页内容。

## 安装
无需安装，直接使用 curl。

## 使用
```bash
# 抓取任意网页
curl -s "https://r.jina.ai/http://目标URL"

# 抓取 Google 搜索结果
curl -s "https://r.jina.ai/http://www.google.com/search?q=搜索词"
```

## 示例
```bash
# 抓取 GitHub Trending
curl -s "https://r.jina.ai/http://github.com/trending"

# 抓取 Hacker News
curl -s "https://r.jina.ai/http://news.ycombinator.com"

# 抓取特定文章
curl -s "https://r.jina.ai/http://example.com/article"
```

## 注意
- Google 被封锁时使用 r.jina.ai 仍可能被拦截
- 大部分网站都可以正常抓取
