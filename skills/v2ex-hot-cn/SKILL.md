---
name: v2ex-hot-cn
description: "V2EX 热门话题监控 | V2EX Hot Topics Monitor. 获取 V2EX 热门帖子、技术讨论、数码生活 | Get V2EX trending posts, tech discussions, digital life. 触发词：V2EX、v2、程序员社区."
metadata:
  openclaw:
    emoji: "💬"
    category: "community"
    tags: ["v2ex", "community", "tech", "china", "programmer"]
    requires:
      bins: ["python3", "curl"]
---

# V2EX 热门话题监控

V2EX 热门话题监控，支持节点分类、用户讨论追踪。

## 功能

### 热门话题
- **今日热门** - 当前最热话题
- **最新主题** - 最新发布
- **全站精选** - 高质量帖子

### 节点分类
- **技术** - 编程、开发相关
- **创意** - 设计、产品
- **好玩** - 游戏、娱乐
- **Apple** - 苹果相关
- **酷工作** - 招聘、求职

### 互动追踪
- **热门回复** - 高赞评论
- **活跃用户** - 活跃发帖者

## 使用方式

### 获取热门话题

```
获取 V2EX 今日热门
```

返回：
```json
[
  {"id": 1, "title": "2026 年该学什么编程语言？", "node": "programmer", "replies": 234, "author": "dev123"},
  {"id": 2, "title": "MacBook Pro M4 值得买吗？", "node": "apple", "replies": 189, "author": "macfan"}
]
```

### 按节点筛选

```
获取 V2EX Apple 节点热门
```

## 输出格式

```
💬 V2EX 今日热门

1. 2026 年该学什么编程语言？
   📂 programmer | 💬 234 回复 | @dev123

2. MacBook Pro M4 值得买吗？
   📂 apple | 💬 189 回复 | @macfan
```

---

*V2EX，程序员的创意社区* 💬
