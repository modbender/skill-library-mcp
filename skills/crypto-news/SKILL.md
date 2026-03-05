---
name: blockbeats-news
description: 获取律动 BlockBeats 最新的加密货币、Web3 及 AI 行业快讯。
metadata:
  openclaw:
    emoji: "📰"
    requires:
      bins: ["node"]
      env: ["BLOCKBEATS_API_KEY"]
---

# BlockBeats 行业快讯抓取

当用户询问最新的 Web3 行业新闻、特定币种动态或需要快讯追踪时，请使用本技能。

## 执行方式

本技能使用原生的 Node.js 脚本执行，完全开源透明，无需额外安装依赖。
你需要通过环境变量向脚本传递用户请求的参数：
- `NEWS_SIZE`：获取的条数（默认 10）。
- `NEWS_PAGE`：页码（默认 1）。
- `NEWS_TYPE`：快讯类别（如 'AI', 'DeFi', 'NFT'，不填则获取全部）。

**执行命令示例：**
```bash
NEWS_SIZE="5" NEWS_TYPE="AI" node index.js