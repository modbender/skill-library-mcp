---
name: social-media-autopilot
description: "Schedule, compose, and publish social media posts across X (Twitter), LinkedIn, and Instagram from OpenClaw. Manage a content calendar, queue posts with approval workflows, track engagement analytics, and maintain brand voice consistency. Use when: (1) scheduling or publishing social media posts, (2) managing a content calendar, (3) drafting posts for multiple platforms, (4) reviewing post performance/analytics, (5) setting up automated posting workflows, or (6) maintaining a social media presence."
---

# Social Media Autopilot

Multi-platform social media management from your OpenClaw agent. Schedule posts, manage a content calendar, get approval before publishing, and track performance.

## Setup

### Required API Credentials

Configure in your environment or `.env` file:

- **X (Twitter):** Requires `xurl` skill or X API v2 credentials (`X_BEARER_TOKEN`, `X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_SECRET`)
- **LinkedIn:** `LINKEDIN_ACCESS_TOKEN` (OAuth 2.0 — see `references/linkedin-setup.md`)
- **Instagram:** `INSTAGRAM_ACCESS_TOKEN` + `INSTAGRAM_BUSINESS_ID` (Meta Graph API — see `references/instagram-setup.md`)

### Content Directory

All content lives in `~/.openclaw/workspace/social-media/`:

```
social-media/
├── calendar.json        # Scheduled posts
├── drafts/              # Posts awaiting approval
├── published/           # Archive of sent posts
├── templates/           # Reusable post templates
└── analytics/           # Performance data
```

Run `scripts/init-workspace.sh` to create this structure.

## Core Workflows

### 1. Draft & Schedule Posts

To create a post:

1. Run `scripts/draft-post.sh --platform <x|linkedin|instagram|all> --text "Post content" [--media path/to/image] [--schedule "2026-02-25 09:00 PST"]`
2. Post saves to `drafts/` as a JSON file with metadata
3. If `--schedule` is set, it's added to `calendar.json`
4. Without `--schedule`, it queues for immediate review

Draft JSON format:
```json
{
  "id": "uuid",
  "platforms": ["x", "linkedin"],
  "text": "Post content here",
  "media": [],
  "scheduled_at": "2026-02-25T17:00:00Z",
  "status": "draft",
  "created_at": "2026-02-23T22:00:00Z",
  "approved": false,
  "tags": ["product-launch"],
  "thread": false
}
```

### 2. Approval Workflow

Before any post goes live:

1. Agent presents the draft to the user with platform previews
2. User approves, edits, or rejects
3. Only approved posts get published
4. Use `scripts/approve-post.sh <post-id>` or `scripts/reject-post.sh <post-id> --reason "..."`

**Never auto-publish without explicit approval** unless the user has configured `auto_approve: true` in `social-media/config.json`.

### 3. Publishing

Run `scripts/publish-post.sh <post-id>` to publish an approved post.

The script:
- Validates the post is approved
- Adapts content per platform (character limits, hashtag style, media format)
- Posts via each platform's API
- Saves response data (post IDs, URLs) to `published/`
- Updates `calendar.json` status

Platform-specific adaptations:
- **X:** 280 char limit, auto-thread if longer, image upload via media endpoint
- **LinkedIn:** 3000 char limit, supports articles and documents
- **Instagram:** Requires media (image/video), caption limit 2200 chars

### 4. Content Calendar

View and manage scheduled content:

- `scripts/calendar.sh --week` — Show this week's schedule
- `scripts/calendar.sh --month` — Monthly overview
- `scripts/calendar.sh --gaps` — Find gaps in posting schedule
- `scripts/calendar.sh --reschedule <post-id> "new-datetime"` — Move a post

### 5. Analytics

Pull engagement data for published posts:

- `scripts/analytics.sh --last 7d` — Last 7 days performance
- `scripts/analytics.sh --post <post-id>` — Single post performance
- `scripts/analytics.sh --report weekly` — Generate weekly report

Metrics tracked: impressions, engagements, clicks, replies, reposts, likes, followers gained.

### 6. Templates & Brand Voice

Store reusable templates in `templates/`:

```json
{
  "name": "product-announcement",
  "platforms": ["x", "linkedin"],
  "template": "🚀 {product_name} is here!\n\n{description}\n\n{link}\n\n{hashtags}",
  "variables": ["product_name", "description", "link", "hashtags"],
  "voice_notes": "Excited but professional. No ALL CAPS."
}
```

When composing posts, reference `social-media/brand-voice.md` for tone guidelines if it exists.

## Cron Integration

Add to OpenClaw cron for automated workflows:

- **Publish scheduled posts:** Check `calendar.json` every 15 min, publish any due approved posts
- **Daily digest:** Summarize yesterday's analytics each morning
- **Gap alerts:** Notify if no posts scheduled for next 48h

## Error Handling

- API rate limits: Back off and retry with exponential delay
- Failed posts: Move to `drafts/` with `status: "failed"` and error message
- Expired tokens: Alert user to re-authenticate

## References

- `references/linkedin-setup.md` — LinkedIn OAuth setup guide
- `references/instagram-setup.md` — Instagram/Meta Graph API setup guide
- `references/platform-limits.md` — Character limits, media specs, rate limits per platform
