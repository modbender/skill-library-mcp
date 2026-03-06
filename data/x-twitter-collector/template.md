# X/Twitter 推文收集报告模板

## 报告头部
```markdown
## 📊 {username} 过去 24 小时推文完整报告
## Complete 24-Hour Tweet Report for @{username}

**统计时间 / Report Time:** {date} {time} ({timezone})

**📸 完整页面截图 / Full Page Screenshot:**
![页面截图]({screenshot_path})
```

## 数据概览表格
```markdown
### 📈 数据概览 / Data Overview

| 类型 / Type | 数量 / Count |
|------|------|
| **原创推文 / Original Tweets** | {original_count} 条 |
| **转帖 / Retweets** | {retweet_count} 条 |
| **总计 / Total** | {total_count} 条 |
```

## 原创推文模板
```markdown
### {index}️⃣ {time_ago} - {topic_cn} / {topic_en}

| 🇨🇳 中文 | 🇺🇸 English |
|----------|-------------|
| **{tweet_content_cn}** | **{tweet_content_en}** |
| {context_cn} | {context_en} |

**📊 互动数据 / Engagement:**
- 💬 {replies} 回复 / Replies
- 🔄 {retweets} 转帖 / Retweets
- ❤️ {likes} 点赞 / Likes
- 👁️ {views} 次浏览 / Views

**🔗 链接 / Link:** {tweet_url}
```

## 转帖列表模板
```markdown
## 🔁 主要转帖 / Key Retweets（{count} 条）

| # | 时间 / Time | 来源 / Source | 内容主题 / Topic | 🔗 链接 / Link |
|---|------|------|------|---------|
| {row_data} |
```

## 主题分析模板
```markdown
## 🎯 主题分析 / Topic Analysis

| 主题 / Topic | 原创 / Original | 转帖 / Retweets | 总计 / Total |
|------|------|------|------|
| {topic_rows} |
```

## 数据汇总模板
```markdown
## 📈 数据汇总 / Data Summary

| 指标 / Metric | 数值 / Value |
|------|------|
| **原创推文 / Original Tweets** | {original_count} 条 |
| **转帖 / Retweets** | {retweet_count} 条 |
| **总推文数 / Total Tweets** | {total_count} 条 |
| **总浏览数 / Total Views** | {total_views} |
| **总点赞数 / Total Likes** | {total_likes} |
| **最热门推文 / Top Tweet** | {top_tweet} |
```

## 结尾模板
```markdown
---

**📸 完整页面截图已保存 / Full page screenshot saved.**

需要我为某条特定推文单独截图或获取更多详细信息吗？ / Need me to screenshot a specific tweet or get more details?
```

## 使用说明

### 变量替换
- `{username}` - X 用户名
- `{date}` - 日期
- `{time}` - 时间
- `{timezone}` - 时区
- `{screenshot_path}` - 截图文件路径
- `{original_count}` - 原创推文数量
- `{retweet_count}` - 转帖数量
- `{total_count}` - 总数量
- `{index}` - 推文序号
- `{time_ago}` - 发布时间（如 "1 小时前"）
- `{topic_cn}` - 主题中文
- `{topic_en}` - 主题英文
- `{tweet_content_cn}` - 推文内容中文
- `{tweet_content_en}` - 推文内容英文
- `{context_cn}` - 上下文中文（如引用说明）
- `{context_en}` - 上下文英文
- `{replies}` - 回复数
- `{retweets}` - 转帖数
- `{likes}` - 点赞数
- `{views}` - 浏览数
- `{tweet_url}` - 推文链接
- `{total_views}` - 总浏览数
- `{total_likes}` - 总点赞数
- `{top_tweet}` - 最热门推文信息
- `{row_data}` - 转帖列表行数据
- `{topic_rows}` - 主题分析行数据

### 使用方式
1. 复制模板到剪贴板
2. 替换所有 `{变量}` 为实际数据
3. 生成最终报告
