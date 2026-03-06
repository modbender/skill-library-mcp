---
name: x-followings-digest
description: |
  Auto-fetch latest tweets from your X/Twitter followings and generate structured AI digest. Supports custom time ranges: 1 day, 3 days, 7 days, or custom.
  
  自动抓取X/Twitter关注列表的最新推文，并使用AI分析师提示词生成结构化日报。支持自定义时间段：1天、3天、7天或自定义天数。
  
  **Trigger Words:**
  - "summarize my followings", "X digest", "Twitter summary", "tweets from last 3 days", "weekly summary"
  
  **触发词：**
  - "总结关注列表", "X日报", "Twitter摘要", "过去3天的推文", "一周摘要"
  
  **Prerequisites:** X auth via AUTH_TOKEN & CT0 env vars
---

# X关注列表日报生成器 / X Followings Digest Generator

自动抓取你关注的人的最新推文，并生成结构化的AI日报。

Auto-fetch latest tweets from your followings and generate structured AI digest.

## 快速开始 / Quick Start

### 1. 配置X授权 / Configure X Auth

```bash
export AUTH_TOKEN="your_auth_token"
export CT0="your_ct0"
```

### 2. 获取关注列表推文 / Fetch Tweets

```bash
# 默认最近1天 / Default: last 1 day
./scripts/fetch_followings_tweets.sh

# 指定数量和时间 / Specify count & days
./scripts/fetch_followings_tweets.sh 50 1   # 50 tweets, 1 day
./scripts/fetch_followings_tweets.sh 50 3   # 50 tweets, 3 days
./scripts/fetch_followings_tweets.sh 100 7  # 100 tweets, 7 days (weekly)
```

### 3. 生成日报 / Generate Digest

将获取到的推文内容，使用 [analyst_prompt_template.md](references/analyst_prompt_template.md) 中的提示词模板进行分析。

Feed the fetched tweets to the AI using the prompt template in `references/analyst_prompt_template.md`.

## 输出格式 / Output Format

日报包含以下分类（仅显示有内容的类别）：

Digest includes (only shows categories with content):

- **🔥 重大事件 / Major Events** - 具体细节和影响分析 / Specific details & impact analysis
- **🚀 产品发布 / Product Releases** - 新模型、API更新、工具版本 / New models, API updates, tools
- **💡 技术洞察 / Tech Insights** - 技术方案、优化技巧、代码片段 / Technical solutions, optimizations
- **🔗 资源汇总 / Resources** - 论文、开源项目、教程、工具 / Papers, OSS, tutorials, tools
- **🎁 福利羊毛 / Deals & Freebies** - 免费额度、优惠、赠品 / Free credits, discounts, giveaways
- **📊 舆情信号 / Signals** - 争议话题、预测、警告 / Controversies, predictions, warnings

## 语言设置 / Language Setting

在调用AI分析时，通过提示词指定输出语言：

When calling the AI, specify output language in the prompt:

- **中文输出**: 使用提示词中的 [中文] 部分
- **English Output**: Use the [EN] section in the prompt template
- **中英双语**: 使用完整提示词，要求 bilingual output

## 依赖 / Dependencies

- `bird` CLI (X/Twitter client)
- `AUTH_TOKEN` & `CT0` from browser cookies

## 注意事项 / Notes

- 推文数量越多，处理时间越长
- More tweets = longer processing time
- 建议设置定时任务每日自动运行
- Recommended: set up cron job for daily auto-run
