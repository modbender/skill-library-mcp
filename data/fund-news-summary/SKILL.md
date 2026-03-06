---
name: fund-news-summary
description: Automatically collects and summarizes the latest core news for US, Europe, Japan stock markets, gold, and prediction markets. Use when user asks about fund news, market updates, investment research, or daily financial summaries. Also triggered automatically via cron job at 11:00 Beijing Time daily.
---

# Fund News Summary Skill

## Purpose

Automatically collects and summarizes the latest core news for specified funds across multiple markets.

## Supported Markets

- **US Markets**: NASDAQ, S&P 500
- **Europe**: European equity markets
- **Japan**: Japanese stock market
- **Commodities**: Gold
- **Prediction Markets**: Polymarket and prediction market news

## Execution

### Automatic (Cron Job)

This skill is bound to the `DailyFundNews` cron job, executing automatically at **11:00 Beijing Time** daily.

### Manual Trigger

User can ask:
- "Get today's fund news"
- "Show market updates"
- "What's the latest on my funds?"
- "Run fund news summary"

When triggered, the Agent should:

1. **Run the script**: `python3 /root/clawd/skills/fund-news-summary/fund_news.py`
2. **Read output**: The script automatically generates a report and outputs to stdout
3. **Send to Telegram**: Send the script output directly to Telegram

## Script Features

- ✅ **Multi-market coverage**: US, Europe, Japan, Gold, Polymarket
- ✅ **Rate limiting**: Maximum 2 concurrent searches, 1.5 second request interval
- ✅ **Retry mechanism**: Automatic retry on rate limit
- ✅ **Error handling**: Individual fund failures don't affect others
- ✅ **Formatted output**: Bold list format
- ✅ **Obsidian sync**: Saves Chinese version to Obsidian
- ✅ **Auto GitHub push**: Automatically pushes to GitHub after generation

## Fund Configuration

The script has built-in keywords for:
- 华宝纳斯达克精选股票 (QDII)C
- 摩根欧洲动力策略股票 (QDII)A
- 摩根日本精选股票 (QDI)A
- 易方达黄金 ETF 联接 C
- 标普500 (S&P 500 Index)
- Polymarket / 预测市场

## Error Handling

### Common Issues

**Issue**: Script fails with "Rate limit exceeded"
- **Cause**: Too many requests to search API
- **Solution**: Script has built-in retry with exponential backoff. Wait 5 minutes and retry.

**Issue**: Empty or partial report
- **Cause**: Some fund APIs may be temporarily unavailable
- **Solution**: Check individual fund sources. The script continues even if some funds fail.

**Issue**: GitHub push fails
- **Cause**: Network issue or authentication expired
- **Solution**: Report success/failure in output. User can manually push if needed.

## Output Format

The script outputs a formatted report with:
- Market name and fund name (bold)
- Key news summary with bullet points
- Last updated timestamp

## Data Storage

- **Obsidian save path**: `/root/clawd/obsidian-vault/reports/fund/YYYY-MM-DD.md`
- **Filename format**: `YYYY-MM-DD.md`
- **Language**: Chinese (translated from English API results)
- **GitHub repo**: `https://github.com/YonghaoZhao722/yonghao-notes`
- **Branch**: `master`

## Manual Execution (Debug)

```bash
cd /root/clawd/skills/fund-news-summary
python3 fund_news.py
```
