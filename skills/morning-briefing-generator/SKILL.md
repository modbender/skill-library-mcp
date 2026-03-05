# Morning Briefing Generator

**Version:** 1.0
**Price:** $15
**Category:** Productivity
**Est. Revenue:** $300-1,000/month

---

## What It Does

Generates personalized morning briefings with:
- Weather forecast for your location
- Today's calendar events
- Tomorrow's calendar preview
- Urgent emails from last 12 hours
- Trending topics in your areas of interest
- Health metrics (if connected)
- News highlights
- Daily priorities from task manager

Saves 30+ minutes every morning.

---

## Use Cases

- **Executives** - Start day informed without checking 5 apps
- **Sales professionals** - Know today's meetings and follow-ups
- **Freelancers** - Track client calls and deadlines
- **Content creators** - See trending topics to cover
- **Anyone** - who wants a productive morning routine

---

## How to Use

### Basic Briefing
```
Generate my morning briefing for [CITY]
```

### Detailed Briefing
```
Create my morning briefing including:
- Weather for San Francisco
- My Google Calendar events for today and tomorrow
- Urgent emails from the last 12 hours
- Top 5 trending topics in AI and tech
- My high-priority Asana tasks
```

### Automated Daily Briefing (Cron)
```
Create a cron job that runs every weekday at 7am.
Generate my morning briefing and send it via Telegram.
```

---

## Configuration

Add to `TOOLS.md` or `HEARTBEAT.md`:

```markdown
## Morning Briefing Preferences

- Location: San Francisco, CA
- Calendar: work@company.com, personal@gmail.com
- Interests: AI, tech, startups, cryptocurrency
- Task Manager: Asana (workspace: "My Company")
- Email Accounts: work@company.com, personal@gmail.com
- Delivery: Telegram at 7am weekdays
- Additional: Include Oura Ring sleep score if below 70%
```

---

## Example Output

```
🌅 Morning Briefing - Monday, Feb 13, 2026

📍 San Francisco, CA
☀️ Partly Cloudy, 58°F → 67°F
☔ 10% chance of rain

📅 TODAY'S SCHEDULE
• 9:00 AM - Team standup (30 min)
• 11:00 AM - Client call: Acme Corp (1 hr)
• 2:00 PM - Product review (45 min)
• 4:30 PM - 1:1 with Sarah (30 min)

📅 TOMORROW PREVIEW
• 10:00 AM - Investor update call
• 3:00 PM - Design review

📧 URGENT EMAILS (2)
• From: boss@company.com - "Q1 targets due Friday"
• From: client@acme.com - "Can we reschedule?"

🔥 TRENDING IN AI/TECH
• OpenAI announces GPT-5
• Apple Vision Pro sales exceed expectations
• New Claude model released
• AI regulation updates in EU
• Startup funding trends

✅ PRIORITY TASKS
• [ ] Finalize Q1 presentation
• [ ] Review contractor invoices
• [ ] Send proposal to Acme Corp

😴 SLEEP SCORE: 72/100
Feeling rested. Good day for deep work.

---
Briefing generated at 7:00 AM PST
```

---

## Integration Options

### Weather
- Built-in weather skill (no API key needed)
- Or specify: "Use OpenWeatherMap with my API key"

### Calendar
- Google Calendar (OAuth)
- Apple Calendar
- Outlook
- Any iCal feed

### Email
- Gmail (OAuth)
- Multiple accounts supported

### Task Manager
- Asana
- Todoist
- Notion
- Linear
- GitHub Issues

### Delivery
- Telegram (recommended)
- WhatsApp
- Slack
- Email

---

## Advanced Features

### Smart Prioritization
```
Include only calendar events tagged "important" or "client-facing"
```

### Custom Time Ranges
```
Show me calendar events for the next 3 days, not just today/tomorrow
```

### Filtered News
```
Only show trending topics related to: SaaS, B2B, enterprise software
```

### Conditional Logic
```
If my Oura readiness score is below 70, suggest rescheduling intense meetings
```

### Team Briefings
```
Generate a team briefing with everyone's meetings and shared tasks
```

---

## Sample Prompts

### For Executives
```
Generate my executive morning briefing:
- Weather for New York
- Today's meetings (board, investors, leadership)
- Urgent emails from executives only
- Market summary for my watchlist: AAPL, MSFT, GOOGL
- Top business news
```

### For Sales
```
Create my sales morning briefing:
- Client meetings today
- Follow-ups due
- New leads from overnight
- Industry news in my vertical
```

### For Creators
```
Generate my creator morning briefing:
- Today's content schedule
- Trending topics in my niche
- New comments/DMs to respond to
- Platform algorithm updates
```

---

## Troubleshooting

**"No calendar events showing"**
- Check calendar permissions
- Verify calendar IDs in TOOLS.md
- Test: "Show me my calendar for today"

**"Weather shows wrong location"**
- Update location in TOOLS.md
- Or specify in prompt: "Weather for [exact city]"

**"Not receiving Telegram messages"**
- Verify bot token in .env
- Test: "Send me a test message via Telegram"

**"Emails not loading"**
- Re-authenticate email account
- Check OAuth tokens haven't expired

---

## Pricing & Value

**Cost:** $15 one-time
**Time Saved:** 30+ minutes every morning
**Value:** At $100/hour, saves $50/day = $1,500/month
**ROI:** 10,000%+ in first month

---

## Installation

1. Install skill from ClawHub
2. Configure preferences in TOOLS.md
3. Set up cron job for automation
4. Or use manually: "Generate my morning briefing"

---

## Support

- ClawHub community Discord
- Email: [support email]
- Documentation: docs.openclaw.ai

---

**Created by Vernox**
**Part of the Productivity Suite**
