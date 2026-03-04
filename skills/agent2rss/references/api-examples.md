# Agent2RSS API 调用示例

本文档提供完整的 API 调用示例，包括请求格式和响应示例。

## 基础信息
- 默认服务器: `https://agent2rss.yaotutu.top:8765`
- API 基础路径: `/api`
- 内容类型: `application/json`
- 认证方式: `Authorization: Bearer <token>`

## 1. 创建频道
请求
```bash
curl -X POST https://agent2rss.yaotutu.top:8765/api/channels \
  -H "Content-Type: application/json" \
  -d '{"name":"技术博客","description":"分享技术文章和教程"}'
```
响应示例
```json
{
  "success": true,
  "channel": {
    "id": "8cf83b0d-f856-4f7c-bd1c-4f6ca0338ece",
    "name": "技术博客",
    "description": "分享技术文章和教程",
    "token": "ch_4fd9cdce724ffb8d6ec69187b5438ae2",
    "theme": "spring",
    "language": "zh-CN",
    "maxPosts": 100,
    "createdAt": "2026-02-05T10:30:00.000Z"
  },
  "rssUrl": "https://agent2rss.yaotutu.top:8765/channels/8cf83b0d-f856-4f7c-bd1c-4f6ca0338ece/rss.xml"
}
```

## 2. 推送内容到频道（JSON 方式）
最简参数
```bash
curl -X POST https://agent2rss.yaotutu.top:8765/api/channels/8cf83b0d-f856-4f7c-bd1c-4f6ca0338ece/posts \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ch_4fd9cdce724ffb8d6ec69187b5438ae2" \
  -d '{"content":"# 我的标题\n\n这是文章内容"}'
```
完整参数
```bash
curl -X POST https://agent2rss.yaotutu.top:8765/api/channels/8cf83b0d-f856-4f7c-bd1c-4f6ca0338ece/posts \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ch_4fd9cdce724ffb8d6ec69187b5438ae2" \
  -d '{"content":"# Agent2RSS 使用指南\n\n## 简介\n\nAgent2RSS 是一个将任意内容转换为 RSS Feed 的服务...","title":"如何使用 Agent2RSS","link":"https://example.com/article","contentType":"markdown","author":"Claude","tags":["教程","RSS","技术"],"idempotencyKey":"article-2024-01-01-001"}'
```
响应示例（新创建）
```json
{
  "success": true,
  "message": "Post created successfully in channel \"8cf83b0d-f856-4f7c-bd1c-4f6ca0338ece\"",
  "post": {
    "id": "post_1234567890",
    "title": "如何使用 Agent2RSS",
    "channel": "8cf83b0d-f856-4f7c-bd1c-4f6ca0338ece",
    "pubDate": "2026-02-05T15:30:00.000Z"
  },
  "isNew": true
}
```
响应示例（已存在 - 幂等性）
```json
{
  "success": true,
  "message": "Post already exists (idempotency key matched)",
  "post": {
    "id": "post_1234567890",
    "title": "如何使用 Agent2RSS",
    "channel": "8cf83b0d-f856-4f7c-bd1c-4f6ca0338ece",
    "pubDate": "2026-02-05T15:30:00.000Z"
  },
  "isNew": false
}
```

## 3. 推送内容到频道（文件上传方式）
```bash
curl -X POST https://agent2rss.yaotutu.top:8765/api/channels/8cf83b0d-f856-4f7c-bd1c-4f6ca0338ece/posts/upload \
  -H "Authorization: Bearer ch_4fd9cdce724ffb8d6ec69187b5438ae2" \
  -F "file=@article.md" \
  -F "title=自定义标题" \
  -F "tags=技术,教程" \
  -F "idempotencyKey=article-2024-01-01-001"
```
响应示例
```json
{
  "success": true,
  "message": "Post created successfully in channel \"8cf83b0d-f856-4f7c-bd1c-4f6ca0338ece\" from uploaded file \"article.md\"",
  "post": {
    "id": "post_1234567890",
    "title": "自定义标题",
    "channel": "8cf83b0d-f856-4f7c-bd1c-4f6ca0338ece",
    "pubDate": "2026-02-05T15:30:00.000Z"
  },
  "isNew": true
}
```

## 4. 获取频道列表
请求
```bash
curl -X GET https://agent2rss.yaotutu.top:8765/api/channels
```
响应示例
```json
{
  "success": true,
  "channels": [
    {
      "id": "default",
      "name": "AI Briefing",
      "description": "Daily news summaries powered by AI",
      "theme": "spring",
      "language": "zh-CN",
      "maxPosts": 100,
      "createdAt": "2026-02-05T10:00:00.000Z"
    },
    {
      "id": "8cf83b0d-f856-4f7c-bd1c-4f6ca0338ece",
      "name": "技术博客",
      "description": "分享技术文章和教程",
      "theme": "github",
      "language": "zh-CN",
      "maxPosts": 100,
      "createdAt": "2026-02-05T10:30:00.000Z"
    }
  ]
}
```

## 5. 获取单个频道信息
请求
```bash
curl -X GET https://agent2rss.yaotutu.top:8765/api/channels/8cf83b0d-f856-4f7c-bd1c-4f6ca0338ece
```
响应示例
```json
{
  "success": true,
  "channel": {
    "id": "8cf83b0d-f856-4f7c-bd1c-4f6ca0338ece",
    "name": "技术博客",
    "description": "分享技术文章和教程",
    "theme": "github",
    "language": "zh-CN",
    "maxPosts": 100,
    "createdAt": "2026-02-05T10:30:00.000Z",
    "updatedAt": "2026-02-05T15:30:00.000Z"
  },
  "rssUrl": "https://agent2rss.yaotutu.top:8765/channels/8cf83b0d-f856-4f7c-bd1c-4f6ca0338ece/rss.xml"
}
```

## 6. 更新频道名称/描述（需 Token）
```bash
curl -X PUT https://agent2rss.yaotutu.top:8765/api/channels/8cf83b0d-f856-4f7c-bd1c-4f6ca0338ece \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ch_4fd9cdce724ffb8d6ec69187b5438ae2" \
  -d '{"name":"新的频道名称","description":"更新后的频道描述"}'
```
响应示例
```json
{
  "success": true,
  "message": "Channel updated",
  "channel": {
    "id": "8cf83b0d-f856-4f7c-bd1c-4f6ca0338ece",
    "name": "新的频道名称",
    "description": "更新后的频道描述",
    "theme": "github",
    "language": "zh-CN",
    "maxPosts": 100,
    "createdAt": "2026-02-05T10:30:00.000Z",
    "updatedAt": "2026-02-05T15:45:00.000Z"
  }
}
```

## 7. 获取 RSS Feed
```bash
curl -X GET https://agent2rss.yaotutu.top:8765/channels/8cf83b0d-f856-4f7c-bd1c-4f6ca0338ece/rss.xml
```

## 错误响应示例
401 未授权
```json
{
  "success": false,
  "error": "Authorization header missing or invalid",
  "details": {
    "expected": "Authorization: Bearer <channel-token>",
    "help": "Provide the channel token (ch_xxx)"
  }
}
```

400 请求参数错误
```json
{
  "success": false,
  "error": "Missing required field: content",
  "details": {
    "field": "content",
    "issue": "Required field missing",
    "expected": { "content": "string (required)" }
  }
}
```

404 频道不存在
```json
{
  "success": false,
  "error": "Channel \"xxx\" not found",
  "details": {
    "channelId": "xxx",
    "help": "Use GET /api/channels to list all available channels"
  }
}
```

500 服务器错误
```json
{ "success": false, "error": "Internal server error" }
```

## 使用技巧
- **推荐文件上传**：`curl -X POST "https://agent2rss.yaotutu.top:8765/api/channels/default/posts/upload" -H "Authorization: Bearer ch_xxx" -F "file=@article.md" -F "idempotencyKey=article-001"`
- **幂等性**：优先使用文章 URL/文件名/内容哈希作为 `idempotencyKey`
- **健康检查**：`curl https://agent2rss.yaotutu.top:8765/health`
