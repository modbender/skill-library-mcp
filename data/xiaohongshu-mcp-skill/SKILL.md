---
name: xiaohongshu-mcp
description: Operate Xiaohongshu (小红书/RED) via local MCP service. Use when user wants to search notes, publish content (image/video), interact with posts (like/comment/favorite), or check account status on Xiaohongshu. Requires MCP service running at localhost:18060.
---

# xiaohongshu-mcp

小红书 MCP 服务操作。

## 快速开始

1. **检查服务状态**
   ```bash
   curl -s -X POST http://localhost:18060/mcp \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc":"2.0","method":"initialize","params":{},"id":1}'
   ```

2. **服务未运行时启动**
   ```bash
   cd /Users/handi7/Documents/agentic-coding-projects/projects/xiaohongshu-mcp
   nohup ./bin/xiaohongshu-mcp-darwin-arm64 > mcp.log 2>&1 &
   ```

## 可用工具

| 工具 | 说明 |
|------|------|
| `check_login_status` | 检查登录状态 |
| `get_login_qrcode` | 获取登录二维码 |
| `list_feeds` | 首页推荐 |
| `search_feeds` | 搜索内容 |
| `get_feed_detail` | 笔记详情 |
| `user_profile` | 用户主页 |
| `publish_content` | 发布图文 |
| `publish_with_video` | 发布视频 |
| `post_comment_to_feed` | 发表评论 |
| `reply_comment_in_feed` | 回复评论 |
| `like_feed` | 点赞 |
| `favorite_feed` | 收藏 |
| `delete_cookies` | 重置登录 |

## 内容限制

- 标题 ≤20 字
- 正文 ≤1000 字
- 每日 ≤50 篇
- 图文流量优于视频

## References

- **首次部署**: [references/deploy.md](references/deploy.md) — 下载、登录、启动服务
- **使用指南**: [references/usage.md](references/usage.md) — 工具详解、工作流、运营知识

## Credits

Based on [xpzouying/xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp) by [@xpzouying](https://github.com/xpzouying)
