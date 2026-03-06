---
name: hackernews-cn
description: "Hacker News 热门监控 | Hacker News Hot Stories. 获取 HN 热门文章、技术讨论、创业动态 | Get HN top stories, tech discussions, startup news. 触发词：Hacker News、HN、YC、创业."
metadata:
  openclaw:
    emoji: "🄪"
    category: "tech"
    tags: ["hackernews", "hn", "tech", "startup", "yc"]
    requires:
      bins: ["python3", "curl"]
---

# Hacker News 热门监控

Hacker News 热门文章监控，支持评论分析、趋势追踪。

## 功能

### 热门文章
- **Top Stories** - 当前最热门文章
- **New Stories** - 最新发布文章
- **Best Stories** - 历史最佳文章
- **Ask HN** - 问答讨论

### 分类内容
- **Show HN** - 项目展示
- **Jobs** - 招聘信息
- **Launch** - 产品发布

### 数据分析
- **热度趋势** - 文章热度变化
- **评论分析** - 高赞评论摘要
- **关键词监控** - 追踪特定话题

## 使用方式

### 获取热门文章

```
获取 Hacker News Top 10
```

返回：
```json
[
  {"rank": 1, "title": "AI Agents Are Getting Scary Good", "points": 892, "comments": 456, "url": "https://..."},
  {"rank": 2, "title": "Show HN: I Built a Markdown Editor", "points": 654, "comments": 234, "url": "https://..."},
  {"rank": 3, "title": "The State of Rust 2026", "points": 543, "comments": 189, "url": "https://..."}
]
```

### 按类型筛选

```
获取 Hacker News Show HN 项目
```

### 关键词搜索

```
在 Hacker News 搜索 "AI agent"
```

## 数据来源

- Hacker News Official API
- Algolia HN Search API

## 输出格式

### 文章列表
```
🄪 Hacker News Top 10

1. AI Agents Are Getting Scary Good
   👍 892 points | 💬 456 comments
   https://...

2. Show HN: I Built a Markdown Editor
   👍 654 points | 💬 234 comments
   https://...
```

---

*Hacker News，技术圈的风向标* 🄪
