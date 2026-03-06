---
name: douyin-hot-trend
description: 获取抖音热榜/热搜榜数据，包含热门视频、挑战赛、音乐等多领域热门内容，并输出标题、热度值与跳转链接。
---

# 抖音热榜

## 技能概述

此技能用于抓取抖音热榜数据，包括：
- 热点标题
- 热度值
- 详情跳转链接
- 热门标签

## 获取热榜

获取热榜（默认 50 条）：

```bash
node scripts/douyin.js hot
```

获取热榜前 N 条：

```bash
node scripts/douyin.js hot 10
```

## 使用示例

```bash
# 获取抖音热榜前 20 条
node scripts/douyin.js hot 20
```

## 数据来源

抖音网页端公开接口

## 注意事项

- 该接口为网页端公开接口，返回结构可能变动
- 访问频繁可能触发风控
