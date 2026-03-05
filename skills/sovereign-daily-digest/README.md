# Daily Digest

**Generate beautiful daily digest reports from multiple sources.**

Compile your calendar, tasks, emails, news feeds, weather, and more into a single, readable briefing you can scan in under five minutes.

---

## Features

- **Multi-source aggregation** -- Calendar (iCal), tasks (todo.txt, Markdown, GitHub Issues), RSS/Atom feeds, weather, and email
- **Smart highlights** -- AI-ranked "most important" items bubbled to the top
- **Dual output** -- Markdown and/or HTML with a clean, responsive design
- **Configurable sections** -- Enable only what you need; disable the rest
- **Scheduling** -- Set it up with cron for automatic daily delivery
- **Offline resilient** -- Falls back gracefully when network sources are unavailable
- **Privacy-first** -- All data stays local; email passwords read only from environment variables

---

## Screenshots

> Screenshots will be added after the first public release.

```
+---------------------------------------------------+
|              DAILY DIGEST                          |
|              Friday, February 21, 2026             |
+---------------------------------------------------+
|                                                    |
|  > "The happiness of your life depends upon the   |
|    quality of your thoughts." -- Marcus Aurelius   |
|                                                    |
|  ## Highlights                                     |
|  1. Team standup in 30 minutes (Calendar)          |
|  2. OVERDUE: Submit tax documents (Tasks)          |
|  3. OpenAI announces GPT-5 (Hacker News)          |
|                                                    |
|  ## Weather -- New York                            |
|  Partly cloudy | 42F | Humidity: 65% | Wind: 8mph |
|                                                    |
|  ## Calendar                                       |
|  09:00  Team standup         Work Calendar         |
|  11:00  Product review       Work Calendar         |
|  14:30  Dentist appointment  Personal              |
|                                                    |
|  ## Tasks                                          |
|  ### Overdue                                       |
|  - (A) Submit tax documents due:2026-02-18         |
|  ### Due Today                                     |
|  - (B) Review PR #342 due:2026-02-21              |
|                                                    |
|  ## News                                           |
|  ### Hacker News                                   |
|  1. Show HN: I built a self-hosting platform       |
|  2. The case for boring technology (2025)           |
|                                                    |
+---------------------------------------------------+
|  Generated at 2026-02-21 07:00:00 EST              |
+---------------------------------------------------+
```

---

## Installation

### From ClawHub

```bash
openclaw install daily-digest
```

### Manual Installation

```bash
git clone https://github.com/sovereign-ai/daily-digest.git
cp -r daily-digest ~/.openclaw/skills/daily-digest
```

### Verify Installation

```bash
openclaw list | grep daily-digest
```

---

## Quick Start

1. **Run your first digest:**

   ```
   openclaw run daily-digest
   ```

   On first run, a default configuration file is created at `~/.openclaw/daily-digest/config.yaml`.

2. **Edit the config to add your sources:**

   ```bash
   $EDITOR ~/.openclaw/daily-digest/config.yaml
   ```

   Add your calendar URLs, preferred weather location, and RSS feeds.

3. **Run again to see your personalized digest:**

   ```
   openclaw run daily-digest
   ```

---

## Configuration

The config file lives at `~/.openclaw/daily-digest/config.yaml`. Key sections:

### Weather

```yaml
weather:
  enabled: true
  location: "San Francisco"
  units: "imperial"    # or "metric"
```

### Calendar

```yaml
calendar:
  enabled: true
  sources:
    - type: "ical"
      name: "Work"
      url: "https://calendar.google.com/calendar/ical/YOUR_ID/basic.ics"
    - type: "ical"
      name: "Personal"
      url: "/path/to/local/calendar.ics"
```

### Tasks

```yaml
tasks:
  enabled: true
  sources:
    - type: "todotxt"
      path: "~/todo.txt"
    - type: "github_issues"
      repo: "your-org/your-repo"
```

### News Feeds

```yaml
news:
  enabled: true
  feeds:
    - name: "Hacker News"
      url: "https://hnrss.org/frontpage"
      max_items: 5
    - name: "Your Favorite Blog"
      url: "https://example.com/feed.xml"
      max_items: 3
  keywords: ["AI", "startup", "funding"]
```

### Output Format

```yaml
general:
  output_format: "both"   # markdown, html, or both
  output_dir: "~/.openclaw/daily-digest/output"
```

---

## Usage Examples

### Basic digest

```
User: "Give me my daily digest"
```

### Morning briefing with specific sections

```
User: "Morning briefing with just calendar and tasks"
```

### HTML output

```
User: "Generate my digest in HTML format"
```

### Schedule for every weekday morning

```
User: "Schedule my digest for 6:30 AM every weekday"
```

### Add a new feed

```
User: "Add https://blog.example.com/feed.xml to my digest"
```

### Compare with yesterday

```
User: "Compare today's digest to yesterday"
```

---

## Running the Script Directly

The `scripts/digest.sh` helper can be run independently:

```bash
# Basic usage
bash scripts/digest.sh

# Custom config location
bash scripts/digest.sh --config /path/to/config.yaml

# HTML output
bash scripts/digest.sh --format html

# Different location
bash scripts/digest.sh --location "London"

# Full options
bash scripts/digest.sh --config ~/.my-config.yaml --format both --output ~/reports/
```

---

## Scheduling

### Linux / macOS (cron)

```bash
# Edit crontab
crontab -e

# Add this line for 7:00 AM every day
0 7 * * * cd ~/.openclaw/skills/daily-digest && bash scripts/digest.sh --format both
```

### macOS (launchd)

Create `~/Library/LaunchAgents/com.openclaw.daily-digest.plist` with the appropriate schedule.

### Windows (Task Scheduler)

1. Open Task Scheduler.
2. Create a new task triggered daily at your preferred time.
3. Set the action to run `bash scripts/digest.sh` from the skill directory.

---

## Requirements

- **bash** (4.0+)
- **curl** (for weather, RSS, and quote fetching)
- **python3** (for RSS parsing and HTML generation)
- **gh** CLI (optional, for GitHub Issues integration)

---

## File Structure

```
daily-digest/
  skill.json          Skill metadata for ClawHub
  SKILL.md            AI agent instructions
  README.md           This file
  scripts/
    digest.sh         Main compilation script
```

---

## Privacy

- All data is processed and stored locally.
- No telemetry or analytics.
- Email passwords are read exclusively from environment variables.
- Archived digests are automatically cleaned up based on your `max_archive_days` setting.

---

## License

MIT License. See skill.json for details.

---

## Author

**Sovereign AI (Taylor)**

Built with care for the OpenClaw ecosystem. If you find this skill useful, consider starring it on ClawHub.
