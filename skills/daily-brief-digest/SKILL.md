---
name: daily-digest
description: Generates a daily brief including urgent emails (himalaya), upcoming calendar events (gog), and relevant news. Use when the user asks for a morning summary, daily briefing, or a status update on their day.
---

# Daily Digest

This skill provides a structured way to get a quick overview of your day. It relies on locally configured tools (`himalaya` for email and `gog` for calendar) and does not store any personal credentials within the skill itself.

## Workflow

1.  **Email Triage**: Use `himalaya --output json envelope list --page-size 20` to get recent emails. Identify urgent items needing attention.
2.  **Calendar & Task Sync**: Use `gog calendar events [calendarId] --from [today_start] --to [today_end]` to fetch today's schedule. Also check for due tasks using `gog` tasks/contacts or specific list commands if available.
3.  **News Retrieval**: Use `web_fetch` or `browser` to find the top 3-5 news stories of the day.
4.  **Log & Present**: Use `scripts/digest.js` to assemble these components into a stylized HTML report. **CRITICAL: The script automatically saves this report as a permanent Markdown file in `.openclaw/cron/DailyDigest_logs/[date].md` for historical record.**
5.  **Notify User**: Send a brief notification via the `message` tool to the user's active channel. Mention that the full detailed log is available at `.openclaw/cron/DailyDigest_logs/[date].md`.

## Data Sources

- **Email**: `himalaya` CLI.
- **Calendar**: `gog` CLI.
- **News**: Web search or trusted RSS feeds.
- **Logs**: Saved locally to `~/.openclaw/cron/DailyDigest_logs/`.

## Example Output

**📅 Daily Briefing - 2026-02-12**

**📧 Emails (Recent)**
- **Google**: Security alert (04:10)
- **The Replit Team**: Unlock Replit Agent's Full Potential (Feb 11)

**🗓️ Calendar**
- 10:30 AM: Workout (Shoulder)
- 02:00 PM: Project Review

**📰 News**
- [Top news item 1]
- [Top news item 2]
