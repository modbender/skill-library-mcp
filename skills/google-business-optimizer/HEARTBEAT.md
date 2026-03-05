# HEARTBEAT.md - Google Business Optimizer Automation

This file defines automated tasks that run on OpenClaw heartbeat polls.

---

## Overview

Google Business Optimizer uses HEARTBEAT automation to keep your business profile
optimized without manual intervention. The system checks for new reviews, monitors
competitors, and tracks rankings on a regular schedule.

---

## Daily Tasks (Every 6 Hours)

### Review Check & Auto-Response

```yaml
task: daily-review-check
schedule: "0 */6 * * *"
enabled: true
conditions:
  - plan: [pro, agency]  # Auto-response requires PRO+
actions:
  - check_new_reviews
  - auto_respond_with_ai  # PRO/AGENCY only
  - notify_owner_of_critical_reviews
```

**What happens:**
1. Polls Google Business Profile API for new reviews
2. For PRO/AGENCY: Generates AI response using configured template
3. Sends Slack/email notification for 1-2 star reviews (requires attention)
4. Logs all activity to local database

**Configuration:**
```bash
# Set response template (pro/agency only)
google-business-optimizer config --response-template=friendly

# Enable/disable auto-response
google-business-optimizer config --auto-respond=true

# Set notification channel
google-business-optimizer config --notify-channel=slack
```

---

## Weekly Tasks (Every Monday 9 AM)

### Competitor Analysis Report

```yaml
task: weekly-competitor-report
schedule: "0 9 * * 1"
enabled: true
conditions:
  - plan: [pro, agency]
  - competitors_tracked: "> 0"
actions:
  - fetch_competitor_data
  - compare_metrics
  - generate_pdf_report
  - send_email_report
```

**What happens:**
1. Fetches latest data for all tracked competitors
2. Compares ratings, review counts, and photos
3. Identifies ranking changes and trends
4. Generates PDF report with insights
5. Emails report to configured address

**Report includes:**
- Your current rating vs competitors
- Review velocity (new reviews per week)
- Photo engagement comparison
- Ranking position changes
- Actionable recommendations

**Configuration:**
```bash
# Add competitors to track
google-business-optimizer competitors --add "Competitor Name"

# Set report recipients
google-business-optimizer config --report-email=owner@business.com

# Set report format (pdf/html)
google-business-optimizer config --report-format=pdf
```

---

## Monthly Tasks (1st of Month 8 AM)

### Rank Tracking Report

```yaml
task: monthly-rank-report
schedule: "0 8 1 * *"
enabled: true
actions:
  - check_all_keyword_rankings
  - calculate_ranking_changes
  - analyze_trends
  - generate_trend_report
  - send_report
```

**What happens:**
1. Checks rankings for all tracked keywords
2. Compares to previous month
3. Calculates visibility score
4. Identifies winning/losing keywords
5. Generates comprehensive report

**Report includes:**
- Current position for each keyword
- Position change (+/- positions)
- Visibility trend graph
- Top 3 opportunities
- Keywords losing ground

**Configuration:**
```bash
# Add keywords to track
google-business-optimizer rank-track --add "keyword here"

# Set report schedule
google-business-optimizer config --rank-report-day=1
```

---

## Heartbeat State Tracking

The skill maintains state in `~/.openclaw/skills/google-business-optimizer/state.json`:

```json
{
  "lastHeartbeat": 1704067200,
  "tasks": {
    "daily-review-check": {
      "lastRun": "2024-01-01T06:00:00Z",
      "reviewsChecked": 150,
      "responsesSent": 12,
      "errors": 0
    },
    "weekly-competitor-report": {
      "lastRun": "2023-12-25T09:00:00Z",
      "competitorsAnalyzed": 5,
      "reportSent": true
    },
    "monthly-rank-report": {
      "lastRun": "2023-12-01T08:00:00Z",
      "keywordsChecked": 20,
      "reportSent": true
    }
  }
}
```

---

## Manual Trigger

You can manually trigger any heartbeat task:

```bash
# Run daily review check now
google-business-optimizer heartbeat --task=daily-review-check

# Run weekly competitor report
google-business-optimizer heartbeat --task=weekly-competitor-report

# Run monthly rank report
google-business-optimizer heartbeat --task=monthly-rank-report

# Run all enabled tasks
google-business-optimizer heartbeat --run-all
```

---

## Disabling Automation

To disable specific automation tasks:

```bash
# Disable auto-responses
google-business-optimizer config --auto-respond=false

# Disable weekly reports
google-business-optimizer config --weekly-reports=false

# Disable monthly reports
google-business-optimizer config --monthly-reports=false

# Disable all automation
google-business-optimizer config --heartbeat-enabled=false
```

---

## Notifications

Configure where alerts and reports are sent:

### Slack
```bash
google-business-optimizer config --slack-webhook=https://hooks.slack.com/...
```

### Email
```bash
google-business-optimizer config --email-to=owner@business.com
google-business-optimizer config --email-from=noreply@yourdomain.com
```

### Discord
```bash
google-business-optimizer config --discord-webhook=https://discord.com/api/webhooks/...
```

---

## Error Handling

If a heartbeat task fails:

1. Error is logged to `~/.openclaw/skills/google-business-optimizer/error.log`
2. Notification sent to configured channel (if set)
3. Task is retried on next heartbeat (max 3 retries)
4. After 3 failures, task is disabled until manually re-enabled

**Check error log:**
```bash
google-business-optimizer logs --errors
```

---

## Performance Considerations

- **API Rate Limits**: Respects Google Business Profile API quotas
- **Batch Processing**: Groups API calls to minimize quota usage
- **Caching**: Caches competitor/rank data for 6 hours
- **Retry Logic**: Exponential backoff on API failures

---

## Custom Scheduling

Advanced users can customize the schedule:

```bash
# Custom daily schedule (every 4 hours)
google-business-optimizer config --daily-schedule="0 */4 * * *"

# Custom weekly schedule (Fridays at 5 PM)
google-business-optimizer config --weekly-schedule="0 17 * * 5"

# Custom monthly schedule (15th at 10 AM)
google-business-optimizer config --monthly-schedule="0 10 15 * *"
```

Cron format: `minute hour day month weekday`

---

## Monitoring

Check automation health:

```bash
# View last run times
google-business-optimizer status

# View automation settings
google-business-optimizer config --show

# Test notifications
google-business-optimizer heartbeat --test-notify
```
