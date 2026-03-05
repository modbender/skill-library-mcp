---
name: web-skills-protocol
description: >
  Auto-discover and use Web Skills Protocol (WSP) skills when interacting with websites.
  Use this skill whenever the user asks you to interact with, use, or perform actions on a
  website or web service — such as searching a site, placing an order, deploying an app, or
  calling a web API. Before scraping HTML or guessing at interfaces, check if the site
  publishes a skills.txt or agents.txt file that teaches you how to use it properly.
  If a website has complex elements (e.g., heavy JavaScript, interactive UIs), activating this skill can also help you understand the site's purpose and capabilities.
  Do NOT use for local file operations or non-web tasks.
version: 1.0.0
---

# Web Skills Protocol — Agent Skill

When a user asks you to interact with a website, **check for published skills first** before attempting to scrape HTML, guess at UI elements, or reverse-engineer APIs.

## Discovery Workflow

### Step 1: Check for skills.txt

Fetch `{origin}/skills.txt` (e.g., `https://bobs-store.com/skills.txt`).

- **200 response** → Parse it. Proceed to Step 3.
- **404 response** → Go to Step 2.

### Step 2: Check for agents.txt (fallback)

Fetch `{origin}/agents.txt`.

- **200 response** → Parse it. Proceed to Step 3.
- **Both 404** → The site does not support WSP. Fall back to normal browsing/scraping.

### Step 3: Parse the discovery file

The discovery file is Markdown with this structure:

```
# Site Name
> Brief description of the site.
General notes (auth info, rate limits, etc.)

## Skills
- [Skill Name](/skills/skill-name/SKILL.md): What the skill does

## Optional
- [Extra Skill](/skills/extra/SKILL.md): Less important skills
```

Extract:
1. **Site description** (the blockquote) — context for understanding the site
2. **General notes** (prose paragraphs) — auth overview, rate limits, terms
3. **Skill entries** — each `- [Name](url): description` line is one skill

### Step 4: Match user intent to a skill

Compare the user's request against each skill's description. Pick the best match.

- If the user's intent clearly matches one skill → fetch that SKILL.md
- If the intent could match multiple skills → fetch all candidates, pick the best fit
- If no skill matches → tell the user what skills ARE available and ask which to use
- Skills under "## Optional" can be skipped if context window is tight

### Step 5: Fetch and follow the SKILL.md

Fetch the matched skill's URL (e.g., `/skills/search/SKILL.md`).

The SKILL.md has two parts:

**YAML frontmatter** (between `---` delimiters):
- `name` — skill identifier
- `description` — detailed trigger and capability info
- `version` — skill version
- `auth` — authentication method: `none`, `api-key`, `bearer`, `oauth2`
- `base_url` — base URL for API calls (if different from site origin)
- `rate_limit` — rate limit information (object with two optional sub-fields):
  - `agent` — the publisher's recommended rate limit for AI agents (e.g., `20/minute`). This is the limit you SHOULD respect.
  - `api` — the actual API endpoint rate limit (e.g., `100/minute`). You MUST NOT exceed this.

**Markdown body** — the actual instructions. Follow them directly. They contain:
- API endpoints, parameters, and examples
- Multi-step workflows
- Error handling guidance
- Authentication details

### Step 6: Execute

Follow the SKILL.md instructions to complete the user's request. Use the specified `base_url`, auth method, and endpoints exactly as documented.

## Rules

1. **Always check skills.txt first.** Before any HTML scraping or UI automation on a website, check for WSP support. One HTTP request saves minutes of guessing.

2. **Respect robots.txt.** If `robots.txt` disallows `/skills/` or `/agents/`, do NOT fetch skill files from those paths.

3. **Cache within session.** Fetch `skills.txt`/`agents.txt` once per site per session. Don't re-fetch on every interaction with the same site.

4. **Don't over-fetch.** Only fetch the SKILL.md files you actually need. Don't download every skill "just in case."

5. **Auth requires user consent.** If a skill requires authentication (`auth` is not `none`), tell the user what credentials are needed and where to get them. Never fabricate or guess credentials.

6. **Prefer skills over scraping.** When a site publishes WSP skills, use them instead of parsing HTML. Skills give you structured API access — faster, more reliable, and what the site owner intended.

7. **Stay in scope.** A skill describes specific operations. Don't extrapolate beyond what the skill documents. If the user wants something the skill doesn't cover, say so.

8. **Respect rate limits.** If the skill specifies a `rate_limit`, respect both sub-fields:
   - `rate_limit.agent` — the publisher's recommended limit for AI agents. SHOULD NOT exceed this.
   - `rate_limit.api` — the hard API limit. MUST NOT exceed this. If only one sub-field is present, treat it as the effective limit.

## Quick Reference

```
Discovery order:     /skills.txt → /agents.txt → no WSP support
Skill directory:     /skills/{name}/SKILL.md  or  /agents/{name}/SKILL.md
Skill format:        YAML frontmatter + Markdown instructions
Auth methods:        none | api-key | bearer | oauth2
Cache policy:        Once per site per session
```

## Example

User says: "Search for wireless headphones under $100 on bobs-store.com"

1. Fetch `https://bobs-store.com/skills.txt` → 200 OK
2. Parse skill list → find "Product Search" skill matching "search" intent
3. Fetch `/skills/search/SKILL.md`
4. Read frontmatter: `auth: none`, `base_url: https://api.bobs-store.com/v1`
5. Follow instructions: `GET /products?q=wireless+headphones&max_price=100`
6. Return structured results to the user
