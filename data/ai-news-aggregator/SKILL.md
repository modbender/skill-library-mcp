---
name: "AI News Aggregator"
slug: ai-news-aggregator
version: "2.2.0"
homepage: https://github.com/lanyasheng/ai-news-aggregator
description: "AI/技术新闻聚合引擎。100+ RSS源并发抓取、兴趣评分、跨天去重、统一预取。"
changelog: "v2.2: unified prefetch, interest scoring, cross-day dedup, repo restructure"
metadata: {"clawdbot":{"emoji":"📰","requires":{"bins":["python3"]},"os":["linux","darwin","win32"]}}
---

# AI News Aggregator — AI/技术新闻高性能聚合引擎

并发抓取 100+ RSS 源，12秒完成，支持 ETag/Last-Modified 缓存、日期过滤。

## Setup

确保 Python 3.8+ 可用，无需额外依赖（纯标准库）。

## When to Use

用户需要查看 AI/技术新闻、技术趋势、最新论文、GitHub 热门项目、AI 公司动态时使用。

触发关键词：
- "AI 新闻"、"技术新闻"、"今天有什么新闻"
- "最新论文"、"arXiv"、"AI 研究"
- "GitHub 热门"、"趋势项目"
- "OpenAI 动态"、"Anthropic 更新"

## Architecture

```
ai-news-aggregator/
├── scripts/
│   ├── rss_aggregator.py      # 核心 RSS 抓取器
│   ├── rss_sources.json       # 100+ RSS 源配置
│   ├── arxiv_papers.py        # arXiv 论文搜索
│   ├── github_trending.py     # GitHub 热门项目
│   └── summarize_url.py       # 文章摘要
└── SKILL.md                   # 本文件
```

## Data Sources

| 分类 | 源数 | 内容 |
|------|------|------|
| company | 16 | OpenAI, Anthropic, Google, Meta, NVIDIA, Apple, Mistral 等官方博客 |
| papers | 6 | arXiv AI/ML/NLP/CV, HuggingFace Daily Papers, BAIR |
| media | 16 | MIT Tech Review, TechCrunch, Wired, The Verge, VentureBeat 等 |
| newsletter | 15 | Simon Willison, Lilian Weng, Andrew Ng, Karpathy 等专家 |
| community | 12 | HN, GitHub Trending, Product Hunt, V2EX 等 |
| cn_media | 5 | 机器之心, 量子位, 36氪, 少数派, InfoQ |
| ai-agent | 5 | LangChain, LlamaIndex, Mem0, Ollama, vLLM 博客 |
| twitter | 10 | Sam Altman, Karpathy, LeCun, Hassabis 等 AI 领袖 |

## Core Commands

### RSS 聚合
```bash
# 抓取所有源（最近3天新闻）
python3 skills/ai-news-aggregator/scripts/rss_aggregator.py --category all --days 3 --limit 10

# 只看公司博客
python3 skills/ai-news-aggregator/scripts/rss_aggregator.py --category company --days 1 --limit 5

# 只看中文媒体
python3 skills/ai-news-aggregator/scripts/rss_aggregator.py --category cn_media --days 3 --limit 10

# AI Agent 相关
python3 skills/ai-news-aggregator/scripts/rss_aggregator.py --category ai-agent --days 7 --limit 10

# 输出 JSON 格式
python3 skills/ai-news-aggregator/scripts/rss_aggregator.py --category all --days 1 --json
```

### arXiv 论文
```bash
# 最新 AI 论文（按热度排序）
python3 skills/ai-news-aggregator/scripts/arxiv_papers.py --limit 5 --top 10

# 搜索特定主题
python3 skills/ai-news-aggregator/scripts/arxiv_papers.py --query "multi-agent" --top 5
```

### GitHub Trending
```bash
# AI 相关热门项目（今日）
python3 skills/ai-news-aggregator/scripts/github_trending.py --ai-only

# 本周热门
python3 skills/ai-news-aggregator/scripts/github_trending.py --since weekly
```

## Core Rules

### 1. 优先使用 --days 参数
默认抓取最近 N 天的新闻，避免获取过期内容：
- 日报：`--days 1`
- 周报：`--days 7`
- 月报：`--days 30`

### 2. 分类选择策略
| 用户需求 | 推荐分类 |
|----------|----------|
| 公司动态 | `--category company` |
| 技术论文 | `--category papers` |
| 中文资讯 | `--category cn_media` |
| 社区趋势 | `--category community` |
| AI Agent | `--category ai-agent` |

### 3. 缓存机制
- 首次抓取后自动缓存（ETag/Last-Modified）
- 缓存有效期 1 小时
- 重复抓取秒级完成

## Configuration

编辑 `scripts/rss_sources.json` 添加/删除 RSS 源：
```json
{
  "name": "OpenAI Blog",
  "url": "https://openai.com/blog/rss.xml",
  "category": "company"
}
```