---
name: blog-generator
displayName: Blog Generator | OpenClaw Skill
description: Analyzes journal entries and chat history to identify high-value topics and automatically generate blog posts.
version: 1.0.0
---

# Blog Generator | OpenClaw Skill

## Description

Analyzes journal entries and chat history to identify high-value topics and automatically generate blog posts.

# Blog Generator | OpenClaw Skill

Automatically generates blog posts by analyzing journal entries, chat history, and recent activity to identify high-value, high-search-volume topics related to OpenClaw.


## Usage

- As a scheduled cron job to automatically generate blog content weekly or daily
- Manually to create blog posts from recent journal analysis
- To identify and document high-value solutions and discoveries

```bash
# X-format articles as HTML; humanizer runs between generations; header from visual-explainer
python3 /Users/ghost/.openclaw/workspace/skills/blog-generator/scripts/blog_generator.py

# Skip humanizer (e.g. no OPENROUTER_API_KEY)
python3 /Users/ghost/.openclaw/workspace/skills/blog-generator/scripts/blog_generator.py --no-humanize

# Custom humanizer or visual-explainer paths
python3 /Users/ghost/.openclaw/workspace/skills/blog-generator/scripts/blog_generator.py --humanizer-path /Users/ghost/Downloads/humanizer-1.0.0 --visual-explainer-path /Users/ghost/.openclaw/workspace/skills/visual-explainer-main

# Classic format (overview/problem/solution), still HTML
python3 /Users/ghost/.openclaw/workspace/skills/blog-generator/scripts/blog_generator.py --format classic

# JSON output
python3 /Users/ghost/.openclaw/workspace/skills/blog-generator/scripts/blog_generator.py --days 14 --max-topics 5 --json
```


## What this skill does

- **Scans** journal entries from the last N days for interesting topics (discoveries, obstacles, solutions)
- **Identifies** high-value topics based on keyword relevance and problem-solving value
- **Researches** search volume and keyword opportunities (heuristic-based, can be enhanced with APIs)
- **Generates** structured blog posts with overview, problem, solution, and takeaways sections
- **Saves** blog posts to `/Users/ghost/.openclaw/blogs/` as HTML only (X-article format, header from visual-explainer, humanizer between generations)


## Integration as a Cron Job

This skill is designed to run periodically (daily or weekly) via OpenClaw cron to automatically generate blog content.

**Example Cron Job Configuration (Daily):**

```json
{
  "payload": {
    "kind": "agentTurn",
    "message": "Run blog-generator skill to analyze journal entries and generate high-value blog posts.",
    "model": "openrouter/google/gemini-2.5-flash",
    "thinking": "low",
    "timeoutSeconds": 300
  },
  "schedule": {
    "kind": "cron",
    "cron": "0 9 * * *"
  },
  "delivery": {
    "mode": "announce"
  },
  "sessionTarget": "isolated",
  "name": "Blog Post Generator"
}
```

**Example Cron Job Configuration (Weekly):**

```json
{
  "payload": {
    "kind": "agentTurn",
    "message": "Run blog-generator skill with --days 7 --max-topics 3 to generate weekly blog posts from journal analysis.",
    "model": "openrouter/google/gemini-2.5-flash",
    "thinking": "low",
    "timeoutSeconds": 300
  },
  "schedule": {
    "kind": "cron",
    "cron": "0 10 * * 1"
  },
  "delivery": {
    "mode": "announce"
  },
  "sessionTarget": "isolated",
  "name": "Weekly Blog Generator"
}
```


## Output Format

**HTML only** (no Markdown). Output is in the format accepted by X articles: one header (from visual-explainer), then article body with no interlaced visuals.

- **File:** `/Users/ghost/.openclaw/blogs/YYYYMMDD_slugified-title.html`
- **Article structure:** **X-style** (long-form): punchy hook, short paragraphs, "two types of people" framing, pivot, stakes. Use `--format classic` for overview/problem/solution.
- **Header:** From visual-explainer only. Default path: `/Users/ghost/.openclaw/workspace/skills/visual-explainer-main`. The skill’s `scripts/generate_header.py` is called with `section: "header"` and returns an `html_snippet` (hero with title and optional summary). No diagrams or images in the body.
- **Humanizer:** Runs **between generations** by default. Each article’s body is sent through `/Users/ghost/Downloads/humanizer-1.0.0` (requires `OPENROUTER_API_KEY`) before rendering to HTML. Use `--no-humanize` to skip.


## Topic Scoring

Topics are scored based on:

- **High-value keywords**: OpenClaw-specific terms, problem-solving language
- **Content type**: Solutions score highest, then obstacles, then discoveries
- **Content depth**: Longer, more detailed content scores higher
- **Search volume indicators**: Keywords like "how to", "tutorial", "fix" increase value


## Requirements

- Journal entries in `/Users/ghost/.openclaw/journal/`
- Blogs directory writable at `/Users/ghost/.openclaw/blogs/`
- Chat history analyzer skill (for journal entries)


## How it works

1. Scans journal directory for markdown files from the last N days
2. Extracts topics from discoveries, obstacles, and solutions sections
3. Scores topics based on keyword relevance and value
4. Selects top N high-value topics
5. Generates structured blog posts with problem/solution format
6. Saves posts to blogs directory with timestamped filenames


## Enhancement Opportunities

- Integrate with Google Keyword Planner API for real search volume data
- Use AI model to enhance blog post quality and SEO optimization
- Cross-reference with existing blog posts to avoid duplicates
- Generate multiple variations of posts for A/B testing
