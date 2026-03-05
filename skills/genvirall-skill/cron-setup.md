# Cron Setup for Genviral Skill

Automate the content pipeline with OpenClaw cron jobs. These run your agent on a schedule so content gets generated, posted, and reviewed without manual intervention.

## Recommended Schedule

| Job | Frequency | What it does |
|-----|-----------|-------------|
| **Daily Content** | Every day at 9:00 AM | Generate, render, review, and post a slideshow |
| **Performance Check** | Every day at 6:00 PM | Check post analytics, log metrics for recent posts |
| **Weekly Review** | Every Sunday at 10:00 AM | Analyze the week's performance, update strategy weights, retire bad hooks |

## Setup

Replace `YOUR_TIMEZONE` with your timezone (e.g. `Europe/Brussels`, `America/New_York`).

### 1. Daily Content Generation

```bash
openclaw cron add \
  --name "Genviral: Daily Content" \
  --cron "0 9 * * *" \
  --tz "YOUR_TIMEZONE" \
  --session isolated \
  --message "Run the Genviral daily content pipeline. Read the genviral SKILL.md, then: 1) Pick a topic from content/scratchpad.md or generate a new one based on performance/insights.md. 2) Generate a slideshow with a strong hook. 3) Render all slides. 4) Review each slide visually. If any slide is below quality, regenerate it. 5) Post to the default account. 6) Log the post in performance/log.json. Use the hooks that have the highest weights in hooks/library.json." \
  --announce
```

### 2. Daily Performance Check

```bash
openclaw cron add \
  --name "Genviral: Performance Check" \
  --cron "0 18 * * *" \
  --tz "YOUR_TIMEZONE" \
  --session isolated \
  --message "Run the Genviral performance check. Read the genviral SKILL.md, then: 1) Run analytics-summary to get overall stats. 2) Run analytics-posts to get individual post metrics. 3) Update performance/log.json with latest metrics for posts older than 24h. 4) If any post significantly outperformed or underperformed, note why in performance/insights.md. 5) Report a brief summary of today's content performance." \
  --announce
```

### 3. Weekly Strategy Review

```bash
openclaw cron add \
  --name "Genviral: Weekly Review" \
  --cron "0 10 * * 0" \
  --tz "YOUR_TIMEZONE" \
  --session isolated \
  --message "Run the Genviral weekly review. Read the genviral SKILL.md, then: 1) Analyze all posts from the past 7 days in performance/log.json. 2) Identify top 3 and bottom 3 performers. 3) Update hook weights in hooks/library.json (increase weight for hooks that drove high engagement, decrease for underperformers). 4) Update performance/insights.md with this week's learnings. 5) Generate 5 new content ideas for next week in content/scratchpad.md based on what worked. 6) Write the weekly review in performance/weekly-review.md." \
  --announce
```

## Customization

**Posting frequency**: Want 2 posts per day? Change the daily cron to `0 9,15 * * *` (9 AM and 3 PM).

**Platform targeting**: Add platform-specific instructions to the message, e.g. "Post to TikTok with vertical format" or "Post to Instagram with 4:5 aspect ratio."

**Content themes**: Add a theme schedule to `content/calendar.json` and reference it in the daily content message.

## Verify Setup

```bash
# List all cron jobs
openclaw cron list

# Test a job manually
openclaw cron run <job-id> --force

# Check run history
openclaw cron runs --id <job-id>
```

## Without OpenClaw

If you're using the skill outside OpenClaw, you can set up system cron jobs that call your agent with the same prompts, or integrate the `genviral.sh` commands into any automation tool.
