---
name: bkmrk
description: Bookmark intelligence for developers. Browse, search, triage, and manage your AI-analyzed library. Submit URLs, assign projects, trigger deep analysis, and execute staged items.
homepage: https://bkmrkapp.com
---

# BKMRK — Bookmark Intelligence

You are connected to the user's BKMRK library. BKMRK analyzes bookmarks with Claude AI against the user's coding projects, scoring relevance and generating implementation suggestions.

**Terminology:** The pipeline statuses are `new` → `staged` → `done`. Always use "stage" / "staged" (never "queue" or "queued") when referring to items the user wants to act on next.

## What Gets Analyzed

BKMRK performs deep content extraction across all source types:

- **Tweets** — full tweet text plus all URLs in the tweet
- **X Articles** — full article body extracted via X API (not just the title)
- **Threads** — reconstructed thread text from all replies, plus URLs found in every tweet in the thread (not just the first)
- **YouTube videos** — full transcript extracted (auto-generated or manual captions), analyzed uncapped regardless of video length
- **Blog posts / news articles** — full article text extracted via trafilatura, analyzed uncapped
- **GitHub repos** — README and repo metadata
- **Any URL** — submitted via the API, fetched and extracted automatically

All content is sent to Claude uncapped for analysis — long articles, 2-hour podcast transcripts, and full X Article bodies all get deep, project-specific analysis.

## Authentication

All requests require the user's BKMRK API key as a header:

```
X-API-Key: {BKMRK_API_KEY}
```

The API key is available at https://bkmrkapp.com/settings under "Your API Key."

## What You Can Do

### Browse Library

Browse the analyzed bookmark library with filters. Returns scores, statuses, per-project analyses, and executable prompts. Use this for triaging, browsing, and pipeline management.

```
GET https://bkmrkapp.com/api/agent/library
X-API-Key: {BKMRK_API_KEY}
```

All query parameters are optional:
- `status` — Filter by card status: `new`, `staged`, `done`, `trashed`
- `project_id` — Filter by project UUID
- `min_score` — Minimum relevance score (e.g. `7`)
- `priority` — Filter by priority: `high`, `medium`, `low`
- `source` — Filter by source: `sync` (from X bookmarks) or `agent` (submitted via API)
- `limit` — Max results (default: 50, max: 100)
- `include_project_analyses` — Include per-project deep analysis data (default: `true`)

Examples:
- Unactioned high-value items: `?status=new&min_score=7`
- Items staged for a specific project: `?status=staged&project_id=<uuid>`
- Agent-submitted items only: `?source=agent`
- Low-priority items for cleanup: `?priority=low&min_score=0`

### Search Library

Keyword search across titles, explanations, actions, authors, and URLs. Use this when looking for something specific.

```
POST https://bkmrkapp.com/api/agent/query
Content-Type: application/json
X-API-Key: {BKMRK_API_KEY}

{
  "q": "search terms",
  "project": "ProjectName",
  "priority": "high",
  "status": "new",
  "limit": 10
}
```

All fields are optional. Returns results sorted by relevance score.

### Manage Card Status

Move cards through the pipeline: new → staged → done, or trash/restore them.

```
POST https://bkmrkapp.com/api/status
Content-Type: application/json
X-API-Key: {BKMRK_API_KEY}
```

Single item:
```json
{ "bookmark_id": "<uuid>", "status": "staged" }
```

Batch update:
```json
{ "items": [
    { "bookmark_id": "<uuid>", "status": "done" },
    { "bookmark_id": "<uuid>", "status": "trashed" }
] }
```

Valid statuses: `new`, `staged`, `done`, `trashed` (use exact values — "staged" not "stage", "trashed" not "trash"). You can also set `"channel": "channel-name"` on any item.

### Manage Projects

List, create, and update coding projects that bookmarks are analyzed against.

**List projects:**
```
GET https://bkmrkapp.com/api/projects
X-API-Key: {BKMRK_API_KEY}
```

Returns all projects with IDs, names, descriptions, tech stacks, and focus areas. Use this to get project UUIDs for other calls.

**Create a project:**
```
POST https://bkmrkapp.com/api/projects
Content-Type: application/json
X-API-Key: {BKMRK_API_KEY}

{
  "name": "My Project",
  "description": "What this project does",
  "tech_stack": ["React", "Node.js"],
  "focus_areas": ["performance", "auth"]
}
```

**Update a project:**
```
PUT https://bkmrkapp.com/api/projects
Content-Type: application/json
X-API-Key: {BKMRK_API_KEY}

{
  "id": "<project-uuid>",
  "description": "Updated description",
  "tech_stack": ["React", "Next.js"]
}
```

### Deep Analysis

Trigger a deep re-analysis of a bookmark against specific projects. Uses Claude Sonnet for thorough analysis. Returns 202 immediately; results appear in the library within 1-2 minutes.

```
POST https://bkmrkapp.com/api/reanalyze
Content-Type: application/json
X-API-Key: {BKMRK_API_KEY}

{
  "bookmark_id": "<uuid>",
  "project_ids": ["<project-uuid>"]
}
```

Returns `job_id`, `credits_used`, and `credits_remaining`. Each project counts as 1 credit. Limits: Free 25/month, Pro 100/month, Scale 500/month.

### Understand Context

Get the user's dashboard summary: projects, tier, stats, and library counts.

```
GET https://bkmrkapp.com/api/context
X-API-Key: {BKMRK_API_KEY}
```

Returns project list, subscription tier, total bookmarks, items by status, and sync history.

### Submit URLs

Send any URL to the library for AI analysis. Supports tweets, YouTube videos, GitHub repos, blog posts, and any web page. Enrichment and analysis run in the background.

```
POST https://bkmrkapp.com/api/agent/submit
Content-Type: application/json
X-API-Key: {BKMRK_API_KEY}

{
  "url": "https://example.com/interesting-article"
}
```

Supported URL types:
- **Tweet URLs** (`x.com/user/status/123`) — fetches full tweet data, thread context, and all URLs
- **YouTube URLs** — extracts full video transcript for analysis
- **Any other URL** — extracts full article text, title, and og:image

Optionally include `"project_ids": ["<uuid>"]` to analyze against specific projects. Returns 202 with `bookmark_id` and `job_id`. Results appear in 1-2 minutes.

Limits: Free 5/month, Pro 50/month, Scale 200/month.

### Create Account (Onboarding)

If the user doesn't have a BKMRK account yet:

```
POST https://bkmrkapp.com/api/agent/onboard
Content-Type: application/json

{
  "email": "user@example.com",
  "consent": true
}
```

Returns an API key immediately. No OAuth needed.

## Example Agent Workflows

### Daily triage
1. `GET /api/context` — check current state
2. `GET /api/agent/library?status=new&min_score=7` — find high-value unactioned items
3. `POST /api/status` — stage the best ones, trash the noise

### Project deep-dive
1. `GET /api/projects` — get project UUIDs
2. `GET /api/agent/library?project_id=<uuid>` — see what's relevant to that project
3. `POST /api/reanalyze` — deep-analyze items that lack per-project data
4. `GET /api/agent/library?project_id=<uuid>` — review enriched results

### Bulk cleanup
1. `GET /api/agent/library?priority=low&min_score=0` — find low-value items
2. `POST /api/status` with batch `"status": "trashed"` — clear them out

### Submit and verify
1. `POST /api/agent/submit` with a URL — submit for analysis
2. Wait 1-2 minutes
3. `POST /api/agent/query` with `{"q": "hostname"}` — verify it was analyzed

## Full API Documentation

For complete endpoint documentation, pricing tiers, and capabilities:

```
GET https://bkmrkapp.com/agent.json
```
