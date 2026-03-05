---
name: xiaohongshu-deep-research
description: Deep research on Xiaohongshu (小红书) topics. Use when user wants to research a topic, analyze trends, gather insights from top posts, or produce a summary report. Crawls posts via search, extracts high-engagement content, generates analysis with post links. Requires xiaohongshu-mcp service running.
---

# xiaohongshu-deep-research

小红书话题研究，自动爬取 + 分析 + 输出报告。

## 前置条件

- xiaohongshu-mcp 服务运行中 (`http://localhost:18060/mcp`)
- 已登录小红书账号

## 存储位置

```
~/xiaohongshu-research/{keyword}_{YYYYMMDD_HHmm}/
├── raw/posts.json        # 原始数据
├── analysis/summary.md   # 完整报告
└── metadata.json         # 研究配置
```

## 研究流程

1. **关键词扩展** — 主词 + 3-4 个相关词
2. **批量搜索** — `POST /api/v1/feeds/search`
3. **去重排序** — 按点赞数取 Top 20-50
4. **生成报告** — 含链接、可转发摘要

## 帖子链接格式

```
https://www.xiaohongshu.com/explore/{note_id}
```

## 报告结构

```markdown
# {主题} 小红书研究

---

## 📱 速览（可直接转发）

{2-3段自然语言总结，像朋友分享一样写}

值得看的几篇：
• {标题} — {链接}
• {标题} — {链接}

---

## 数据概览

采集 {N} 篇帖子，共 {likes} 赞 / {collects} 收藏

## Top 10

1. **{标题}** @{作者}
   {likes}👍 {collects}📁 | [查看]({link})

## 发现

{自然语言描述趋势和洞察}

## 数据

原始数据: `{path}`
```

## 写作风格

- 速览部分：像给朋友发消息，口语化，有观点
- 正文部分：简洁，重点突出，避免套话
- 不要用"本报告"、"经过分析"这类官腔

## 限制

⚠️ API 限制：帖子详情和评论无法获取，报告基于搜索结果元数据生成。

## 详细工作流

见 [references/workflow.md](references/workflow.md)

## Credits

基于 [xpzouying/xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp)
