---
name: twinfold
description: Control Twinfold — AI-powered social media content platform — from your agent. Create posts, generate images, adapt content for 10 platforms in 13 languages, manage autopilot, publish, and track analytics. Use when the user wants to create social media content, post to LinkedIn/Twitter/Instagram/etc., manage their content calendar, run autopilot content generation, check trends, or interact with their Twinfold account. Triggers on: post, publish, tweet, linkedin, social media, content, schedule, autopilot, twinfold, thread, adapt, trends, repurpose.
metadata:
  openclaw:
    requires:
      env:
        - TWINFOLD_API_KEY
    credentials:
      - name: TWINFOLD_API_KEY
        description: "Twinfold API key (starts with twf_). Get one at twinfold.app → Settings → API Keys."
        required: true
        prefix: "twf_"
---

# Twinfold Skill

Control [Twinfold](https://twinfold.app) — the AI thought leadership platform — via its MCP API.

## Setup

The user needs a Twinfold API key. Check env var `TWINFOLD_API_KEY`.

If missing, tell the user:
1. Go to **twinfold.app → Settings → API Keys**
2. Create a key (starts with `twf_`)
3. Set it: `export TWINFOLD_API_KEY=twf_...` or add to `.env`

## API

**Endpoint:** `POST https://twinfold.app/api/mcp/tools`  
**Auth:** `Authorization: Bearer <TWINFOLD_API_KEY>`  
**Body:** `{ "tool": "twinfold.<toolName>", "arguments": { ... } }`

All calls return `{ "result": { ... } }` on success or `{ "error": "..." }` on failure.

### Discover tools

```bash
curl https://twinfold.app/api/mcp/tools
```

Returns all 34 tools with schemas. No auth required.

## Tools Quick Reference

### Content Creation

| Tool | Use |
|------|-----|
| `createPost` | Generate a post with AI. Supports multilingual, images, first comments, per-platform adaptation, auto-publish |
| `createArticle` | Generate long-form articles with Twin knowledge |
| `adaptContent` | Rewrite content for a specific platform's culture and format |
| `generateHooks` | Get 4 viral hook options with engagement scores |
| `generateImage` | Generate an AI image and attach to a post |
| `repurposeContent` | Turn any text into multi-platform draft posts |
| `planContent` | Generate a multi-day content calendar with draft posts |

### Content Management

| Tool | Use |
|------|-----|
| `getPost` | Read a single post with full details |
| `listPosts` | List posts (filter by status/platform) |
| `updatePost` | Edit content, platforms, media, schedule |
| `deletePost` | Remove draft/scheduled posts |
| `listArticles` | List articles |

### Publishing

| Tool | Use |
|------|-----|
| `publishNow` | Publish immediately to connected platforms |
| `schedulePost` | Schedule for a future date/time |

### Autopilot

| Tool | Use |
|------|-----|
| `runAutopilot` | Trigger full autopilot pipeline (discover → create → publish) |
| `getAutopilotQueue` | List posts pending review |
| `approvePost` | Approve for scheduled publication |
| `rejectPost` | Reject an autopilot post |

### Intelligence

| Tool | Use |
|------|-----|
| `queryTwin` | Ask the AI Twin questions based on user's expertise |
| `addKnowledge` | Teach the Twin new knowledge |
| `getTrends` | Fetch trending topics scored by relevance |

### Brand Guide & Voice

| Tool | Use |
|------|-----|
| `getBrandGuide` | Get the brand guide markdown |
| `setBrandGuide` | Update brand guide (free, no credits) |
| `generateBrandGuide` | AI-generate brand guide from Twin knowledge (5 credits) |
| `listBrandVoices` | List all brand voice profiles |
| `createBrandVoice` | Create a brand voice manually |
| `updateBrandVoice` | Update an existing brand voice |
| `deleteBrandVoice` | Delete a brand voice |
| `generateBrandVoice` | AI-generate a brand voice analysis (5 credits) |

### Notifications

| Tool | Use |
|------|-----|
| `getNotifications` | List notifications (unread, by type, paginated) |
| `markNotificationRead` | Mark one or all notifications as read |
| `getNotificationPreferences` | Get notification channel preferences |

### Account

| Tool | Use |
|------|-----|
| `listAccounts` | Connected social accounts + content languages |
| `getCredits` | Credit balance, plan, cost table |
| `getAnalytics` | Post stats and workspace analytics |

## Common Workflows

For detailed tool schemas and workflow examples, read [references/workflows.md](references/workflows.md).

### Quick: Create and publish a post

```
1. twinfold.createPost { topic, platforms, language, autoAdapt: true, autoPublish: true }
```

One call does it all — generates content, adapts per platform, publishes.

### Quick: Create, review, then publish

```
1. twinfold.createPost { topic, platforms, language }  → postId
2. Show content to user, let them edit
3. twinfold.updatePost { postId, content: editedContent }
4. twinfold.publishNow { postId }
```

### Full pipeline with images and hooks

```
1. twinfold.generateHooks { topic }  → pick best hook
2. twinfold.createPost { topic, platforms, language, generateImage: true, generateFirstComment: true }  → postId
3. twinfold.getPost { postId }  → review
4. twinfold.publishNow { postId }
```

## Platforms

LinkedIn · Twitter/X · Instagram · Facebook · YouTube · TikTok · Pinterest · Threads · Reddit · Bluesky

## Languages

English · French · Quebec French (fr-CA) · Spanish · German · Portuguese · Brazilian Portuguese · Italian · Dutch · Japanese · Korean · Chinese · Arabic

Set language per social account or per API call. Content generates natively (not translated).

## Credit Costs

| Operation | Credits |
|-----------|---------|
| Post | 10 |
| Article | 50 |
| Hook simulation | 5 |
| Image | 10 |
| First comment | 2 |
| Twin query | 2 |
| Brand guide generate | 5 |
| Brand voice generate | 5 |

Always check `twinfold.getCredits` before heavy operations.

## Error Handling

- `401` → Invalid API key
- `402` → Insufficient credits (check with `getCredits`)
- `400` → Bad arguments (error message explains what's wrong)
- `429` → Rate limited (wait and retry)

## Tips

- Use `autoAdapt: true` on `createPost` to get platform-optimized versions automatically
- Set `language: "fr-CA"` for authentic Quebec French content
- Use `getTrends` → `createPost` for trend-jacking workflows
- `repurposeContent` turns blog posts, transcripts, or notes into social posts
- `planContent` creates a full week of drafts in one call
- Autopilot runs daily — use `getAutopilotQueue` + `approvePost` for review workflows
