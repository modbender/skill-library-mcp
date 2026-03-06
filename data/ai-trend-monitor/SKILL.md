---
name: AI Trend Monitor
description: 监控 AI 市场趋势和技术前沿，支持实时重大新闻推送 + 定时汇总推送。
---

# AI Trend Monitor

监控 AI 市场趋势和技术前沿，支持实时重大新闻推送 + 定时汇总推送。

## 功能

- **多渠道监控**：GitHub、Reddit、Twitter/X、小红书、新闻
- **智能 URL 提取**：自动提取具体帖子/文章 URL（非首页）
- **重大新闻实时推送**：检测到重大新闻立即推送
- **定时汇总**：每天 9:00、13:00、19:00 定时推送
- **飞书卡片格式**：分渠道表格，完整文本，可跳转链接

## 安装

```bash
# 克隆到 skills 目录
git clone <repo-url> ~/.openclaw/skills/ai_trend_monitor

# 安装依赖
cd ~/.openclaw/skills/ai_trend_monitor
npm install
```

## 配置

编辑 `config.js`：

```javascript
module.exports = {
  // 飞书 Webhook
  webhooks: {
    market: 'https://open.feishu.cn/open-apis/bot/v2/hook/xxx',
    tech: 'https://open.feishu.cn/open-apis/bot/v2/hook/xxx'
  },
  
  // 监控渠道
  channels: ['GitHub', 'Reddit', 'Twitter', '小红书', '新闻'],
  
  // 推送时间
  schedule: {
    morning: '0 9 * * *',    // 9:00
    noon: '0 13 * * *',      // 13:00
    evening: '0 19 * * *'    // 19:00
  },
  
  // 重大新闻判定标准
  majorNewsCriteria: {
    funding: 100000000,      // 1亿美元
    stockChange: 5,          // 股价涨跌5%
    keyPeople: ['Sam Altman', 'Elon Musk', 'Andrej Karpathy'],
    keyCompanies: ['OpenAI', 'Google', 'Anthropic', 'Meta', 'xAI']
  }
};
```

## 使用

### 手动运行

```bash
node ai_trend_monitor.js
```

### 定时任务

使用 OpenClaw cron：

```json
{
  "jobs": [
    {
      "name": "ai-trend-morning",
      "schedule": "0 9 * * *",
      "command": "node ~/.openclaw/skills/ai_trend_monitor/ai_trend_monitor.js"
    },
    {
      "name": "ai-trend-noon",
      "schedule": "0 13 * * *",
      "command": "node ~/.openclaw/skills/ai_trend_monitor/ai_trend_monitor.js"
    },
    {
      "name": "ai-trend-evening",
      "schedule": "0 19 * * *",
      "command": "node ~/.openclaw/skills/ai_trend_monitor/ai_trend_monitor.js"
    }
  ]
}
```

## 消息格式

飞书卡片消息，按渠道分组：

| 渠道 | 标题 | 概述 | 时间 | 影响分析 | 链接 |
|------|------|------|------|----------|------|
| GitHub | xxx | xxx | 2026-02-19 08:00 | xxx | [查看] |
| Reddit | xxx | xxx | 2026-02-19 10:30 | xxx | [查看] |

## 依赖

- Node.js >= 18
- OpenClaw CLI（用于定时任务）
- kimi_search API（用于实时搜索）

## 版本

v1.0.0

## 作者

小赵

## License

MIT
