---
name: multi-platform-crosspost
description: Automatically cross-post blog content to 7+ platforms (LinkedIn, Dev.to, Hashnode, Twitter/X, Reddit, Substack, Pinterest) with tracking, deduplication, and platform-specific formatting. Production-tested pipeline.
tags: [cross-posting, content-distribution, seo, blog, linkedin, devto, hashnode, automation, marketing]
author: mhmalvi
version: 1.2.0
license: CC BY-NC-SA 4.0
metadata:
  clawdbot:
    emoji: "📡"
    requires:
      n8nCredentials: [google-sheets-oauth2, smtp, linkedin-oauth2]
    os: [linux, darwin, win32]
---

# Multi-Platform Cross-Post Pipeline 📡

Automatically distribute your blog content across 7+ platforms with a single command. Built for Hugo blogs but adaptable to any static site generator or CMS.

## Problem

You write a great article. Then you spend 45 minutes manually posting it to LinkedIn, Dev.to, Hashnode, Reddit, Substack, and Twitter. Every. Single. Time.

This skill eliminates that entirely.

## What It Does

1. Takes a blog post slug as input
2. Fetches the full article content from your blog admin API
3. Formats content for each platform (HTML → Markdown, character limits, image handling)
4. Posts automatically to platforms with API access (Dev.to, Hashnode, LinkedIn)
5. Emails formatted content for platforms without API (Twitter, Reddit, Substack)
6. Tracks all cross-posts in Google Sheets (deduplication via slug + source matching)
7. Handles auth, rate limits, and error recovery

## Supported Platforms

| Platform | Method | Automation Level |
|----------|--------|-----------------|
| LinkedIn | API (OAuth) | Fully automated |
| Dev.to | API (token) | Fully automated |
| Hashnode | API (token) | Fully automated |
| Pinterest | API | Fully automated |
| Twitter/X | Email digest | Content formatted, manual post |
| Reddit | Email digest | Content formatted, manual post |
| Substack | Email digest | Content formatted, manual post |

## Architecture

```
Blog Post Published
    │
    ▼
Webhook Trigger (n8n)
    │
    ├── Validate auth (_secret)
    ├── Fetch post content from blog-admin API
    ├── Parse frontmatter + body
    │
    ├──► IF LinkedIn enabled → Format + Post via API
    ├──► IF Dev.to enabled → Format + Post via API
    ├──► IF Hashnode enabled → Format + Post via API
    ├──► IF Pinterest enabled → Format + Pin via API
    ├──► IF Twitter enabled → Format + Email to owner
    ├──► IF Reddit enabled → Format + Email to owner
    └──► IF Substack enabled → Format + Email to owner
    │
    ▼
Google Sheets Tracker (appendOrUpdate, no duplicates)
```

## Required n8n Credentials

You must create these credentials in your n8n instance before importing:

| Credential Type | Used For | Placeholder in JSON |
|----------------|----------|---------------------|
| Google Sheets OAuth2 | Cross-post tracking and deduplication | `YOUR_GOOGLE_SHEETS_CREDENTIAL_ID` |
| SMTP (Gmail or custom) | Email digests for manual platforms | `YOUR_SMTP_CREDENTIAL_ID` |
| LinkedIn OAuth2 | Auto-posting to LinkedIn | `YOUR_LINKEDIN_CREDENTIAL_ID` |
| OpenAI (optional) | AI-powered content formatting | `YOUR_OPENAI_CREDENTIAL_ID` |

## Configuration Placeholders

Replace these placeholders in the workflow JSON before deploying:

| Placeholder | Description |
|-------------|-------------|
| `YOUR_BLOG_ADMIN_API_KEY` | API key for your blog admin panel |
| `YOUR_CROSSPOST_SECRET` | Webhook authentication secret |
| `YOUR_TRACKER_SHEET_ID` | Google Sheet ID for cross-post tracking |
| `YOUR_GOOGLE_SHEETS_CREDENTIAL_ID` | n8n Google Sheets credential ID |
| `YOUR_SMTP_CREDENTIAL_ID` | n8n SMTP credential ID |
| `YOUR_LINKEDIN_CREDENTIAL_ID` | n8n LinkedIn OAuth credential ID |
| `YOUR_LINKEDIN_PERSON_ID` | Your LinkedIn profile URN |
| `YOUR_OPENAI_CREDENTIAL_ID` | n8n OpenAI credential ID |
| `YOUR_BLOG_DOMAIN` | Your blog's public URL |
| `YOUR_FROM_EMAIL` | Sender email for digests |
| `YOUR_NOTIFICATION_EMAIL` | Where to send cross-post summaries |
| `YOUR_BLOG_ADMIN_HOST:3000` | Blog admin hostname (Docker or URL) |

## Quick Start

### 1. Prerequisites
- n8n instance (v2.4+)
- Blog with an API endpoint that returns post content
- Google Sheets OAuth2 credentials
- Platform API keys (at least one)

### 2. Configure Platforms
Set your API credentials in the workflow's Platform Config node:

```json
{
  "devto_api_key": "your-dev-to-api-key",
  "hashnode_token": "your-hashnode-token",
  "hashnode_publication_id": "your-pub-id",
  "linkedin_credential_id": "your-linkedin-oauth-id"
}
```

### 3. Set Up Tracking Sheet
Create a Google Sheet with columns:
- `slug` (text) — Post identifier
- `source` (text) — Blog name (for multi-blog support)
- `date` (date) — Cross-post date
- `platforms` (text) — Comma-separated list of platforms posted to
- `status` (text) — success/partial/failed

### 4. Trigger
```bash
# Via webhook
curl -X POST https://your-n8n.com/webhook/blog-crosspost \
  -H "Content-Type: application/json" \
  -d '{"slug": "my-article", "lang": "en", "platforms": "all", "_secret": "your-secret"}'

# Or via blog admin (auto-triggers on first publish)
```

## Platform-Specific Formatting

### Dev.to
- Converts HTML to Markdown
- Adds canonical URL pointing to original
- Maps categories to Dev.to tags (max 4)
- Prepends cover image

### Hashnode
- Markdown with frontmatter
- Canonical URL backlink
- Tag mapping to Hashnode tags
- Publication-scoped posting

### LinkedIn
- Plain text with line breaks (no markdown)
- Truncated to 3,000 chars
- Includes link to full article
- Hashtag injection from tags

### Pinterest
- Creates pin with featured image
- Title from post title
- Description from meta description
- Link to original article

## Deduplication

The tracker uses Google Sheets `appendOrUpdate` with matching on `slug` + `source`. This means:
- First post → creates new row
- Re-trigger same slug → updates existing row (no duplicates)
- Different blogs with same slug → separate rows (source differentiates)

## Multi-Blog Support

Run multiple blogs through the same pipeline by setting different `source` values:
- Blog A: `source: "my-tech-blog"`
- Blog B: `source: "my-business-blog"`

Each gets tracked separately in the same sheet.

## Use Cases

1. **Solo blogger** — Write once, distribute everywhere
2. **Content agency** — Manage cross-posting for multiple client blogs
3. **SEO strategy** — Build backlink network across 7 platforms automatically
4. **Newsletter growth** — Each platform drives subscribers to your newsletter

## Requirements

- n8n v2.4+ (self-hosted or cloud)
- At least one platform API key
- Google Sheets API credentials
- Blog admin API or file system access to post content

## Tips

- Start with Dev.to + LinkedIn (highest ROI, easiest setup)
- Add platforms incrementally
- Monitor the tracking sheet for failed posts
- Canonical URLs prevent duplicate content penalties
- Schedule cross-posts 1-2 hours after original publish for better engagement
