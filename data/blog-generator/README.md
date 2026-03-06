# Blog Generator

Automatically generates blog posts by analyzing journal entries and chat history to identify high-value topics.

## Quick Start

```bash
# Generate blog posts from last 7 days
python3 scripts/blog_generator.py

# Generate from last 14 days, up to 5 posts
python3 scripts/blog_generator.py --days 14 --max-topics 5
```

## Features

- Scans journal entries for discoveries, obstacles, and solutions
- Scores topics based on keyword relevance and value
- Generates structured blog posts with problem/solution format
- Saves to `/Users/ghost/.openclaw/blogs/`

## Cron Job Setup

See `SKILL.md` for OpenClaw cron job configuration examples. Recommended schedule: daily at 9 AM or weekly on Mondays.

## Output

Blog posts are saved as:
```
/Users/ghost/.openclaw/blogs/YYYYMMDD_slugified-title.md
```

Each post includes:
- Overview
- Problem description
- Solution guide
- Key takeaways
- Related topics
