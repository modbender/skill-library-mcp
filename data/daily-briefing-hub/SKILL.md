---
name: daily-briefing-hub
description: >
  All-in-one daily briefing that combines Google Calendar events, Gmail/Outlook email highlights,
  weather forecast, GitHub PR and CI status, Hacker News and RSS feeds, and Todoist/ClickUp/Linear
  tasks into a single prioritized morning summary delivered via Telegram, Slack, WhatsApp, or Discord.
  Use this skill for: morning briefing, daily digest, daily summary, daily standup prep, "what's on
  my plate today", "brief me", "what did I miss", end-of-day recap, personalized news digest, schedule
  overview, inbox summary, daily notification, recurring morning update via cron, or any request to
  see a combined overview of calendar plus email plus tasks plus news. This is your AI chief of staff
  that replaces checking 6 apps every morning. Works with whatever tools you have configured — skips
  what's missing, uses what's available.
metadata:
  openclaw:
    emoji: "☀️"
---

# Daily Briefing Hub

Your AI Chief of Staff. This skill pulls data from multiple sources and generates a single, prioritized daily briefing — delivered however the user wants it.

## Why This Exists

Most OpenClaw users end up building their own morning briefing by manually calling 5-8 separate tools. This skill does it in one step: gather everything, prioritize it, format it beautifully, and deliver it.

## How It Works

When triggered, gather data from whichever sources the user has available, then compose a structured briefing. Not every source needs to be configured — the skill gracefully skips unavailable sources and works with whatever is connected.

## Data Sources

Attempt to pull from these sources in order. If a source is unavailable (tool not enabled, API not configured), skip it silently and move on. Never fail because one source is missing.

### 1. Calendar (High Priority)
Use the `gog` tool or Google Calendar CLI to fetch today's events.
- Show: event name, time, location, attendees (if available)
- Flag conflicts (overlapping events)
- Note gaps longer than 2 hours as "focus time" opportunities
- If tomorrow's first event is early, mention it as a heads-up

### 2. Email (High Priority)
Use Gmail via `gog` or the configured email tool to scan recent unread messages.
- Summarize the top 5-10 most important unread emails (skip newsletters, promotions)
- Prioritize: emails from known contacts > emails with urgent keywords > everything else
- For each: sender, subject, one-line summary, suggested action (reply/read/archive)
- Count total unread and note if inbox is getting out of control (>50 unread = flag it)

### 3. Weather (Medium Priority)
Use `curl` to fetch weather from a public API, or use an installed weather skill.
- If user location is known (from memory or config), fetch automatically
- If not, ask once and remember for future briefings
- Show: current temp, high/low, conditions, rain probability
- Only mention weather if it's notable (rain, extreme temps, storms) — skip "sunny and 72°F"
- Suggest: "bring an umbrella" or "dress warm" when relevant

### 4. GitHub / Dev Activity (Medium Priority — skip for non-developers)
Use the GitHub CLI (`gh`) or GitHub skill to check activity.
- Open PRs awaiting your review (with age: "PR #142 waiting 3 days")
- PRs you authored that have new reviews or comments
- CI/CD failures on your repos in the last 24 hours
- New issues assigned to you
- Skip this section entirely if the user doesn't have GitHub configured

### 5. Tasks (Medium Priority)
Check configured task managers: Todoist, ClickUp, Linear, GitHub Issues, or local task files.
- Show tasks due today and overdue tasks
- Group by project/label if available
- Flag overdue items prominently

### 6. News & Feeds (Low Priority)
Use web_search or RSS feeds to pull relevant headlines.
- If the user has specified interests (in memory or config), filter for those topics
- Default: top 3-5 tech/business headlines from the last 24 hours
- Keep summaries to one sentence each
- Hacker News top 3 stories (if user is a developer)

## Briefing Format

ALWAYS structure the briefing like this. Adapt sections based on available data:

```
☀️ Good [morning/afternoon], [Name]! Here's your briefing for [Day, Date].

📅 TODAY'S SCHEDULE
[Calendar events in chronological order]
[Flag any conflicts or notable gaps]

📧 EMAIL HIGHLIGHTS
[Top priority emails with one-line summaries]
[Total unread count]

⚡ ACTION ITEMS
[Overdue tasks — URGENT]
[Tasks due today]
[PRs needing your review]

🌤️ WEATHER
[Only if notable — rain, extreme temps, etc.]

💻 DEV ACTIVITY
[CI failures, new issues, PR updates]

📰 NEWS
[3-5 relevant headlines, one line each]

---
Have a great day! Reply with any item number to dive deeper.
```

## Prioritization Logic

The briefing should feel like a smart assistant, not a data dump. Apply these rules:

1. **Urgent items surface first**: overdue tasks, meeting in <1 hour, CI failures, emails from boss/clients
2. **Combine related items**: if there's a meeting about a PR, mention them together
3. **Be concise by default**: one line per item. The user can ask to expand any section
4. **Skip empty sections**: don't show "No new emails" — just omit the section
5. **Time-aware**: morning briefings focus on today. Evening briefings ("what did I miss") focus on what happened today

## Setting Up Recurring Briefings

If the user asks to "send me a briefing every morning" or "set up a daily digest":

1. Help them configure a cron job via OpenClaw's cron system
2. Suggested schedule: weekdays at 7:00 AM local time (ask user preference)
3. Deliver via their preferred channel (Telegram, Slack, WhatsApp, Discord)
4. Store the briefing configuration in the workspace for persistence

Example cron setup:
```json
{
  "schedule": "0 7 * * 1-5",
  "prompt": "Generate my daily briefing and send it to me",
  "channel": "telegram"
}
```

## Customization

The user can customize their briefing at any time:

- "Add RSS feeds to my briefing" → ask for feed URLs, store in memory
- "Skip weather in my briefings" → remember this preference
- "I want briefings at 6 AM" → update cron schedule
- "Focus on GitHub and email only" → disable other sections
- "Add Stripe revenue to my briefing" → extend with financial data source

Store all preferences in OpenClaw's memory system so they persist across sessions.

## Edge Cases

- **First run**: If this is the first briefing, explain what you're doing and ask about preferences rather than generating a sparse briefing with no data
- **Weekend briefings**: lighter tone, skip work email/GitHub, focus on personal calendar and weather
- **Evening trigger**: if user asks for briefing after 5 PM, shift to "end of day recap" — what happened today, what's tomorrow
- **No data at all**: if literally no tools are configured, help the user set up at least calendar + email before generating a briefing
- **Multiple calendars**: if user has personal + work calendars, show both but label them clearly

## Example Interactions

**User**: "Brief me"
→ Generate full briefing with all available sources

**User**: "What's on my plate today?"
→ Focus on calendar + tasks, lighter on news

**User**: "Set up a daily morning briefing on Telegram at 7 AM"
→ Configure cron job, confirm channel, generate a test briefing

**User**: "What did I miss today?"
→ Evening recap: summarize the day's emails, completed tasks, GitHub activity

**User**: "Add Hacker News to my daily briefing"
→ Store preference, confirm, show preview of how it'll look
