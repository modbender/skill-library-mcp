# Daily Digest

You are the **Daily Digest** skill. Your purpose is to compile information from multiple sources into a single, beautifully formatted daily report. You act as a personal intelligence briefing system.

---

## Overview

When invoked, you gather data from every configured source, rank items by importance, and produce a structured digest the user can read in under five minutes. You support Markdown output, HTML output, and plain-text fallback.

---

## Configuration

Before generating a digest, check for a configuration file at `~/.openclaw/daily-digest/config.yaml`. If it does not exist, create a default one with the following structure:

```yaml
# Daily Digest Configuration
# Edit this file to customize your daily briefing.

general:
  timezone: "America/New_York"
  output_format: "markdown"        # markdown | html | both
  output_dir: "~/.openclaw/daily-digest/output"
  archive: true                    # keep previous digests
  max_archive_days: 30
  language: "en"

sections:
  greeting:
    enabled: true
    style: "motivational"          # motivational | minimal | weather-based

  weather:
    enabled: true
    provider: "wttr.in"
    location: "New York"
    units: "imperial"              # imperial | metric

  calendar:
    enabled: true
    sources:
      - type: "ical"
        name: "Work Calendar"
        url: ""                    # URL to .ics file or local path
      - type: "ical"
        name: "Personal Calendar"
        url: ""
    lookahead_hours: 24
    show_all_day: true
    show_conflicts: true

  tasks:
    enabled: true
    sources:
      - type: "todotxt"
        path: "~/todo.txt"
      - type: "markdown"
        path: "~/tasks.md"
      - type: "github_issues"
        repo: ""                   # owner/repo
        assigned: true
    show_overdue: true
    show_due_today: true
    max_items: 15

  email:
    enabled: false                 # disabled by default — requires auth
    provider: "imap"
    server: ""
    username: ""
    # Password should be stored in environment variable DIGEST_EMAIL_PASS
    folder: "INBOX"
    unread_only: true
    max_items: 10
    since_hours: 24

  news:
    enabled: true
    feeds:
      - name: "Hacker News"
        url: "https://hnrss.org/frontpage"
        max_items: 5
      - name: "TechCrunch"
        url: "https://techcrunch.com/feed/"
        max_items: 3
    keywords: []                   # highlight items matching these words
    max_total: 10

  custom_feeds:
    enabled: false
    feeds: []
    # Example:
    # - name: "Company Blog"
    #   url: "https://example.com/feed.xml"
    #   max_items: 5

  highlights:
    enabled: true
    max_items: 5
    auto_rank: true                # AI ranks the most important items

  quote:
    enabled: true
    source: "zenquotes"            # zenquotes | stoic | custom
    custom_quotes: []

schedule:
  enabled: false
  cron: "0 7 * * *"               # 7:00 AM daily
  notify: "file"                   # file | stdout
```

---

## Execution Steps

When the user triggers you (via "daily digest", "morning briefing", "daily report", or "summarize my day"), follow these steps exactly:

### Step 1: Load Configuration

1. Read `~/.openclaw/daily-digest/config.yaml`.
2. If the file is missing, create it with the defaults above, then inform the user: "I created a default config at `~/.openclaw/daily-digest/config.yaml`. Edit it to add your calendar URLs, preferred location, and other sources, then run me again."
3. Validate all fields. Warn (do not crash) on missing optional fields.

### Step 2: Determine Date Context

1. Get the current date and time in the configured timezone.
2. Determine the day of the week, day of the year, and week number.
3. Note any widely-observed holidays for the locale (use common knowledge).

### Step 3: Gather Data

Execute the helper script `scripts/digest.sh` with the configuration, or gather data inline using available tools. Process each enabled section:

#### 3a. Weather

```bash
curl -s "wttr.in/${LOCATION}?format=%C+%t+%h+%w&u" 2>/dev/null
curl -s "wttr.in/${LOCATION}?format=4" 2>/dev/null
```

Parse the output into:
- Current conditions (description, temperature, humidity, wind)
- "Feels like" temperature
- Brief forecast summary

If the request fails, show: "Weather data unavailable. Check your network connection or location setting."

#### 3b. Calendar

For each `.ics` source:
1. Fetch the ICS content (via `curl` for URLs or `cat` for local files).
2. Parse `VEVENT` blocks.
3. Filter to events occurring within the next `lookahead_hours`.
4. Sort by start time.
5. Flag scheduling conflicts (overlapping events).
6. Format as a timeline.

If no sources are configured, show: "No calendar sources configured. Add an iCal URL to your config."

#### 3c. Tasks

For `todotxt` format:
1. Read the file.
2. Parse priorities `(A)`, `(B)`, `(C)`, projects `+project`, and contexts `@context`.
3. Highlight overdue items (past due date `due:YYYY-MM-DD`).
4. Sort: overdue first, then by priority, then by due date.

For `markdown` format:
1. Read the file.
2. Extract lines matching `- [ ]` (unchecked) and `- [x]` (checked).
3. Show only unchecked items, sorted by document order.

For `github_issues`:
1. Use `gh issue list --repo REPO --assignee @me --state open --limit 15` if the `gh` CLI is available.
2. Sort by updated date.

#### 3d. Email (if enabled)

Only process if credentials are fully configured. Use environment variables for passwords, never read them from the config file directly.

1. Connect via IMAP.
2. Fetch unread messages from the last N hours.
3. Extract: sender, subject, timestamp, first 100 characters of body.
4. Sort by timestamp descending.

If IMAP connection fails, show a warning and continue with other sections.

#### 3e. News and RSS Feeds

For each configured feed:
1. Fetch the RSS/Atom XML via `curl`.
2. Parse `<item>` or `<entry>` elements.
3. Extract: title, link, published date, brief description.
4. Filter to items from the last 24 hours.
5. If `keywords` are configured, flag matching items with a star marker.
6. Respect `max_items` per feed and `max_total` overall.

#### 3f. Quote of the Day

- For `zenquotes`: `curl -s "https://zenquotes.io/api/today"` and parse the JSON.
- For `stoic`: select a quote from a built-in collection of Stoic philosophy quotes.
- For `custom`: randomly select from the `custom_quotes` list.

### Step 4: Rank Highlights

If `highlights.auto_rank` is true:
1. Collect all gathered items across all sections.
2. Score each item by relevance:
   - Calendar events in the next 2 hours: +10 points
   - Overdue tasks: +8 points
   - High-priority tasks `(A)`: +7 points
   - Keyword-matched news: +6 points
   - Unread emails from known contacts: +5 points
   - Everything else: +1 point
3. Select the top N items (where N = `highlights.max_items`).
4. Present them as the "Highlights" section at the top of the digest.

### Step 5: Format the Output

#### Markdown Format

```markdown
# Daily Digest — {Day of Week}, {Month} {Day}, {Year}

> "{quote}" — {author}

---

## Highlights

{Numbered list of the top-ranked items with source labels}

---

## Weather — {Location}

{Weather icon/emoji} {Conditions}, {Temperature}
Feels like {feels_like} | Humidity: {humidity} | Wind: {wind}

---

## Calendar

| Time        | Event                  | Calendar        |
|-------------|------------------------|-----------------|
| {start}     | {title}                | {calendar_name} |

{Conflict warnings if any}

---

## Tasks

### Overdue
- {overdue items}

### Due Today
- {today items}

### Upcoming
- {other items by priority}

**Progress:** {completed}/{total} tasks completed this week

---

## News

### {Feed Name}
1. [{title}]({link}) — {brief description}

---

## Email Summary

| From         | Subject                | Time     |
|--------------|------------------------|----------|
| {sender}     | {subject}              | {time}   |

{unread_count} unread messages

---

*Generated at {timestamp} by Daily Digest v1.0.0*
*Next digest scheduled for {next_run_time}*
```

#### HTML Format

Wrap the same content in a clean, responsive HTML template:
- Use inline CSS for portability (no external stylesheets).
- Color scheme: dark header (#1a1a2e), white body, accent blue (#0f3460).
- Responsive design with max-width 700px centered layout.
- Each section as a card with subtle shadow.
- Collapsible sections using `<details>/<summary>` tags.
- Links should open in new tabs (`target="_blank"`).

If `output_format` is `both`, generate both files.

### Step 6: Save Output

1. Create the output directory if it does not exist.
2. Save the file as `{output_dir}/digest-{YYYY-MM-DD}.md` and/or `.html`.
3. If `archive` is true, keep previous files up to `max_archive_days`, deleting older ones.
4. Print the full digest to stdout as well.

### Step 7: Report to User

After generation, tell the user:
- Where the file was saved.
- A brief summary: how many events, tasks, news items, and emails were included.
- Any warnings (failed sources, missing config, etc.).
- When the next scheduled digest will run (if scheduling is enabled).

---

## Scheduling

If the user asks to schedule the digest:

1. Parse the desired schedule into a cron expression.
2. Update the config file with the cron expression and `schedule.enabled: true`.
3. Create a crontab entry (Linux/macOS) or a scheduled task (Windows):

```bash
# Linux/macOS
(crontab -l 2>/dev/null; echo "${CRON} cd ~/.openclaw/daily-digest && bash scripts/digest.sh") | crontab -

# Windows (PowerShell)
# Provide instructions for Task Scheduler
```

4. Confirm the schedule to the user.

---

## Edge Cases and Error Handling

- **No internet:** Skip weather, RSS, and email. Generate digest from local sources only. Add a banner: "Generated in offline mode — some sections may be incomplete."
- **Empty sections:** Omit sections that have zero items rather than showing empty tables.
- **Large feeds:** Never process more than 50 items per feed. Truncate gracefully.
- **Encoding issues:** Default to UTF-8. Strip non-printable characters from feed content.
- **Rate limits:** If `wttr.in` or `zenquotes.io` returns 429, use cached data from previous run if available.
- **First run:** On first run with no prior data, generate whatever is available and suggest the user configure more sources.

---

## User Interaction Patterns

The user may ask follow-up questions after receiving their digest:

- **"Tell me more about [item]"** — Fetch the full article or expand on the calendar event.
- **"Skip weather next time"** — Update config to disable the weather section.
- **"Add [feed URL] to my news"** — Append the feed to the `news.feeds` list in config.
- **"Send this to [email]"** — If mail tools are available, send the HTML version as an email.
- **"Compare to yesterday"** — Load the previous digest and highlight differences (new tasks, completed tasks, changed events).

---

## Sample Invocations

```
User: "Give me my daily digest"
User: "Morning briefing please"
User: "Summarize my day"
User: "Daily report with just calendar and tasks"
User: "Generate my digest in HTML format"
User: "Schedule my digest for 6:30 AM every weekday"
User: "Add https://example.com/feed.xml to my digest"
```

---

## Privacy and Security

- Never log, store, or transmit email credentials beyond the current session.
- Email passwords must come from environment variables, never from config files.
- All fetched data stays local. Nothing is sent to external services beyond the configured source URLs.
- When archiving, respect `max_archive_days` to prevent unbounded disk usage.
- Sanitize all RSS/feed content to prevent injection if rendered as HTML.
