---
name: generate_news_article
description: Generate individual Markdown articles from SerpAPI Google search results with images
homepage:
metadata: {"clawdbot":{"emoji":"📰","requires":["serpapi"]}}
---

# Generate News Article

自动从 SerpAPI Google 搜索结果生成多篇独立的 Markdown 文章。

## 功能

1. 接收搜索关键词（默认：AI助手）
2. 调用 SerpAPI Google 搜索（默认获取 5 条结果）
3. 为每条结果生成独立的 Markdown 文件
4. 自动下载缩略图到 assets 目录
5. 以时间目录结构保存文章

## 使用

```bash
# 使用默认关键词 "AI助手"
generate.sh

# 指定关键词
generate.sh "AI大模型"

# 指定关键词和结果数量
generate.sh "ChatGPT" 10
```

## 输出结构

生成的文章保存在 agent 根目录的 output 文件夹中：

```
/Users/lihaijian/.openclaw/workspace-wechat-publisher/output/
└── 2026-02-22/
    ├── 文章标题1.md
    ├── 文章标题2.md
    ├── 文章标题3.md
    ├── 文章标题4.md
    ├── 文章标题5.md
    └── assets/
        ├── image1.jpg
        ├── image2.jpg
        └── ...
```

## 文章格式

每篇 Markdown 文件包含：

```markdown
---
title: 文章标题
cover: ./assets/image.jpg
---

# 文章标题

摘要内容...

[原文链接](https://example.com/article)
```

## 特性

- ✅ 每条搜索结果生成独立文件
- ✅ 文件名使用搜索标题（自动清理特殊字符）
- ✅ 自动下载缩略图
- ✅ 支持指定文章数量
- ✅ 按日期归档

## 依赖

- SerpAPI skill（必须已安装）
- SERPAPI_API_KEY 环境变量
- Python 3（用于 JSON 解析和图片下载）

## 注意事项

- 如果搜索结果没有缩略图，cover 字段会留空
- 文件名会自动清理特殊字符
- 文章按搜索结果的序号生成
- 搜索使用 Google 搜索引擎（不是 Google News）
