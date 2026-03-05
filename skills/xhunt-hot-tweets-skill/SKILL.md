---
name: xhunt-hot-tweets
description: 从 XHunt 抓取 X/Twitter 热门推文榜单并输出中文摘要与互动数据。用户提到“最火推文/热门帖子/Top20/4小时最火/只要AI/AI最火/给我链接+摘要”等请求时使用。支持 group=global|cn、hours=1|4|24、tag=ai|crypto|全部，并可切换过滤模式（全部/仅AI产品与模型更新/允许政治争议）。
compatibility: 需要可访问 https://trends.xhunt.ai；优先 browser 快照抓取，失败时可降级 web_fetch（结果可能不完整）。
metadata:
  author: Javis
  version: 2.0.1
---

# XHunt 热门推文提取（v2）

目标：稳定输出“可直接转发/复盘”的热门推文清单（链接 + 一句话摘要 + 核心互动数据）。

## 1) 参数解析（先做）
默认参数：
- `group=global`
- `hours=24`
- `tag=ai`
- `limit=20`
- `mode=all`（不过滤政治）

按用户话术覆盖：
- “华语区”→ `group=cn`
- “4小时/1小时/24小时”→ `hours`
- “只要AI”→ `tag=ai`
- “全部最火”→ 不传 `tag`
- “Top10/Top20/Top30”→ `limit`
- “只看AI产品/模型更新”→ `mode=ai-product-only`
- “可以有政治争议”→ `mode=all`

URL 模板：
- 基础：`https://trends.xhunt.ai/zh/tweets?group=<group>&hours=<hours>`
- 有标签：在末尾追加 `&tag=<tag>`

## 2) 抓取策略（固定顺序）
1. 优先 `browser` 打开目标 URL + `snapshot(refs=aria)`。
2. 从榜单卡片提取：排名、作者、链接、标题、views、likes、retweets、热度。
3. 若 browser 失败，降级 `web_fetch`，并在输出首行标注：
   - `说明：本次使用降级抓取，字段可能不完整。`
4. 若两种抓取都失败，直接返回错误说明，不得编造数据：
   - `说明：抓取失败（网络或页面结构变化），请稍后重试。`

## 3) 过滤规则
### mode=all
- 不做内容过滤（含政治争议）。

### mode=ai-product-only
保留：
- 模型发布/更新（如 Claude、GPT、Qwen、Gemini 等）
- AI 产品与工具更新（如 Cursor、Perplexity、Notion AI、Devin 等）
- AI agent/workflow/开发工具实操内容
- AI 基础设施与算力（与 AI 直接相关）

剔除：
- 纯政治选举/党争（无 AI 主体）
- 纯加密炒作（无 AI 主体）
- 娱乐八卦与空洞内容

若过滤后不足 `limit`：
- 继续向后补齐；仍不足则如实返回实际条数，不编造。

## 4) 输出格式（严格）
首行口径：
- `数据源：XHunt 推文榜（<group> / <hours>h / <tag或全部>）`

列表：每条固定 3 行
1. `N) <tweet_url>`
2. `摘要：<一句中文摘要>`
3. `数据：<views>｜<likes>｜<retweets>｜热度<score>`

末尾补“观察”3条：
- 当前最强话题簇
- 高互动内容的共同结构
- 适合用户二次创作的切入角度

## 5) 质量门槛
- 不输出无链接条目。
- 不输出“内容为空”类摘要；遇到则跳过补位。
- 摘要必须是“信息点 + 结果/影响”，避免空话。
- 数据字段缺失时写“NA”，不要臆造。
- 若过滤后不足 `limit`，返回真实条数，并在末尾加一句：
  - `说明：符合条件条目不足 <limit>，已返回全部可用结果。`

## 6) 快速模板（执行时可直接套）
用户：`四小时最火帖子，只要AI，给我Top20，每个一条摘要`

执行参数：
- `group=global`
- `hours=4`
- `tag=ai`
- `limit=20`
- `mode=ai-product-only`
