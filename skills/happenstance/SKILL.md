---
name: happenstance
description: Search your professional network and research people using the Happenstance API.
metadata:
  openclaw:
    requires:
      env:
        - HAPPENSTANCE_API_KEY
      bins:
        - curl
    primaryEnv: HAPPENSTANCE_API_KEY
---

# Happenstance

Search your network and get detailed research profiles on people using the Happenstance API.

Documentation: https://developer.happenstance.ai

## Authentication

All requests require the `HAPPENSTANCE_API_KEY` environment variable. Pass it as a Bearer token:

```
Authorization: Bearer $HAPPENSTANCE_API_KEY
```

Base URL: `https://api.happenstance.ai`

## Billing

- **Search**: 2 credits per search (including find-more)
- **Research**: 1 credit per completed research
- Check balance with `GET /v1/usage`
- Purchase credits at https://happenstance.ai/settings/api

## Available Operations

### 1. Search Your Network

Search for people across groups and connections. Searches run asynchronously.

**Start a search:**

```bash
curl -s -X POST https://api.happenstance.ai/v1/search \
  -H "Authorization: Bearer $HAPPENSTANCE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "engineers who have worked on AI infrastructure",
    "include_my_connections": true,
    "include_friends_connections": true
  }'
```

You can also search within specific groups by adding `"group_ids": ["uuid1", "uuid2"]`. Get group IDs from `GET /v1/groups`.

At least one search source is required: `group_ids`, `include_my_connections: true`, or `include_friends_connections: true`.

**Response:**

```json
{"id": "search-uuid", "url": "https://happenstance.ai/search/search-uuid"}
```

**Poll for results** (every 5-10 seconds until status is `COMPLETED` or `FAILED`):

```bash
curl -s https://api.happenstance.ai/v1/search/SEARCH_ID \
  -H "Authorization: Bearer $HAPPENSTANCE_API_KEY"
```

**Completed response includes:**

- `status`: `RUNNING`, `COMPLETED`, or `FAILED`
- `results`: array of people, each with `id`, `name`, `current_title`, `current_company`, `summary`, `weighted_traits_score`, `socials` (with `happenstance_url`, `linkedin_url`, `twitter_url`), `mutuals`, and `traits`
- `has_more`: boolean indicating if more results are available
- `mutuals`: top-level array of mutual connections (results reference these by index)
- `traits`: top-level array of trait definitions (results reference these by index)

### 2. Find More Results

When `has_more` is `true` on a completed search, get additional results that exclude all previously returned people. Costs 2 credits.

```bash
curl -s -X POST https://api.happenstance.ai/v1/search/SEARCH_ID/find-more \
  -H "Authorization: Bearer $HAPPENSTANCE_API_KEY"
```

**Response:**

```json
{"page_id": "page-uuid", "parent_search_id": "search-uuid"}
```

Then poll with the page_id:

```bash
curl -s "https://api.happenstance.ai/v1/search/SEARCH_ID?page_id=PAGE_ID" \
  -H "Authorization: Bearer $HAPPENSTANCE_API_KEY"
```

### 3. Research a Person

Get a detailed professional profile for a specific person. Runs asynchronously.

**Start research:**

```bash
curl -s -X POST https://api.happenstance.ai/v1/research \
  -H "Authorization: Bearer $HAPPENSTANCE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"description": "Garry Tan, CEO of Y Combinator, @garrytan on Twitter"}'
```

Include as many details as possible (full name, company, title, location, social handles) for best results.

**Response:**

```json
{"id": "research-uuid"}
```

**Poll for results** (every 5-10 seconds until status is `COMPLETED`, `FAILED`, or `FAILED_AMBIGUOUS`):

```bash
curl -s https://api.happenstance.ai/v1/research/RESEARCH_ID \
  -H "Authorization: Bearer $HAPPENSTANCE_API_KEY"
```

**Completed response includes a `profile` object with:**

- `person_metadata`: `full_name`, `alternate_names`, `profile_urls`, `current_locations`, `tagline`
- `employment`: array of jobs with `company_name`, `job_title`, `start_date`, `end_date`, `description`
- `education`: array with `university_name`, `degree`, `start_date`, `end_date`
- `projects`: array with `title`, `description`, `urls`
- `writings`: array of publications with `title`, `description`, `date`, `urls`
- `hobbies`: array with `description`
- `summary`: overall `text` summary with supporting `urls`

### 4. List Groups

Get the groups you can search within:

```bash
curl -s https://api.happenstance.ai/v1/groups \
  -H "Authorization: Bearer $HAPPENSTANCE_API_KEY"
```

Returns `{"groups": [{"id": "uuid", "name": "Group Name"}, ...]}`.

### 5. Check Credits and Usage

```bash
curl -s https://api.happenstance.ai/v1/usage \
  -H "Authorization: Bearer $HAPPENSTANCE_API_KEY"
```

Returns `balance_credits`, `has_credits`, `purchases`, `usage` history, and `auto_reload` settings.

## Error Handling

Errors use RFC 7807 format:

```json
{"type": "about:blank", "title": "Bad Request", "status": 400, "detail": "Description must not be empty", "instance": "/v1/research"}
```

Key status codes:
- `401`: Invalid or missing API key
- `402`: Insufficient credits
- `429`: Too many concurrent requests (max 10 running searches or research requests)
- `500`/`503`: Server error, retry with backoff

## Tips

- Always check credits before starting multiple searches or research requests.
- Search typically completes in 30-60 seconds. Research takes 1-3 minutes.
- Each search returns up to 30 results. Use find-more for additional pages.
- When presenting search results, include the person's name, title, company, summary, and Happenstance profile link.
- When presenting research, summarize the profile and link to sources.
- The more data sources the user connects, the better the search results.
