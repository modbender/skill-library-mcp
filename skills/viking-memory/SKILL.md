---
name: viking-memory
description: OpenViking 长期记忆系统。用于语义检索用户偏好、历史对话、重要信息等。当需要召回用户之前提到的信息、查找相关上下文时使用此 Skill。
---

# Viking Memory

基于 OpenViking 的向量化记忆系统，提供语义搜索能力。

## 功能

- **语义搜索** - 用自然语言描述搜索相关记忆
- **添加记忆** - 将重要信息存入长期记忆
- **读取内容** - 获取记忆的详细内容

## API 端点

- Base URL: `http://127.0.0.1:18790`
- 语义搜索: `POST /api/v1/search/find`
- 添加资源: `POST /api/v1/resources`
- 读取内容: `POST /api/v1/content/read`

## 使用场景

1. 用户提到之前讨论过的话题 → 搜索相关记忆
2. 用户询问之前保存的信息 → 召回记忆
3. 对话中识别到重要信息 → 自动保存

## 示例

### 搜索记忆
```bash
curl -s -X POST http://127.0.0.1:18790/api/v1/search/find \
  -H "Content-Type: application/json" \
  -d '{"query": "用户的工作习惯", "limit": 5}'
```

### 添加记忆
```bash
curl -s -X POST http://127.0.0.1:18790/api/v1/resources \
  -H "Content-Type: application/json" \
  -d '{"uri": "viking://user/memories/preferences/咖啡偏好", "content": "用户喜欢喝拿铁，不加糖"}'
```

### 读取记忆
```bash
curl -s -X POST http://127.0.0.1:18790/api/v1/content/read \
  -H "Content-Type: application/json" \
  -d '{"uri": "viking://user/memories/preferences/咖啡偏好"}'
```
