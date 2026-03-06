---
name: google-ai-usage-monitor
version: 1.0.0
description: Monitor Google AI Studio (Gemini API) usage, rate limits, and quota consumption with automated alerts.
author: xiaoyaner
---

# Google AI Usage Monitor Skill

Monitor Google AI Studio usage to prevent quota exhaustion and optimize API consumption.

## Supported Metrics

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| RPM | Requests Per Minute (peak) | > 80% of limit |
| TPM | Tokens Per Minute (peak) | > 80% of limit |
| RPD | Requests Per Day | > 80% of limit |

## Rate Limits by Tier

| Tier | Typical Limits |
|------|---------------|
| Free | 2 RPM, 32K TPM, 50 RPD |
| Pay-as-you-go | 10-15 RPM, 100K+ TPM, 500+ RPD |
| Paid Tier 1 | 20 RPM, 100K TPM, 250 RPD (varies by model) |

Note: Actual limits vary by model and can be viewed at the usage dashboard.

## Usage Dashboard

### URL
```
https://aistudio.google.com/usage?project={PROJECT_ID}&timeRange=last-28-days&tab=rate-limit
```

### Key Elements to Extract
- **Project name**: Which GCP project
- **Tier**: Free / Pay-as-you-go / Paid tier X
- **Models table**: Each row contains model name, category, RPM, TPM, RPD
- **Time range**: Default 28 days

## Browser Automation

### Open Usage Page
```javascript
// Using OpenClaw browser tool
browser action=open targetUrl="https://aistudio.google.com/usage?project=YOUR_PROJECT_ID&timeRange=last-28-days&tab=rate-limit" profile=openclaw
```

### Wait for Data Load
The page loads data asynchronously. Wait for:
1. Project dropdown shows project name (not "Loading...")
2. Rate limits table has data rows

### Parse Table Data
Look for table rows with pattern:
```
Model Name | Category | X / Y | X / Y | X / Y | View in charts
```

Where `X / Y` represents `used / limit`.

## Report Format

### Discord Message Template

```markdown
## 📊 Google AI Studio 用量报告

**项目**: {project_name}
**付费等级**: {tier}
**统计周期**: 过去 28 天

---

### {Model Name}
| 指标 | 用量 | 限额 | 使用率 |
|------|------|------|--------|
| RPM | {rpm_used} | {rpm_limit} | {rpm_pct}% |
| TPM | {tpm_used} | {tpm_limit} | {tpm_pct}% |
| RPD | {rpd_used} | {rpd_limit} | {rpd_pct}% |

---

{status_emoji} **状态**: {status_text}

*检查时间: {timestamp}*
```

### Status Levels

| Usage % | Status | Emoji | Action |
|---------|--------|-------|--------|
| < 50% | 正常 | ✅ | Continue normally |
| 50-80% | 需关注 | ⚠️ | Monitor more frequently |
| > 80% | 风险预警 | 🚨 | Alert user, consider rate limiting |

## Alert Rules

### When to Alert User

1. **Any metric > 80%**: Immediate alert with @mention
2. **Any metric > 50%**: Include warning note in report
3. **API errors (429)**: Track rate limit hits

### Alert Message Template

```markdown
🚨 **Google AI 配额预警**

<@USER_ID> 以下指标接近限额：

- **{model}** {metric}: {used}/{limit} ({pct}%)

建议：
- 减少 API 调用频率
- 考虑升级付费等级
- 检查是否有异常调用
```

## Cron Job Setup

### Daily Check (Recommended)

```json
{
  "name": "Google AI 用量检查",
  "schedule": {
    "kind": "cron",
    "expr": "0 20 * * *",
    "tz": "Asia/Shanghai"
  },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "检查 Google AI Studio 用量并发送报告到指定 Discord 频道"
  },
  "delivery": {
    "mode": "announce",
    "channel": "discord",
    "to": "CHANNEL_ID"
  }
}
```

## Integration with OpenClaw

### Configuration

Add to `TOOLS.md`:

```markdown
## Google AI Studio

- **Project ID**: gen-lang-client-XXXXXXXXXX
- **Dashboard**: https://aistudio.google.com/usage
- **Discord Channel**: #google-ai (CHANNEL_ID)
- **Check Schedule**: Daily 20:00
```

### Heartbeat Integration

Add to `HEARTBEAT.md`:

```markdown
## Google AI Monitoring
- Check usage if last check > 24 hours
- Alert if any metric > 80%
```

## Troubleshooting

### Page Not Loading

1. Check if logged into correct Google account
2. Verify project ID is correct
3. Wait longer for async data load (5-10 seconds)

### Data Shows "Loading..."

The project dropdown may take time to populate. Retry snapshot after a few seconds.

### Metrics Not Updating

Google notes: "Usage data may take up to 15 minutes to update."

## References

- [Google AI Studio Usage Dashboard](https://aistudio.google.com/usage)
- [Gemini API Rate Limits](https://ai.google.dev/gemini-api/docs/rate-limits)
- [Billing Documentation](https://ai.google.dev/gemini-api/docs/billing)
- [Cloud Monitoring for Gemini](https://firebase.google.com/docs/ai-logic/monitoring)
