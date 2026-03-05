---
name: video-understanding
version: 1.0.0
description: 视频理解与分析能力 - 让 AI 能够理解视频内容、提取关键信息。当用户要求分析视频、理解视频内容、总结视频、提取视频要点时触发此技能。
---

# Video Understanding - 视频理解技能

## 概述

赋予 AI 理解和分析视频内容的能力，支持：
- 视频链接分析（YouTube、Bilibili等）
- 提取视频标题、描述、时长等信息
- 视频内容总结与关键点提取
- 语音转文字（需要额外工具）

## 触发场景

1. 用户发送视频链接并要求"理解"、"分析"、"总结"
2. 用户询问视频"讲了什么"、"重点是什么"
3. 用户要求"提取"视频内容
4. 需要从视频中获取信息

## 支持平台

| 平台 | 网址 | 支持情况 |
|------|------|----------|
| YouTube | youtube.com | 标题、描述、时长 |
| Bilibili | bilibili.com | 标题、简介、BV号 |
| 抖音 | douyin.com | 标题、描述 |
| 腾讯视频 | v.qq.com | 标题、简介 |
| 爱奇艺 | iq.com | 标题、简介 |

## 获取视频信息

### 方法1: web_fetch
```python
url = "https://www.youtube.com/watch?v=视频ID"
# 提取 title, description, duration
```

### 方法2: 第三方 API
- RapidAPI Video APIs
- YouTube Data API
- Bilibili API

## 工作流

```
1. 识别视频平台 → 判断使用哪个 API/方法
2. 获取基本信息 → 标题、描述、时长、作者
3. 提取关键内容 → 章节、要点、字幕（如有）
4. 整合总结 → 用中文呈现给用户
```

## 输出格式

向用户呈现视频信息时：
- 视频标题和来源
- 内容摘要（如果可以获取）
- 关键时间点（如有章节）
- 建议的观看重点

## 限制

- 无法直接播放视频
- 无法理解视频画面内容
- 需要平台支持或第三方 API
