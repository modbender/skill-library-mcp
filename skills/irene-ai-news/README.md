# Daily AI News 📰

OpenClaw Skill - 每日 AI 资讯聚合器

## 功能

自动抓取并汇总 AI 领域最新动态：
- 🔥 **HackerNews** - AI 相关热门讨论
- ⭐ **GitHub** -  trending AI 开源项目  
- 📄 **ArXiv** - 最新 AI/ML 研究论文

## 快速开始

### 安装

```bash
# 方法1: 复制到 workspace skills 目录
cp -r daily-ai-news ~/.openclaw/workspace/data/skills/

# 方法2: 从 ClawHub 安装（发布后）
openclaw skill install daily-ai-news
```

### 使用

**主动查询:**
```
"今天有什么 AI 新闻"
"获取 AI 资讯"
"显示今日科技摘要"
```

**手动运行:**
```bash
# 仅显示
python3 ~/.openclaw/workspace/data/skills/daily-ai-news/scripts/ai_news.py

# 发送到当前频道
python3 ~/.openclaw/workspace/data/skills/daily-ai-news/scripts/ai_news.py --send
```

### 定时推送配置

在 `~/.openclaw/openclaw.json` 中添加 cron job:

```json
{
  "cron": {
    "jobs": [
      {
        "id": "daily-ai-news",
        "schedule": "0 9 * * *",
        "command": "python3 ~/.openclaw/workspace/data/skills/daily-ai-news/scripts/ai_news.py --send",
        "mode": "isolated",
        "delivery": {
          "target": "last"
        }
      }
    ]
  }
}
```

每天早上 9 点自动推送 AI 资讯到上次联系的频道。

## 配置

编辑 `scripts/ai_news.py` 修改配置:

```python
CONFIG = {
    "max_hackernews": 5,      # HN 条目数
    "max_github": 5,          # GitHub 项目数
    "max_arxiv": 3,           # 论文数
    "keywords": ["ai", "ml", ...],  # 关键词过滤
}
```

## 依赖

- Python 3.8+
- 无需额外 pip 包（只用标准库）
- 无需 API Key

## 输出示例

```markdown
📰 每日 AI 资讯 - 2026-03-02

## 🔥 HackerNews 热门
1. [OpenAI releases GPT-5] (128👍)
2. [New neural architecture breakthrough] (95👍)
...

## ⭐ GitHub 趋势项目
1. **awesome-llm** ⭐15,234
   A curated list of Large Language Model resources
   
2. **local-ai** ⭐8,456
   Run AI models locally with one command
...

## 📄 ArXiv 最新论文
1. [Attention Is All You Need: Revisited]
   We revisit the transformer architecture and propose improvements...
...
```

## License

MIT © 2026
