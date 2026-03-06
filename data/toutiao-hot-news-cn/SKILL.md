---
name: toutiao-hot-news-cn
description: "今日头条热榜 | Toutiao (China's Top News) Hot Topics. 获取中国最热门新闻资讯 | Get China's hottest news and trends. 包含时政、财经、科技、娱乐等多领域 | Covers politics, finance, tech, entertainment. 输出热点标题、热度值、链接 | Outputs hot titles, popularity scores, links. 触发词：头条、热榜、中国新闻、China news, trending."
---

# 今日头条新闻热榜

## 技能概述

此技能用于抓取今日头条 PC 端热榜（hot-board）数据，包括：
- 热点标题
- 热度值（HotValue）
- 详情跳转链接（去除冗余查询参数，便于分享）
- 封面图（如有）
- 标签（如“热门事件”等）

数据来源：今日头条 (www.toutiao.com)

## 获取热榜

获取热榜（默认 50 条，按榜单顺序返回）：

```bash
node scripts/toutiao.js hot
```

获取热榜前 N 条：

```bash
node scripts/toutiao.js hot 10
```

## 返回数据字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| rank | number | 榜单排名（从 1 开始） |
| title | string | 热点标题 |
| popularity | number | 热度值（HotValue，已转为数字；解析失败时为 0） |
| link | string | 热点详情链接（已清理 query/hash） |
| cover | string \| null | 封面图 URL（如有） |
| label | string \| null | 标签/标识（如有） |
| clusterId | string | 聚合 ID（字符串化） |
| categories | string[] | 兴趣分类（如有） |

## 注意事项

- 该接口为网页端公开接口，返回结构可能变动；若字段缺失可适当容错
- 访问频繁可能触发风控，脚本内置随机 User-Agent 与超时控制

## 作者介绍

- 爱海贼的无处不在
- 我的微信公众号：无处不在的技术
