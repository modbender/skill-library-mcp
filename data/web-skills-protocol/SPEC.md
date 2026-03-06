# Web Skills Protocol (WSP) — Specification v0.1

**Status:** Draft
**Date:** March 2026
**Author:** [To be assigned]
**URI:** `https://github.com/0xtresser/Web-Skills-Protocol`

---

## Abstract

The Web Skills Protocol (WSP) defines a standard mechanism for websites to publish structured skill files that teach AI agents how to interact with the site's capabilities. A website places a discovery file at `/skills.txt` (or alternatively `/agents.txt`) and individual skill definitions under a `/skills/` (or `/agents/`) directory. Each skill is a Markdown document containing metadata and instructions that enable AI agents to perform supported operations — such as searching products, placing orders, or deploying applications — through the site's official interfaces rather than through fragile HTML scraping.

Critically, WSP does not define a new skill document format. The `SKILL.md` format — YAML frontmatter with metadata plus Markdown body with instructions — is an existing standard already widely adopted in the AI agent ecosystem (Claude, OpenClaw, and others). WSP’s contribution is a **web discovery layer**: a well-known file (`skills.txt`/`agents.txt`) and directory convention (`/skills/`/`/agents/`) that allows websites to surface their capabilities to any conforming AI agent.

WSP supports **dual discovery paths** for maximum compatibility: both `skills.txt` and `agents.txt` are recognized as valid discovery files, and both `/skills/` and `/agents/` are recognized as valid skill directories. This allows publishers to choose the naming convention that best fits their mental model — whether "skills" (what the site can teach) or "agents" (who the site is talking to, mirroring `robots.txt`).

WSP is complementary to existing web standards: `robots.txt` governs access control, `llms.txt` provides content for reading, and `skills.txt`/`agents.txt` provides capabilities for action.

## 1. Introduction

### 1.1 Background

The web has evolved through three phases of machine interaction:

1. **Access control era (1994–):** `robots.txt` (RFC 9309) tells web crawlers which pages they may or may not access.
2. **Content era (2024–):** `llms.txt` provides curated, LLM-friendly content summaries for language models to read and understand.
3. **Capability era (2026–):** `skills.txt`/`agents.txt` teaches AI agents how to perform supported operations on a website.

As AI agents increasingly interact with websites on behalf of users, a gap exists between what a site offers and what an agent can reliably discover. Agents currently rely on HTML scraping, reverse-engineering network requests, or prompting users for manual steps. These methods are fragile, inefficient, and give website operators no control over how agents interact with their platforms.

### 1.2.1 What WSP Does NOT Do

WSP does not invent a new skill file format. The `SKILL.md` document format — consisting of YAML frontmatter (`name`, `description`, `version`, and optional fields) followed by a Markdown instruction body — is an existing, proven standard used by AI agent platforms. WSP inherits this format unchanged.

WSP’s sole innovation is the **discovery mechanism**: placing a `skills.txt` (or `agents.txt`) file at a website’s root to index available skills, analogous to how `robots.txt` indexes access rules and `sitemap.xml` indexes pages.

### 1.2 Problem Statement

- AI agents have no standard way to discover what operations a website supports.
- Websites have no standard way to communicate their capabilities to AI agents.
- HTML scraping is unreliable, resource-intensive, and breaks with UI changes.
- API documentation, when it exists, is designed for human developers — not for AI agents to consume at runtime.

### 1.3 Design Principles

1. **Inherit, don't invent.** The SKILL.md format is an existing standard. WSP reuses it unchanged and only adds a web discovery layer.
2. **Simplicity.** A single Markdown file at a well-known path is the minimum viable implementation.
3. **Progressive adoption.** Start with a single discovery file; add individual skill files as needed.
4. **Markdown-native.** Both discovery and skill files use Markdown, which is human-readable and LLM-friendly.
5. **CDN-friendly.** All files are static and independently cacheable.
6. **Composable.** WSP works alongside robots.txt, llms.txt, OpenAPI, and MCP without replacing any of them.
7. **Voluntary compliance.** Like robots.txt, WSP relies on good-faith adoption by both publishers and consumers.
8. **Dual-path compatibility.** Both `skills.txt`/`/skills/` and `agents.txt`/`/agents/` conventions are supported to maximize adoption.

## 2. Terminology

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in RFC 2119.

| Term | Definition |
|------|-----------|
| **Skill** | A structured document that teaches an AI agent how to perform a specific operation on a website. |
| **Discovery File** | A `skills.txt` or `agents.txt` file located at a website's root path, listing available skills. |
| **Skill Document** | An individual `SKILL.md` file containing metadata and instructions for one skill. |
| **Publisher** | The website or service that creates and hosts skill files. |
| **Consumer** | The AI agent or application that discovers and follows skill files. |
| **Skill Directory** | The `/skills/` or `/agents/` path on a website where individual skill subdirectories are organized. |

## 3. Discovery Mechanism

### 3.1 Discovery File Location

The discovery file MUST be located at one of the following root paths of the website's origin:

| Path | Convention | Notes |
|------|-----------|-------|
| `/skills.txt` | **Primary** | Describes what the site can teach. RECOMMENDED. |
| `/agents.txt` | **Alternative** | Mirrors `robots.txt` naming. Equally valid. |

Both paths follow the same format and are semantically equivalent. A publisher MUST serve at least one. A publisher MAY serve both (with identical content).

```
https://example.com/skills.txt    ← Primary convention
https://example.com/agents.txt    ← Alternative convention (same protocol)
```

A discovery file applies to a single origin. For websites with multiple subdomains, each subdomain MAY have its own discovery file.

#### Consumer Discovery Order

A conforming consumer MUST check for discovery files in the following order:

1. Fetch `{origin}/skills.txt`
2. If 404, fetch `{origin}/agents.txt`
3. If both return 404, the site does not support WSP

If a site serves both files, the consumer SHOULD use whichever it finds first (i.e., `skills.txt`).

### 3.2 Discovery File Format

The discovery file is a Markdown document with the following structure:

1. **H1 heading** (REQUIRED): The name of the site or service.
2. **Blockquote** (RECOMMENDED): A brief description of the site, containing key information for understanding the available skills.
3. **Prose sections** (OPTIONAL): Zero or more paragraphs providing general context — such as authentication overview, terms of use, or general notes.
4. **H2 sections** (REQUIRED): One or more sections containing skill lists.

Each skill list entry is a Markdown list item with the format:

```markdown
- [Skill Name](/skills/{skill-name}/SKILL.md): Brief description of the skill
```

Or, using the agents convention:

```markdown
- [Skill Name](/agents/{skill-name}/SKILL.md): Brief description of the skill
```

The link MUST be a relative or absolute URL pointing to the skill's `SKILL.md` file. The description after the colon SHOULD summarize what the skill does and when an agent should use it.

### 3.3 Special Sections

An H2 section titled "Optional" has special meaning: skills listed under this section MAY be skipped by consumers that need a shorter context or have limited capabilities. Publishers SHOULD use this section for secondary or advanced skills that are not essential for basic interaction.

### 3.4 Discovery File Examples

**Using the `/skills/` convention (skills.txt):**

```markdown
# Bob's Online Store

> Online store for electronics, gadgets, and accessories.

Product search is open (no auth required). All other endpoints require an API key. Get one at https://bobs-store.com/developers.
Rate limits: 100 requests/minute for search, 20 requests/minute for orders.

## Skills

- [Product Search](/skills/search/SKILL.md): Search and browse products by keyword, category, price range, or brand. Returns structured product data including prices, ratings, and availability.
- [Place Order](/skills/order/SKILL.md): Add items to cart, apply coupons, select shipping method, and complete checkout via API.
- [Track Order](/skills/tracking/SKILL.md): Check order status, estimated delivery, and tracking information.

## Optional

- [Product Reviews](/skills/reviews/SKILL.md): Read and submit product reviews and ratings.
- [Wishlist](/skills/wishlist/SKILL.md): Manage user wishlists.
```

**Using the `/agents/` convention (agents.txt):**

```markdown
# Bob's Online Store

> Online store for electronics, gadgets, and accessories.

Product search is open (no auth). API key required for other endpoints. Get one at https://bobs-store.com/developers.

## Skills

- [Product Search](/agents/search/SKILL.md): Search products by keyword, category, or price range.
- [Place Order](/agents/order/SKILL.md): Complete checkout via API.
```

Both formats are semantically identical — only the directory path differs.

### 3.5 Discovery Process

A consumer SHOULD follow this process when interacting with a website:

1. Fetch `{origin}/skills.txt`. If 404, fetch `{origin}/agents.txt`.
2. If the response status is 200 and the content is valid Markdown, parse the skill list.
3. If both return 404 or error, the site does not support WSP. The consumer SHOULD fall back to other interaction methods.
4. Match the user's intent against available skill descriptions.
5. Fetch the matching skill's `SKILL.md` file.
6. Follow the instructions in the skill document.

Consumers SHOULD cache the discovery file for the duration of a session or according to HTTP cache headers to avoid redundant fetches.

## 4. Skills Directory

### 4.1 Directory Location

Skills SHOULD be organized under one of the following paths at the website's origin:

| Path | Convention | Notes |
|------|-----------|-------|
| `/skills/` | **Primary** | RECOMMENDED. Consistent with `skills.txt`. |
| `/agents/` | **Alternative** | Consistent with `agents.txt`. Equally valid. |

The directory path SHOULD be consistent with the discovery file name:

- If using `skills.txt` → use `/skills/`
- If using `agents.txt` → use `/agents/`

However, the discovery file's skill entry links are authoritative — a consumer MUST follow the URLs specified in the discovery file regardless of which directory convention is used.

### 4.2 Directory Structure

Each skill occupies its own subdirectory:

```
/skills/ convention:                /agents/ convention:

/skills/                            /agents/
├── search/                         ├── search/
│   ├── SKILL.md        ← Required │   ├── SKILL.md        ← Required
│   ├── references/     ← Optional │   ├── references/     ← Optional
│   │   └── filters.md             │   │   └── filters.md
│   └── scripts/        ← Optional │   └── scripts/        ← Optional
│       └── bulk.py                 │       └── bulk.py
├── order/                          ├── order/
│   └── SKILL.md                    │   └── SKILL.md
└── tracking/                       └── tracking/
    └── SKILL.md                        └── SKILL.md
```

### 4.3 Subdirectory Naming

Skill subdirectory names MUST use kebab-case (lowercase with hyphens) and MUST match the `name` field in the skill's YAML frontmatter.

### 4.4 Auxiliary Files

Each skill subdirectory MAY contain additional resources:

| Directory      | Purpose                                       | Loaded by consumer? |
|---------------|-----------------------------------------------|---------------------|
| `references/` | Additional documentation, loaded on demand    | On demand           |
| `scripts/`    | Executable code for the agent to run          | On demand           |
| `assets/`     | Templates, images, and other output resources | As needed           |

Consumers SHOULD only fetch auxiliary files when explicitly referenced in the skill document.

## 5. Skill Document Format

### 5.1 File Name and Location

A skill document MUST be named `SKILL.md` and MUST be located in the skill's subdirectory:

```
/skills/{skill-name}/SKILL.md    ← Using /skills/ convention
/agents/{skill-name}/SKILL.md    ← Using /agents/ convention
```

The filename `SKILL.md` is the same regardless of which directory convention is used.

### 5.2 Structure

A skill document consists of two parts:

1. **YAML Frontmatter**: Metadata enclosed in `---` delimiters.
2. **Markdown Body**: Instructions for the AI agent.

### 5.3 YAML Frontmatter

#### Required Fields

| Field         | Type   | Description |
|--------------|--------|-------------|
| `name`       | string | Unique identifier for this skill. MUST be kebab-case. MUST match the subdirectory name. |
| `description`| string | A detailed description of what this skill does and when it should be triggered. This is the primary field consumers use to match user intent to skills. |
| `version`    | string | Semantic version of this skill (e.g., "1.0.0"). |

#### Optional Fields

| Field         | Type   | Description |
|--------------|--------|-------------|
| `author`     | string | Name of the publisher or organization. |
| `api_version`| string | Version of the underlying API this skill targets. |
| `auth`       | string | Authentication method: `none`, `api-key`, `bearer`, `oauth2`. |
| `rate_limit` | object | Rate limit information. Contains `agent` (recommended limit for AI agents) and/or `api` (underlying API rate limit). See below. |
| `base_url`   | string | Base URL for API calls, if different from the site origin. |
| `contact`    | string | Contact email or URL for skill-related issues. |

#### Example Frontmatter

```yaml
---
name: search
description: >
  Search and browse products in Bob's Online Store catalog.
  Use when the user wants to find products by keyword, category, price range,
  or brand. Returns structured product data including prices, ratings,
  and stock availability. Supports pagination and sorting.
version: 1.0.0
auth: none
rate_limit:
  agent: 20/minute
  api: 100/minute
base_url: https://api.bobs-store.com/v1
---
```

### 5.4 Markdown Body

The Markdown body contains instructions that teach the AI agent how to perform the skill. There is no required structure for the body, but the following sections are RECOMMENDED:

#### Recommended Sections

| Section              | Purpose                                         |
|---------------------|------------------------------------------------|
| Endpoint(s)         | HTTP method, path, and purpose of each endpoint |
| Parameters          | Request parameters with types and descriptions  |
| Request Examples    | Complete request examples with headers          |
| Response Format     | Response structure with field descriptions       |
| Error Handling      | Common error codes and how to handle them       |
| Workflow            | Multi-step processes with ordering              |
| Authentication      | How to authenticate (if not fully covered by frontmatter) |
| Notes / Constraints | Rate limits, pagination, special behaviors      |

#### Writing Guidelines

Publishers SHOULD follow these guidelines when writing skill documents:

1. **Be imperative.** Write instructions the agent can follow directly: "Send a GET request to..." not "The GET endpoint can be used to..."
2. **Use code blocks.** Show complete request/response examples.
3. **Only teach what's unique.** Do not explain HTTP, JSON, or general programming concepts. Focus on site-specific details.
4. **Keep it concise.** Aim for under 300 lines. Move detailed reference material to `references/`.
5. **Include error handling.** Show how to handle common errors (auth failures, rate limits, validation errors).
6. **Specify required vs optional parameters.** Use tables for clarity.

### 5.5 Description Field Guidelines

The `description` field is the most critical field in the frontmatter. It determines whether a consumer activates this skill for a given user request.

A good description MUST include:
- **What** the skill does (its primary function)
- **When** to use it (trigger conditions)
- **Specific scenarios** that should activate this skill

A good description SHOULD include:
- What the skill does **not** do (exclusion conditions)
- Key capabilities or limitations

Example of a good description:
```yaml
description: >
  Search and browse products in Bob's Online Store catalog. Use when the user
  wants to find products by keyword, category, price range, or brand.
  Returns structured product data including prices, ratings, and availability.
  Supports pagination and sorting. Do NOT use for order management or
  account operations — use the order or account skills instead.
```

Example of a bad description:
```yaml
description: Product search functionality.
```

## 6. Authentication and Authorization

### 6.1 Declaring Auth Requirements

Skills that require authentication MUST declare the auth method in the YAML frontmatter using the `auth` field.

| Auth Value  | Description                                             |
|-------------|---------------------------------------------------------|
| `none`      | No authentication required.                             |
| `api-key`   | Requires an API key, typically sent as a header or query parameter. |
| `bearer`    | Requires a Bearer token in the Authorization header.    |
| `oauth2`    | Requires OAuth 2.0 authentication flow.                |

### 6.2 Auth Details in Body

When `auth` is not `none`, the skill document body SHOULD include an "Authentication" section explaining:
- How to obtain credentials (link to developer portal, registration page)
- How to include credentials in requests (header name, parameter format)
- Token refresh procedures (for oauth2)

### 6.3 Security Requirements

Publishers MUST NOT embed actual credentials, API keys, or secrets in skill documents.

Consumers MUST NOT store or transmit credentials obtained through skill instructions without explicit user consent.

Consumers SHOULD prompt the user for credentials when a skill requires authentication, rather than attempting to bypass auth mechanisms.

## 7. Versioning

### 7.1 Skill Versioning

Individual skill documents MUST include a `version` field in the YAML frontmatter following Semantic Versioning (SemVer):

- **MAJOR** version: Incompatible changes to the skill's interface.
- **MINOR** version: Backward-compatible additions.
- **PATCH** version: Backward-compatible fixes.

### 7.2 Discovery File Versioning

The discovery file does not require a version field. Its content is implicitly versioned by the individual skill versions it references.

### 7.3 Change Notification

Publishers SHOULD update the `version` field in skill documents when making changes. There is no push notification mechanism; consumers discover changes by re-fetching skill documents.

## 8. Caching and Performance

### 8.1 Caching Behavior

All WSP files (discovery file and skill documents) are static resources and SHOULD be served with appropriate HTTP cache headers.

**Recommended cache durations:**

| Resource                  | Recommended Cache-Control          |
|--------------------------|-------------------------------------|
| skills.txt / agents.txt  | `public, max-age=3600` (1 hour)    |
| SKILL.md                 | `public, max-age=86400` (1 day)    |
| references/*             | `public, max-age=86400` (1 day)    |

### 8.2 Consumer Caching

Consumers SHOULD cache the discovery file for the duration of a user session. Within a single session, a consumer SHOULD NOT fetch `skills.txt`/`agents.txt` more than once for the same origin.

Consumers MAY cache individual skill documents across sessions, using standard HTTP caching mechanisms (ETag, Last-Modified).

### 8.3 File Size Limits

The discovery file SHOULD NOT exceed 50 KB.

Individual skill documents (`SKILL.md`) SHOULD NOT exceed 100 KB. For skill documents approaching this limit, publishers SHOULD move detailed content to `references/` files.

## 9. Relationship to Other Standards

### 9.1 robots.txt (RFC 9309)

WSP and robots.txt serve different purposes and MUST NOT conflict:

- `robots.txt` governs **access** — which paths crawlers may visit.
- `skills.txt`/`agents.txt` governs **capability** — how agents may interact with the site.

A website MAY publish both `robots.txt` and `skills.txt`/`agents.txt`. If `robots.txt` disallows access to `/skills/` or `/agents/`, consumers MUST respect that directive — the access control layer takes precedence.

### 9.2 llms.txt

WSP and llms.txt are complementary:

- `llms.txt` provides content for **reading** — documentation, explanations, context.
- `skills.txt`/`agents.txt` provides instructions for **acting** — API calls, workflows, operations.

A website MAY publish both. In fact, `llms.txt` can help an agent understand the site, while `skills.txt`/`agents.txt` enables the agent to operate on it.

### 9.3 OpenAPI / Swagger

Skills MAY reference OpenAPI specifications for detailed API schemas. WSP provides the "task workflow" layer above raw API documentation:

- OpenAPI describes endpoints, schemas, and parameters (the "what").
- WSP describes task workflows, decision logic, and best practices (the "how" and "when").

A skill document MAY include a reference to an OpenAPI spec:
```markdown
For complete API schema, see our [OpenAPI spec](https://api.example.com/openapi.json).
```

### 9.4 MCP (Model Context Protocol)

MCP is a runtime protocol for connecting AI agents to tools. WSP is a web-native discovery standard for publishing capabilities.

- WSP is **publisher-side** — the website defines its skills.
- MCP is **consumer-side** — the agent runtime connects to tool servers.

Skills published via WSP can be implemented as MCP tool servers, but WSP does not require MCP and functions independently.

### 9.5 sitemap.xml

`sitemap.xml` lists pages for search engine indexing. `skills.txt`/`agents.txt` lists capabilities for AI agent interaction. They serve different audiences and can coexist without conflict.

## 10. Conformance Requirements

### 10.1 Publisher Requirements

A conforming publisher:

- MUST serve the discovery file at `{origin}/skills.txt` and/or `{origin}/agents.txt` with a 200 status code and `text/plain` or `text/markdown` content type.
- MUST include at least one skill entry in the discovery file.
- MUST provide a valid `SKILL.md` file at the URL referenced in each skill entry.
- MUST include `name`, `description`, and `version` fields in each skill's YAML frontmatter.
- MUST ensure the `name` field matches the skill's subdirectory name.
- MUST NOT embed credentials or secrets in skill documents.
- SHOULD serve skill files with appropriate cache headers.
- SHOULD keep skill documents under 100 KB.

### 10.2 Consumer Requirements

A conforming consumer:

- MUST check for discovery files in order: `{origin}/skills.txt` first, then `{origin}/agents.txt`.
- MUST gracefully handle 404 responses (site does not support WSP).
- MUST respect `robots.txt` directives — if `/skills/` or `/agents/` is disallowed, do not fetch skill files.
- MUST validate YAML frontmatter before executing skill instructions.
- MUST NOT execute skill instructions that would bypass the site's stated authentication requirements.
- SHOULD cache the discovery file for the duration of a session.
- SHOULD match user intent against skill descriptions before fetching individual skill documents.
- SHOULD prefer skill-based interaction over HTML scraping when skills are available.

## 11. Security Considerations

### 11.1 Skill Injection

Skill documents contain instructions that AI agents follow. A compromised skill document could instruct an agent to:
- Exfiltrate user data to a third-party URL.
- Make unintended purchases or transactions.
- Bypass authentication or authorization controls.

Consumers SHOULD validate that skill documents only reference URLs within the publisher's origin or explicitly declared `base_url`. Consumers MUST prompt users before performing sensitive operations (payments, account changes, data deletion) regardless of skill instructions.

### 11.2 Content Integrity

Publishers MAY implement content integrity by serving skill files over HTTPS (RECOMMENDED) and providing checksums in the discovery file.

Consumers MUST fetch skill files over HTTPS in production environments. Consumers SHOULD warn users when fetching skills over plain HTTP.

### 11.3 Rate Limiting and Abuse

Skills MAY declare two types of rate limits in the `rate_limit` frontmatter field:

| Sub-field | Meaning |
|-----------|---------|
| `agent`   | The publisher's recommended rate limit for AI agents calling this skill. This is the limit agents SHOULD respect. It may be stricter than the API limit to prevent abuse or preserve resources for human users. |
| `api`     | The actual technical rate limit of the underlying API. If an agent exceeds this, requests will be rejected (HTTP 429). |

Consumers MUST NOT exceed `rate_limit.api` if declared. Consumers SHOULD NOT exceed `rate_limit.agent` if declared.

If only one sub-field is present, consumers SHOULD treat it as the effective limit. If both are present, `rate_limit.agent` takes precedence (it is typically the stricter of the two).

Publishers SHOULD implement server-side rate limiting in addition to declaring limits in skill documents, as consumer compliance is voluntary.

### 11.4 Scope Limitation

Skill documents describe supported operations. They do not grant additional permissions. A skill that describes an order API does not authorize the agent to place orders — the agent still needs valid credentials and user consent.

## 12. IANA Considerations

This section is reserved for future IANA registration if this specification progresses to an RFC.

Potential registrations:
- Well-Known URI: `/.well-known/skills` or `/.well-known/agents` (alternative discovery paths)
- Media Type: `text/markdown; profile="skill"` (skill-specific content type)

## 13. Examples

### 13.1 Minimal Discovery File

The simplest valid discovery file (as either `skills.txt` or `agents.txt`):

```markdown
# My Website

## Skills

- [Search](/skills/search/SKILL.md): Search site content
```

### 13.2 Complete skills.txt (using /skills/ convention)

```markdown
# DevTools Cloud

> Cloud deployment platform for web applications. Deploy from Git in seconds.
> Supports Node.js, Python, Go, and Rust.

Authentication via OAuth 2.0. Register at https://devtools.cloud/developers to obtain client credentials.

## Skills

- [Deploy Application](/skills/deploy/SKILL.md): Deploy web applications from Git repositories with automatic build detection and zero-downtime deployment.
- [Manage Domains](/skills/domains/SKILL.md): Add custom domains, configure DNS, and manage SSL certificates for deployed applications.
- [View Logs](/skills/logs/SKILL.md): Stream application logs, filter by severity, and search log history.

## Optional

- [Team Management](/skills/teams/SKILL.md): Invite team members, manage roles, and configure access permissions.
```

### 13.3 Complete agents.txt (using /agents/ convention)

```markdown
# DevTools Cloud

> Cloud deployment platform for web applications. Deploy from Git in seconds.

Auth: OAuth 2.0. Register at https://devtools.cloud/developers.

## Skills

- [Deploy Application](/agents/deploy/SKILL.md): Deploy web apps from Git with auto build detection.
- [Manage Domains](/agents/domains/SKILL.md): Custom domains, DNS, and SSL management.
- [View Logs](/agents/logs/SKILL.md): Stream and search application logs.
```

### 13.4 Complete SKILL.md

```markdown
---
name: deploy
description: >
  Deploy web applications to DevTools Cloud from Git repositories.
  Use when the user wants to deploy, ship, publish, or launch a web app.
  Supports Node.js, Python, Go, and Rust with automatic build detection.
  Handles zero-downtime deployments with automatic rollback on failure.
version: 2.1.0
auth: oauth2
rate_limit:
  agent: 5/minute
  api: 10/minute
base_url: https://api.devtools.cloud/v2
---

# Deploy Application

## Prerequisites

- OAuth 2.0 access token (see https://devtools.cloud/docs/oauth)
- A Git repository URL (GitHub, GitLab, or Bitbucket)

## Workflow

### Step 1: Create Application (if new)

POST /apps

```json
{
  "name": "my-app",
  "git_url": "https://github.com/user/repo",
  "branch": "main",
  "runtime": "nodejs"
}
```

Response (201 Created):
```json
{
  "id": "app_k8x7m",
  "name": "my-app",
  "status": "created",
  "url": "https://my-app.devtools.cloud"
}
```

### Step 2: Trigger Deployment

POST /apps/{app_id}/deployments

```json
{
  "branch": "main",
  "env_vars": {
    "NODE_ENV": "production"
  }
}
```

Response (202 Accepted):
```json
{
  "id": "deploy_9f3n",
  "status": "building",
  "started_at": "2026-03-04T10:30:00Z"
}
```

### Step 3: Check Deployment Status

Poll until status is "live" or "failed":

GET /apps/{app_id}/deployments/{deploy_id}

Response:
```json
{
  "id": "deploy_9f3n",
  "status": "live",
  "url": "https://my-app.devtools.cloud",
  "build_time_seconds": 47
}
```

Possible status values: building → deploying → live | failed

### Step 4: View Logs (if needed)

GET /apps/{app_id}/logs?lines=50&level=error

## Error Handling

| Code | Meaning                | Action                        |
|------|------------------------|-------------------------------|
| 400  | Invalid request        | Check required fields         |
| 401  | Auth failed            | Refresh OAuth token           |
| 404  | App not found          | Verify app_id                 |
| 409  | Deployment in progress | Wait for current deploy       |
| 429  | Rate limited           | Wait and retry after header   |
| 500  | Server error           | Retry with exponential backoff|

## Notes

- Deployments are atomic: if the build fails, the previous version stays live.
- Environment variables set in Step 2 persist across deployments.
- Build detection is automatic — the platform reads package.json, requirements.txt, go.mod, or Cargo.toml.
```

## Appendix A: Discovery File Grammar

```
discovery-file  = site-header [site-desc] [prose-sections] skill-sections
site-header     = "# " site-name NEWLINE
site-desc       = "> " description-text NEWLINE
prose-sections  = *(paragraph NEWLINE)
skill-sections  = 1*(section-header skill-list)
section-header  = "## " section-name NEWLINE
skill-list      = 1*(skill-entry NEWLINE)
skill-entry     = "- [" skill-name "](" skill-url ")" [":" skill-desc]
skill-name      = 1*VISIBLE-CHAR
skill-url       = relative-url / absolute-url  ; path under /skills/ or /agents/
skill-desc      = 1*UTF8-CHAR
```

## Appendix B: SKILL.md Frontmatter Schema

```yaml
# Required fields
name: string          # kebab-case identifier, matches directory name
description: string   # Trigger description (what, when, and for whom)
version: string       # Semantic version (MAJOR.MINOR.PATCH)

# Optional fields
author: string        # Publisher name or organization
api_version: string   # Version of the underlying API
auth: string          # One of: none, api-key, bearer, oauth2
rate_limit:              # Rate limit information (object)
  agent: string          # Recommended limit for AI agents (e.g., "20/minute")
  api: string            # Actual API rate limit (e.g., "100/minute")
base_url: string      # Base URL for API calls (if not site origin)
contact: string       # Contact for skill-related issues (email or URL)
```

## Appendix C: Content Types

| File                     | Recommended Content-Type              |
|-------------------------|---------------------------------------|
| skills.txt / agents.txt | `text/plain; charset=utf-8` or `text/markdown; charset=utf-8` |
| SKILL.md                | `text/markdown; charset=utf-8`        |

## Appendix D: Path Convention Summary

| Component       | Primary Convention | Alternative Convention |
|----------------|-------------------|----------------------|
| Discovery file | `/skills.txt`     | `/agents.txt`        |
| Skill directory| `/skills/`        | `/agents/`           |
| Skill document | `/skills/{name}/SKILL.md` | `/agents/{name}/SKILL.md` |

Publishers choose one convention. Consumers MUST support both.

## Appendix E: Changelog

### v0.1 (March 2026)
- Initial draft specification.
- Dual-path discovery: both `skills.txt` and `agents.txt` supported.
- Dual-path directories: both `/skills/` and `/agents/` supported.
