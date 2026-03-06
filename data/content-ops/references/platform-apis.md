# Platform APIs Reference

## 小红书 (Xiaohongshu)

### 内容抓取

**方法**: 浏览器自动化 (Playwright/Selenium)

**搜索URL**: `https://www.xiaohongshu.com/search_result?keyword={keyword}`

**数据提取**:
- 笔记卡片选择器: `[class*="note-item"]`, `[class*="feeds-page"] a`
- 标题: `[class*="title"]`, `h1`
- 作者: `[class*="author"]`, `[class*="nickname"]`
- 点赞: `[class*="like"]`, `[class*="count"]`
- 内容: 需要进入详情页抓取

**详情页数据**:
- 正文: `[class*="desc"]`
- 图片: `[class*="swiper-slide"] img`
- 标签: `[class*="tag"]`
- 发布时间: `[class*="time"]`

**反爬注意**:
- 需要登录态 Cookie
- 请求频率限制
- 需要处理滑块验证

### 数据获取（个人主页）

**主页URL**: `https://www.xiaohongshu.com/user/profile/{user_id}`

**可获取数据**:
- 粉丝数
- 获赞与收藏数
- 笔记列表及基础数据

**限制**:
- 需要登录态
- 只能获取公开数据

### 发布（模拟）

**发布页面**: `https://creator.xiaohongshu.com/publish/publish`

**步骤**:
1. 登录创作者中心
2. 上传图片/视频
3. 填写标题和正文
4. 添加标签
5. 选择话题
6. 发布

**注意**: 小红书发布需要完整的登录态和可能的验证码处理，建议使用官方 API（如有）或半自动化方式（Agent辅助填写，人工确认发布）。

---

## Reddit

### API 访问

**文档**: https://www.reddit.com/dev/api/

**认证**: OAuth2

**常用端点**:
- 获取帖子: `GET /r/{subreddit}/hot.json`
- 搜索: `GET /search.json?q={query}&restrict_sr=on&sort=relevance`
- 提交帖子: `POST /api/submit`

### 发布

**POST /api/submit** 参数:
- `sr`: subreddit 名称
- `title`: 标题
- `text`: 正文（self post）
- `url`: 链接（link post）
- `kind`: 'self' 或 'link'

### 数据获取

**用户数据**: `GET /user/{username}/about.json`
- karma
- 创建时间
- 简介

**帖子数据**: `GET /r/{subreddit}/comments/{post_id}.json`

---

## Pinterest

### API 访问

**文档**: https://developers.pinterest.com/docs/api/v5/

**注意**: Pinterest API 需要商业账号和审核

### 内容抓取

**方法**: 浏览器自动化

**搜索URL**: `https://www.pinterest.com/search/pins/?q={keyword}`

**Pin 数据**:
- 图片 URL
- 描述
- 链接
- 保存数

### 发布 Pin

**API**: `POST /v5/pins`

**参数**:
- `title`: 标题
- `description`: 描述
- `board_id`: 画板 ID
- `media_source`: 图片 URL

---

## Discord

### API 访问

**文档**: https://discord.com/developers/docs/reference

**Bot Token**: 需要创建 Bot 获取 Token

### 发布消息

**Webhook**（最简单）:
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"content": "消息内容"}' \
  {webhook_url}
```

**Bot API**:
- `POST /channels/{channel.id}/messages`

### 内容适配

Discord 支持:
- 富文本 (Markdown)
- Embed（卡片）
- 图片附件
- 链接预览

---

## 通用抓取建议

### 浏览器自动化

**推荐工具**: Playwright

**基本流程**:
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    
    # 登录（手动或自动）
    page.goto("https://...")
    
    # 抓取数据
    elements = page.query_selector_all("[class*='note-item']")
    for el in elements:
        title = el.query_selector("[class*='title']")
        
    browser.close()
```

### 反爬虫策略

1. **请求间隔**: 随机 1-5 秒延迟
2. **User-Agent**: 使用真实浏览器 UA
3. **Cookie**: 保持登录态
4. **代理**: 必要时使用住宅代理
5. **行为模拟**: 滚动、点击等人工行为

### 数据存储

建议存储:
- 原始 HTML（便于重新解析）
- 解析后的结构化数据
- 抓取时间戳
- 来源 URL
