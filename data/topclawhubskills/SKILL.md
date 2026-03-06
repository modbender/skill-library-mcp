---
name: topclawhubskills
display_name: Top ClawHub Skills
description: Discover the most popular, newest, and security-certified ClawHub skills via live API data.
emoji: "\U0001F4CA"
os:
  - macos
  - linux
  - windows
---

# Top ClawHub Skills

You have access to a live API that provides real-time data about ClawHub skills — downloads, stars, newest additions, and security certification status.

## API Base URL

```
https://topclawhubskills.com/api
```

## Available Endpoints

### 1. Top Downloads
```
GET /api/top-downloads?limit=N
```
Returns the most downloaded skills, sorted by download count descending. Default limit: 20, max: 100.

### 2. Top Stars
```
GET /api/top-stars?limit=N
```
Returns the most starred skills, sorted by star count descending.

### 3. Newest Skills
```
GET /api/newest?limit=N
```
Returns the most recently published skills, sorted by creation date descending.

### 4. Security-Certified Skills
```
GET /api/certified?limit=N
```
Returns only skills that have passed security screening (not flagged as suspicious and not malware-blocked). Sorted by downloads descending.

### 5. Deleted Skills
```
GET /api/deleted?limit=N
```
Returns skills that were previously listed on ClawHub but now return "Skill not found." — preserved for historical reference. Sorted by downloads descending. Each result includes `is_deleted: true` and a `deleted_at` timestamp.

### 6. Search
```
GET /api/search?q=TERM&limit=N
```
Free-text search across skill slug, display name, summary, and owner handle. The `q` parameter is required.

### 7. Aggregate Statistics
```
GET /api/stats
```
Returns overall platform statistics: total skills, total downloads, total stars, certified skill count, deleted skill count, and the newest skill.

### 8. Health Check
```
GET /api/health
```
Returns API uptime and total skill count.

## Response Format

All list endpoints return:
```json
{
  "ok": true,
  "data": [
    {
      "slug": "skill-name",
      "display_name": "Skill Name",
      "summary": "What this skill does...",
      "downloads": 1234,
      "stars": 56,
      "owner_handle": "author",
      "created_at": "2026-01-15T10:30:00.000Z",
      "updated_at": "2026-02-10T14:20:00.000Z",
      "is_certified": true,
      "is_deleted": false,
      "deleted_at": null,
      "clawhub_url": "https://clawhub.ai/skills/skill-name"
    }
  ],
  "total": 20,
  "limit": 20,
  "generated_at": "2026-02-16T12:00:00.000Z"
}
```

The `/api/stats` endpoint returns:
```json
{
  "ok": true,
  "data": {
    "total_skills": 850,
    "total_downloads": 2500000,
    "total_stars": 45000,
    "certified_skills": 780,
    "deleted_skills": 186,
    "newest_skill": {
      "slug": "latest-skill",
      "display_name": "Latest Skill",
      "created_at": "2026-02-16T08:00:00.000Z"
    }
  },
  "generated_at": "2026-02-16T12:00:00.000Z"
}
```

## How to Use

1. **Fetch data** from the appropriate endpoint using HTTP GET.
2. **Format results** as a clean Markdown table for the user.
3. **Always include ClawHub links** so users can install skills directly.

## Formatting Rules

When presenting results to the user:

- **Downloads:** Format large numbers with K/M suffixes (e.g., 1,234 → `1.2K`, 1,500,000 → `1.5M`)
- **Stars:** Show as-is with a star symbol (e.g., `42`)
- **Certified status:** Show `Certified` for certified skills, leave blank otherwise
- **Links:** Always link to the ClawHub page using the `clawhub_url` field
- **Dates:** Show as relative time when possible (e.g., "2 days ago", "3 weeks ago")

### Example Table Output

| # | Skill | Author | Downloads | Stars | Certified |
|---|-------|--------|-----------|-------|-----------|
| 1 | [Skill Name](https://clawhub.ai/skills/skill-name) | @author | 45.2K | 312 | Certified |
| 2 | [Another Skill](https://clawhub.ai/skills/another-skill) | @dev | 38.1K | 289 | Certified |
| 3 | [Third Skill](https://clawhub.ai/skills/third-skill) | @creator | 22.7K | 156 | |

## Security Messaging

When showing certified skills or when the user asks about security:

> All certified skills on ClawHub have been verified through automated security screening that goes beyond standard VirusTotal checks. This multi-layer analysis examines code patterns, network behavior, and permission requests to ensure skills are safe to install.

## Example Queries

- "What are the most popular ClawHub skills?" → Use `/api/top-downloads`
- "Show me the newest skills" → Use `/api/newest`
- "Find skills related to git" → Use `/api/search?q=git`
- "Which skills are security-certified?" → Use `/api/certified`
- "How many skills are on ClawHub?" → Use `/api/stats`
- "What are the most loved skills?" → Use `/api/top-stars`
- "Which skills have been removed?" → Use `/api/deleted`
