---
name: hot-topic-finder
description: "发现并追踪热点话题，自动去重，支持多平台热榜监控。Use when: (1) 寻找创作灵感或热点话题，(2) 检查话题是否已使用过，(3) 监控微博/知乎/抖音等平台热榜，(4) 需要话题推荐时。NOT for: 实时新闻追踪、舆情危机处理。"
metadata:
  {
    "openclaw":
      {
        "emoji": "🔥",
        "requires": { "bins": ["curl", "python3"] },
      },
  }
---

# Hot Topic Finder

自动发现热点话题，智能去重，追踪使用历史。

## 核心功能

1. **热点发现**：从多平台获取热门话题
2. **话题去重**：检查话题是否已使用，避免重复
3. **历史追踪**：记录话题使用日期和次数
4. **智能推荐**：根据热度 + 新鲜度推荐话题

## 使用场景

✅ **适合：**
- "帮我找个热点话题写文章"
- "今天有什么热门事件"
- "这个话题我之前写过吗"
- "推荐几个新鲜话题"

## 快速开始

```bash
# 查找热点话题
python3 {baseDir}/scripts/find_topics.py --count 10

# 检查话题是否已使用
python3 {baseDir}/scripts/check_topic.py "房价下跌趋势"

# 标记话题已使用
python3 {baseDir}/scripts/mark_topic.py "房价下跌趋势" --heat 560000

# 获取智能推荐
python3 {baseDir}/scripts/recommend.py --count 5

# 查看使用历史
python3 {baseDir}/scripts/topic_history.py --days 30
```

## 数据存储

话题历史存储在 SQLite 数据库：`~/.openclaw/data/topic_history.db`

## 去重规则

1. **24小时内**：同一话题只能使用 1 次
2. **7天内**：同一话题最多使用 2 次
3. **30天内**：同一话题最多使用 3 次