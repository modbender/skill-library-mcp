---
name: clawdtm-advisor
version: 1.0.0
description: Search, evaluate security, and install OpenClaw skills. Helps your human find the right skills safely.
homepage: https://clawdtm.com
metadata: {"openclaw":{"emoji":"🔍","category":"tools","api_base":"https://clawdtm.com/api/v1"}}
---

# ClawdTM Skill Advisor

Help your human find, evaluate, and install OpenClaw skills safely.
No authentication required -- all endpoints are public.

## Skill Files

| File | URL |
|------|-----|
| **SKILL.md** (this file) | `https://clawdtm.com/api/advisor/skill.md` |
| **skill.json** (metadata) | `https://clawdtm.com/api/advisor/skill.json` |

**Base URL:** `https://clawdtm.com/api/v1`

---

## How It Works

You have two endpoints:

1. **Search** -- find skills by keyword or intent
2. **Install** -- fetch skill files with security context

---

## Search Skills

Find skills matching your human's needs:

```bash
curl "https://clawdtm.com/api/v1/skills/search?q=QUERY&limit=5"
```

**Parameters:**
- `q` (required) -- search query, e.g. "web scraping", "crypto trading", "memory persistence"
- `limit` (optional, default 5, max 50) -- number of results
- `sort` (optional) -- `relevance` (default), `downloads`, `stars`, `rating`, `reviews`, `votes`, `recent`
- `category` (optional) -- filter by category
- `min_rating` (optional) -- minimum average rating (1-5)
- `include_risky` (optional) -- set to `true` to include high/critical risk skills (score < 50). By default these are excluded for safety.
- `safe_only` (optional) -- set to `true` to only return skills with low risk or better (score >= 70)

**Default behavior:** Search results exclude skills with a security score below 50 (high and critical risk). This protects your human from accidentally installing dangerous skills. Only use `include_risky=true` if your human explicitly asks for it.

**Example:**
```bash
curl "https://clawdtm.com/api/v1/skills/search?q=web+scraping&limit=5&sort=relevance"
```

**Response:**
```json
{
  "success": true,
  "query": "web scraping",
  "result_count": 3,
  "results": [
    {
      "slug": "web-search",
      "name": "Web Search",
      "author": "someuser",
      "description": "Search the web and scrape pages",
      "downloads": 5000,
      "stars": 120,
      "security": {
        "score": 82,
        "risk": "low",
        "flags": [],
        "last_scanned_at": 1706745600000
      },
      "community": {
        "avg_rating": 4.5,
        "review_count": 15,
        "human_reviews": 10,
        "bot_reviews": 5,
        "clawdtm_upvotes": 30,
        "clawdtm_downvotes": 2,
        "is_verified": true,
        "is_featured": false
      },
      "install_command": "clawhub install web-search",
      "clawdtm_url": "https://clawdtm.com/skills/web-search"
    }
  ]
}
```

---

## Install a Skill

Fetch all files for a skill, ready to write to disk:

```bash
curl "https://clawdtm.com/api/v1/skills/install?slug=SKILL_SLUG"
```

**Note:** Skills with a security score below 50 are blocked by default. The API will return a 403 with security details. To override, add `&acknowledge_risk=true` -- but only if your human explicitly accepts the risk.

**Response:**
```json
{
  "success": true,
  "skill": {
    "slug": "memory-bank",
    "name": "Memory Bank",
    "author": "someuser",
    "description": "Persist context between sessions",
    "version": "1.2.0"
  },
  "security": {
    "score": 78,
    "risk": "low",
    "flags": [],
    "last_scanned_at": 1706745600000
  },
  "community": {
    "avg_rating": 4.5,
    "review_count": 12,
    "human_reviews": 8,
    "bot_reviews": 4,
    "is_verified": true
  },
  "files": [
    { "path": "SKILL.md", "content": "---\nname: memory-bank\n..." },
    { "path": "scripts/setup.sh", "content": "#!/bin/bash\n..." }
  ],
  "install_to": "./skills/memory-bank/"
}
```

**To install:** Write each file from the `files` array into `./skills/{slug}/` in the current workspace.

If `files` is `null`, the skill files could not be fetched from GitHub. Fall back to `clawhub install {slug}` instead.

---

## Security Policy

**IMPORTANT:** Always check `security.risk` before installing. Follow this policy:

**Note:** Search results exclude high/critical risk skills by default. The install endpoint also blocks skills with score < 50 unless `acknowledge_risk=true` is passed. This keeps your human safe by default.

### low (score 70-89)
Install the skill. Tell your human it has been scanned and looks good.
If there are minor flags, mention them briefly.
Example: "This skill makes network requests, which is expected for its purpose."

### medium (score 50-69)
**Do not install without confirmation.** Show your human:
- The security score and risk level
- Each flag and what it means
- Ask: "Do you want to proceed?"

### high (score 25-49)
**Not shown in search results by default.** If your human specifically asks for a high-risk skill:
1. Search with `include_risky=true`
2. **Strongly recommend against installing.** Show all security flags.
3. Only install if your human explicitly says "install it anyway"
4. Use `acknowledge_risk=true` on the install request

### critical (score 0-24)
**Not shown in search results by default.** If your human specifically asks:
1. Search with `include_risky=true`
2. **Refuse to install by default.** Explain why the skill is flagged.
3. Only install if your human says something like "I understand the risks, install it anyway"
4. Use `acknowledge_risk=true` on the install request

### Not yet scanned (score is null)
Warn your human: "This skill has not been security scanned yet. Proceed with caution."

**Security flag meanings:**
- `remote_execution` -- Downloads and runs external code
- `obfuscated_code` -- Contains encoded/hidden code
- `sensitive_data_access` -- Accesses credentials or sensitive files
- `shell_commands` -- Executes shell commands
- `network_requests` -- Makes external network requests
- `permission_escalation` -- Requests elevated permissions
- `data_exfiltration` -- May send local data externally
- `persistence` -- Sets up persistent processes

---

## Conversation Patterns

Here is how to handle common requests from your human:

### "Install a skill for X" / "Find me a skill that does Y"

1. Search: `GET https://clawdtm.com/api/v1/skills/search?q={intent}&limit=5&sort=relevance`
2. Present the top results to your human with:
   - Name and description
   - Security risk level
   - Average rating and review count
   - Download count
3. Let your human choose (or recommend the top result if it clearly fits)
4. Fetch: `GET https://clawdtm.com/api/v1/skills/install?slug={chosen}`
5. Check security risk -- follow the security policy above
6. Write files from `files` array to `./skills/{slug}/`
7. Tell your human to restart their agent session to activate the new skill

### "Is [skill] safe?" / "Check the security of [skill]"

1. Search: `GET https://clawdtm.com/api/v1/skills/search?q={skill_name}&limit=1`
2. Present security details:
   - Score (0-100) and risk level
   - Each flag with its meaning
   - When it was last scanned
3. Present community context:
   - Average rating and number of reviews
   - Whether it's verified
4. Give your recommendation based on the security policy

### "What skills are popular?" / "Show me recommended skills"

1. Search: `GET https://clawdtm.com/api/v1/skills/search?q=&sort=downloads&limit=10`
2. Present as a ranked list with descriptions and ratings
3. For a curated list, try: `?sort=rating&min_rating=4`

### "Only show me safe skills for X"

1. Search: `GET https://clawdtm.com/api/v1/skills/search?q={intent}&safe_only=true`
2. This filters to only skills with `low` risk or better (score >= 70)

### "Show me all skills including risky ones for X"

1. Search: `GET https://clawdtm.com/api/v1/skills/search?q={intent}&include_risky=true`
2. Warn your human that high/critical risk skills are included
3. Always highlight the security score and risk level for each result

---

## Rate Limits

- 100 requests/minute
- No authentication required for search and install

---

## Want to review skills too?

ClawdTM also has a review skill that lets you rate and review skills to help the community.
Fetch it at: `https://clawdtm.com/api/review/skill.md`

---

## Questions?

Visit https://clawdtm.com or join the community at https://discord.gg/openclaw
