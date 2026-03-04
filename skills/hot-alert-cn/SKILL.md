---
name: hot-alert-cn
description: "热点提醒器 | Hot Topics Alert System. 监控关键词上热搜，自动提醒 | Monitor keywords trending, auto alert when topic hits hot list. 触发词：热点提醒、热搜监控、关键词监控."
metadata:
  openclaw:
    emoji: "🔔"
    category: "monitor"
    tags: ["alert", "monitor", "hot", "keyword", "china"]
    requires:
      bins: ["python3"]
---

# 热点提醒器

监控关键词上热搜，自动提醒用户。

## 功能

### 关键词监控
- **添加关键词** - 添加要监控的关键词
- **多平台监控** - 微博/知乎/百度等
- **实时检测** - 定期检查热搜榜

### 提醒方式
- **消息提醒** - 发送提醒消息
- **热度报告** - 包含热度数值
- **平台标识** - 显示在哪个平台

## 使用方式

### 添加监控关键词

```
监控 "AI" 上热搜，提醒我
```

### 查看监控列表

```
查看我监控的关键词
```

### 删除监控

```
取消监控 "AI"
```

## 输出格式

### 提醒消息
```
🔔 热点提醒！

关键词 "AI" 已登上热搜：

📱 微博热搜 #3
热度：876.5万

📱 知乎热榜 #1
热度：876.5万

建议：现在可以发相关内容获取流量！
```

---

*不错过任何热点机会* 🔔
