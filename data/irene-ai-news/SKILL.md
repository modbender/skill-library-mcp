---
name: daily-ai-news
description: >
  Daily AI news aggregator. Fetches latest AI-related content from HackerNews, 
  GitHub Trending, ArXiv papers, and web search (Brave/Tavily). Use for: 
  (1) Getting daily AI digest, (2) Staying updated with trending AI projects, 
  (3) Discovering latest research papers, (4) Web search for breaking news.
  Triggers: ai news, daily digest, what's new in ai, tech news.
version: "1.1.0"
user-invocable: true
metadata:
  openclaw:
    emoji: 📰
    requires:
      tools: ["web_search", "web_fetch"]
      bins: ["python3", "curl"]
    suggests: ["openclaw-tavily-search"]
---

# Daily AI News - 每日 AI 资讯聚合器

自动抓取 AI 领域最新资讯，包括 HackerNews 热帖、GitHub 趋势项目、ArXiv 论文摘要，以及实时网络搜索。

## 功能特性

- 🤖 **AI 智能筛选** - 自动识别 AI/ML 相关内容
- 📊 **多源聚合** - HackerNews + GitHub + ArXiv + 网络搜索
- 🔍 **实时搜索** - 支持 Brave Search 或 Tavily（无需信用卡）
- 🕘 **定时推送** - 支持 Cron 定时任务
- 💬 **一键分享** - 直接发送到聊天频道
- 💳 **零门槛** - Tavily 方案无需绑定信用卡

## 搜索方案选择

| 方案 | 优点 | 是否需要信用卡 | 配置方式 |
|------|------|----------------|----------|
| **Tavily** ⭐推荐 | 1000次/月免费，AI增强结果 | ❌ 不需要 | 安装 `openclaw-tavily-search` skill |
| **Brave** | OpenClaw原生支持 | ✅ 需要 | `openclaw configure --section web` |

### Tavily 配置（推荐）

1. 安装社区skill：
```bash
clawhub install openclaw-tavily-search
```

2. 获取免费API Key：
   - 访问 https://tavily.com/
   - 注册账号（仅需邮箱）
   - Dashboard复制API Key

3. 配置环境变量：
```bash
echo 'TAVILY_API_KEY=tvly-你的key' >> ~/.openclaw/.env
```

### Brave Search 配置

```bash
openclaw configure --section web
# 输入 Brave Search API Key
```

## 使用方法

### 主动查询
```
"今天有什么 AI 新闻"
"获取最新的 AI 资讯"
"显示今日 AI 摘要"
"搜索 OpenAI 最新消息"
```

### 定时推送（Cron 配置）
```json
{
  "cron": {
    "jobs": [
      {
        "schedule": "0 9 * * *",
        "command": "python3 ~/.openclaw/workspace/data/skills/daily-ai-news/scripts/ai_news.py --send",
        "channel": "feishu"
      }
    ]
  }
}
```

## 数据源

| 来源 | 内容类型 | 更新频率 |
|------|---------|---------|
| HackerNews | 技术讨论、产品发布 | 实时 |
| GitHub Trending | 开源项目、工具库 | 每日 |
| ArXiv | 学术论文、研究进展 | 每日 |
| Web Search | 突发新闻、官方公告 | 实时 |

## 输出格式

```markdown
📰 每日 AI 资讯 - 2026-03-02

## 🔥 热点头条（Web搜索）
• [标题] - 简短描述... [链接]
• [标题] - 简短描述... [链接]

## 💬 HackerNews 热门
• [标题] - 简短描述... [链接]
• [标题] - 简短描述... [链接]

## ⭐ GitHub 趋势
• [项目名] ⭐ Stars - 项目描述... [链接]
• [项目名] ⭐ Stars - 项目描述... [链接]

## 📄 ArXiv 论文
• [论文标题] - 作者/机构 - 一句话摘要... [链接]
• [论文标题] - 作者/机构 - 一句话摘要... [链接]

---
💡 提示: 回复 "详细+序号" 查看完整内容
```

## 安装

```bash
# 从 ClawHub 安装
clawhub install irene-ai-news

# 或手动克隆到 workspace skills 目录
cd ~/.openclaw/workspace/data/skills
git clone <repo-url> daily-ai-news
```

## 依赖

- Python 3.8+
- curl
- Tavily API Key（推荐）或 Brave Search API Key

## 配置选项

编辑 `scripts/ai_news.py` 顶部配置区：

```python
CONFIG = {
    "max_hackernews": 5,      # HN 条目数
    "max_github": 5,          # GitHub 项目数
    "max_arxiv": 3,           # 论文数
    "max_web_search": 5,      # 网络搜索条数
    "categories": ["ai", "ml", "llm", "gpt", "neural"],  # 关键词过滤
    "search_provider": "auto", # auto/tavily/brave
}
```

## 手动运行测试

```bash
# 仅显示结果
python3 scripts/ai_news.py

# 使用 Tavily 搜索
python3 scripts/ai_news.py --provider tavily

# 发送到当前频道
python3 scripts/ai_news.py --send

# 发送到指定频道
python3 scripts/ai_news.py --send --channel feishu
```

## 技术实现

- **HackerNews**: 官方 Algolia API
- **GitHub**: Trending 页面解析
- **ArXiv**: RSS Feed + 摘要提取
- **Web Search**: Brave Search API 或 Tavily API

## Changelog

### v1.1.0 (2026-03-02)
- ✨ 新增 Tavily 搜索支持（无需信用卡）
- 🔍 集成网络搜索获取实时AI新闻
- 📚 更新文档，添加双方案配置说明

### v1.0.0 (2026-03-02)
- 🎉 初始发布
- 📊 HackerNews + GitHub + ArXiv 聚合

## License

MIT
