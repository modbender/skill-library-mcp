---
name: huxiu
description: 获取虎嗅网文章和24小时资讯。用于当用户想查看虎嗅网热点文章或24小时模块内容。支持的场景：(1) 查看虎嗅网首页热点 (2) 获取24小时模块资讯 (3) 获取特定文章详细内容
metadata:
  openclaw:
    emoji: "🐯"
---

# 虎嗅网 Skill

获取虎嗅网（huxiu.com）的文章内容和24小时资讯。

## 使用方法

### 1. 获取首页热点

访问虎嗅网首页，提取热文标题和链接：

```
https://www.huxiu.com
```

### 2. 获取24小时模块资讯

访问24小时聚合页面：

```
https://www.huxiu.com/moment/
```

获取单条24小时资讯详情（URL格式：https://www.huxiu.com/moment/XXX.html）：

```
web_fetch(url: "资讯链接", maxChars: 5000)
```

### 3. 获取文章详情

用户提供文章链接时，使用 `web_fetch` 获取文章正文：

```
web_fetch(url: "文章链接", maxChars: 8000)
```

文章链接格式：`https://www.huxiu.com/article/XXXXXX.html`

## 输出格式

提取内容后，以清晰的方式呈现：
- 标题
- 来源/作者
- 发布时间
- 内容摘要

## 注意事项

- 虎嗅网24小时模块是快速资讯聚合，包含各类即时热点
- 头条新闻通常带有"持续更新"标记
- 多个热点以列表形式呈现
