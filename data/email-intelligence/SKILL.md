---
name: email-intelligence
description: "Analyze email inbox health with weather metaphors, spam/signal classification, email debt scoring, and ghost detection. Use when user asks about inbox status, email overwhelm, who they're ghosting, or email time cost. Requires himalaya CLI configured with IMAP."
---

# Email Intelligence

Analyze your email inbox health using creative weather metaphors, intelligent classification, debt scoring, and ghost detection. Transform overwhelming inbox analysis into clear, actionable insights.

## When to Use

Use this skill when the user asks about:
- Inbox status or health
- Email overwhelm or management
- Who they're "ghosting" (ignoring responses to)
- Time cost of processing their inbox
- Signal vs noise in their email
- Email debt or backlog

## Requirements

- **himalaya CLI** configured with IMAP access
- Python 3.6+
- The configured email account should have standard folder names (INBOX, Archive)

## Quick Usage

```bash
# Basic analysis (last 7 days)
python3 scripts/email_classify.py

# Extended analysis (last 14 days)
python3 scripts/email_classify.py --days 14

# JSON output for integration
python3 scripts/email_classify.py --format json
```

## Weather System

The inbox "weather" is determined by the number of human emails in your INBOX that need responses:

- **🌊 Calm Seas** (0-2): Inbox is peaceful and manageable
- **🍃 Light Breeze** (3-5): A few emails need attention, nothing urgent
- **🌬️ Choppy Waters** (6-10): Multiple emails require responses  
- **⛵ Small Craft Advisory** (11-20): Many people waiting for replies
- **⛈️ Storm Warning** (21+): Inbox is overwhelming, needs immediate attention

## Email Classification

Emails are automatically classified into four categories:

### 🤖 Automated
- Sender contains: noreply, no-reply, donotreply, notifications@, alerts@
- Subject contains: unsubscribe, automatic, auto-generated
- Time cost: 0 minutes (can be safely ignored)

### 📰 Newsletter
- From domains: substack.com, email.*, marketing.*, updates@
- Subject contains: newsletter, digest, weekly, monthly, roundup
- Time cost: 1 minute each (skim or archive)

### 🔔 Notification  
- From services: github, slack, jira, linear, aws, google, microsoft, etc.
- Time cost: 30 seconds each (quick action/acknowledgment)

### 👥 Human
- Everything else (actual people writing)
- Time cost: 3 minutes each (requires thoughtful response)

## Metrics Explained

### Email Debt Score (0-100)
Calculated based on unseen human emails in your INBOX, weighted by age:
- < 1 day old: 1 point each
- 1-3 days old: 3 points each  
- 3-7 days old: 5 points each
- 7+ days old: 10 points each

**Score meanings:**
- 0-30: 🟢 Great job! Inbox under control
- 31-60: 🟡 Getting busy. Consider tackling some replies
- 61-100: 🔴 High debt! Many emails waiting for responses

### Signal-to-Noise Ratio
Percentage of emails that are from humans (signal) vs automated/newsletter/notification (noise).

Higher ratio = more meaningful email, less spam/clutter.

### Ghost Report
Shows up to 5 people you're "ghosting" (human emails you haven't read), sorted by how long they've been waiting. Helps prioritize who needs responses most urgently.

### Time Investment
Estimates how much time you'll need to process your current inbox based on email types and their typical processing times.

## Output Formats

### Text Format (Default)
Human-readable report with weather, debt score, signal/noise analysis, ghost report, and time estimates. Perfect for quick status updates or daily reviews.

### JSON Format
Structured data for integration with other tools, APIs, or dashboards:

```json
{
  "weather": {
    "level": "breeze",
    "emoji": "🍃", 
    "description": "Light Breeze - A few emails need attention...",
    "humanCount": 4
  },
  "categories": {
    "automated": 15,
    "newsletter": 8,
    "notification": 12,
    "human": 4
  },
  "debtScore": 18,
  "ghostReport": [...],
  "signalNoiseRatio": {
    "ratio": 0.103,
    "percentage": "10%"
  },
  "timeCost": {
    "minutes": 18,
    "formatted": "18 minutes"
  }
}
```

## Integration Tips

### Dashboard Integration
The JSON output is designed for easy integration into dashboards or status displays. The weather metaphor makes it intuitive for users to understand their inbox state at a glance.

### Automation
Run periodically (via cron) to track inbox health trends over time. The debt score is particularly useful for identifying when inbox maintenance is needed.

### Alerts
Set up alerts when:
- Weather reaches "Storm Warning" level
- Debt score exceeds 60
- Ghost report shows people waiting >5 days

## Troubleshooting

### No emails found
- Verify himalaya CLI is configured: `himalaya envelope list -f INBOX --page-size 1`
- Check folder names match your email provider (some use "Inbox" vs "INBOX")

### Classification seems wrong
The classification uses heuristics based on sender patterns and subject lines. You can modify the patterns in the script for your specific needs.

### Slow performance
- Reduce the `--days` parameter to analyze fewer emails
- The script fetches up to 200 emails from Archive - adjust `page_size` in the code if needed

## Philosophy

Email Intelligence treats your inbox as a living system with its own weather patterns and health metrics. Rather than just counting unread emails, it helps you understand:

- What actually needs your attention (humans vs bots)
- How "behind" you are (debt score)  
- Who you might be accidentally ignoring (ghost report)
- How much time you're really looking at (time cost)

The weather metaphor makes inbox status intuitive and actionable - you know to "batten down the hatches" when a storm is brewing, but you can relax when the seas are calm.

Use this skill to transform inbox anxiety into clear, prioritized action plans.