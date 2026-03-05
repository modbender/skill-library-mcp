# xiaohongshu-mcp 使用指南

## 前置条件

- MCP 服务运行在 `http://localhost:18060/mcp`
- 已完成小红书登录（cookies.json 存在）

## 可用工具 (13个)

### 账号管理

| 工具 | 说明 |
|------|------|
| `check_login_status` | 检查登录状态 |
| `get_login_qrcode` | 获取登录二维码（Base64 图片 + 超时时间） |
| `delete_cookies` | 删除 cookies 重置登录状态 |

### 内容浏览

| 工具 | 说明 |
|------|------|
| `list_feeds` | 获取首页推荐 Feeds |
| `search_feeds` | 搜索小红书内容 |
| `get_feed_detail` | 获取笔记详情（内容、图片、互动数据、评论） |
| `user_profile` | 获取用户主页（基本信息、关注/粉丝、笔记列表） |

### 内容发布

| 工具 | 说明 |
|------|------|
| `publish_content` | 发布图文内容 |
| `publish_with_video` | 发布视频内容（仅支持本地文件） |

### 互动操作

| 工具 | 说明 |
|------|------|
| `post_comment_to_feed` | 发表评论 |
| `reply_comment_in_feed` | 回复评论 |
| `like_feed` | 点赞/取消点赞 |
| `favorite_feed` | 收藏/取消收藏 |

## 常用工作流

### 1. 搜索并获取笔记详情

```
1. search_feeds(keyword="xxx") → 获取搜索结果列表
2. 从结果中提取 note_id 和 xsec_token
3. get_feed_detail(note_id, xsec_token) → 获取完整详情
```

### 2. 发布图文笔记

```
publish_content(
  title="标题（≤20字）",
  content="正文（≤1000字）",
  images=["/path/to/img1.jpg", "/path/to/img2.jpg"]
)
```

图片支持：
- 本地绝对路径（推荐）
- HTTP/HTTPS URL

### 3. 发布视频笔记

```
publish_with_video(
  title="标题（≤20字）",
  content="正文（≤1000字）",
  video="/path/to/video.mp4"
)
```

仅支持本地视频文件，建议 <1GB。

### 4. 批量互动

```
1. list_feeds() 或 search_feeds() 获取笔记列表
2. 遍历结果调用 like_feed / favorite_feed / post_comment_to_feed
```

## 重要参数说明

### xsec_token

- 多数操作需要 `xsec_token` 参数
- 从 `list_feeds` 或 `search_feeds` 返回结果中获取
- 与 `note_id` 配对使用

### note_id

- 笔记唯一标识
- 从搜索/推荐结果中获取

## 运营知识

- **标题**：≤20字（硬限制）
- **正文**：≤1000字（硬限制）
- **每日发帖**：≤50篇
- **图文优于视频**：推荐角度图文流量更好
- **Tags**：添加合适标签增加曝光
- **违禁词**：使用前检查内容是否含违禁词
- **禁止行为**：引流、纯搬运会被打击

## 错误排查

| 问题 | 解决 |
|------|------|
| 登录失效 | 运行 `xiaohongshu-login-*` 重新登录 |
| 无法发布 | 检查标题/正文长度限制 |
| 找不到笔记 | 确认 note_id 和 xsec_token 配对正确 |
| 服务不响应 | `tail -f mcp.log` 查看日志 |
