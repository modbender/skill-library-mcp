# Content Ops - MCP 配套技能

## 已集成的 MCP 服务

### 1. 小红书抓取 (xiaohongshu-mcp)
- **包名**: `xiaohongshu-mcp-steve`
- **功能**: 搜索笔记、获取评论、搜索+评论
- **配置**: 需要 `XIAOHONGSHU_COOKIE` 环境变量
- **使用**:
  ```bash
  XIAOHONGSHU_COOKIE="your_cookie" mcporter call xiaohongshu-mcp.search_notes keyword="AI" sort="popularity_descending"
  ```
- **文档**: `node_modules/xiaohongshu-mcp-steve/README.md`

### 2. Reddit 发布/抓取 (reddit-mcp)
- **包名**: `reddit-mcp`
- **功能**: 浏览帖子、搜索内容、分析用户
- **配置**: 需要 `REDDIT_CLIENT_ID` 和 `REDDIT_CLIENT_SECRET` 环境变量
- **获取凭据**:
  1. 访问 https://www.reddit.com/prefs/apps
  2. 创建应用，获取 Client ID 和 Secret
- **使用**:
  ```bash
  REDDIT_CLIENT_ID="xxx" REDDIT_CLIENT_SECRET="xxx" mcporter call reddit.search query="AI tools"
  ```

### 3. 社交媒体引擎 (social-media-mcp-server)
- **包名**: `@muhammadhamidraza/social-media-mcp-server`
- **功能**: 多平台社交媒体管理（YouTube, LinkedIn, Facebook, Instagram, TikTok, Twitter/X）
- **配置**: 需要各平台的 API 凭据
- **状态**: 待配置

## MCP 配置位置

全局配置: `/home/admin/.openclaw/workspace/config/mcporter.json`

```json
{
  "mcpServers": {
    "xiaohongshu-mcp": {
      "command": "npx xiaohongshu-mcp-steve"
    },
    "reddit": {
      "command": "npx -y reddit-mcp"
    },
    "social-media": {
      "command": "npx -y @muhammadhamidraza/social-media-mcp-server"
    }
  }
}
```

## 使用流程

### 内容抓取流程
```
1. 设置小红书 Cookie
2. mcporter call xiaohongshu-mcp.search_notes keyword="AI"
3. 审核内容存入 crawl_results
4. 生成发布任务到 publish_tasks
```

### 内容发布流程
```
1. 从 crawl_results 选择已审核内容
2. 生成发布任务（reddit/social-media）
3. 配置 Reddit/Social Media API 凭据
4. mcporter call reddit.create_post ...
5. 记录到 publish_metrics_daily
```

## 待办

- [ ] 配置小红书 Cookie
- [ ] 配置 Reddit API 凭据
- [ ] 测试端到端抓取-发布流程
