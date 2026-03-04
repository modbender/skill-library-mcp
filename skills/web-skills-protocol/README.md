# Web Skills Protocol

> **skills.txt** — Teach AI agents how to use your website.

English | [中文](README_ZH.md)

---

In 1994, `robots.txt` told web crawlers what **not** to do.

In 2024, `llms.txt` told LLMs what content to **read**.

In 2026, `skills.txt` (or `agents.txt`) teaches AI agents how to **act**.

The **Web Skills Protocol (WSP)** is an open standard for websites to publish skill files that teach AI agents how to interact with the site — its APIs, workflows, and capabilities — instead of scraping HTML and guessing.

**WSP does not invent a new format.** AI agent skills — Markdown files with YAML metadata that teach agents how to perform tasks — are already an established standard in the AI agent ecosystem (used by Claude, OpenClaw, and others). WSP simply brings this existing skill format to the web by adding a discovery layer: a `skills.txt` file that tells agents which skills a website offers, just like `robots.txt` tells crawlers which pages to avoid.

## The Problem

AI agents are visiting your website right now. They're parsing HTML, guessing at buttons, and reverse-engineering your API from network traffic. It's fragile, slow, and breaks constantly.

Websites have no standard way to say: *"Hey agent, here's how to actually use us."*

## The Solution

Drop a `skills.txt` (or `agents.txt`) file on your site root. List your capabilities. Publish skill definitions in `/skills/` (or `/agents/`). Done.

```
your-website.com/
├── skills.txt              ← Discovery file (or agents.txt)
└── skills/                 ← Skills directory (or /agents/)
    ├── search/
    │   └── SKILL.md        ← "Here's how to search our products"
    └── order/
        └── SKILL.md        ← "Here's how to place an order"
```

WSP also supports an **alternative convention** using `agents.txt` and `/agents/` — same protocol, same format, different name. Use whichever feels natural. AI agents check both.

AI agents check `skills.txt` (or `agents.txt`) first, find the right skill, and follow your instructions — not their guesses.

## Why Not a New Format?

AI agent skills already exist. Thousands of skills are published and used daily by AI agents like Claude — each one a simple `SKILL.md` file with YAML frontmatter (name, description, version) and Markdown instructions. This format is proven, adopted, and works.

WSP inherits this standard as-is. The only addition is a **web discovery mechanism**:

```
Existing standard:  SKILL.md (YAML frontmatter + Markdown instructions)
WSP adds:           skills.txt → points agents to the right SKILL.md files
```

Think of it this way: WSP is to agent skills what RSS was to XML — not a new format, but a well-known location and discovery convention on top of what already works.

## The Evolution

```
robots.txt (1994)  →  "Dear robot, don't crawl /admin"          →  Access Control
llms.txt   (2024)  →  "Dear LLM, here's our documentation"      →  Content
skills.txt (2026)  →  "Dear agent, here's how to use our API"   →  Capabilities
```

## Install

Add WSP auto-discovery skill to your AI agent — one command:

**OpenClaw**

```bash
mkdir -p ~/.openclaw/workspace/skills/web-skills-protocol && curl -sL \
  https://raw.githubusercontent.com/0xtresser/Web-Skills-Protocol/main/skill/SKILL.md \
  -o ~/.openclaw/workspace/skills/web-skills-protocol/SKILL.md
```

**OpenCode**

```bash
mkdir -p ~/.claude/skills/web-skills-protocol && curl -sL \
  https://raw.githubusercontent.com/0xtresser/Web-Skills-Protocol/main/skill/SKILL.md \
  -o ~/.claude/skills/web-skills-protocol/SKILL.md
```

**Claude Code**

```bash
mkdir -p ~/.claude/skills/web-skills-protocol && curl -sL \
  https://raw.githubusercontent.com/0xtresser/Web-Skills-Protocol/main/skill/SKILL.md \
  -o ~/.claude/skills/web-skills-protocol/SKILL.md
```

**Codex (OpenAI)**

Codex reads instructions from `AGENTS.md`. Append the skill to your project:

```bash
curl -sL \
  https://raw.githubusercontent.com/0xtresser/Web-Skills-Protocol/main/skill/SKILL.md \
  >> AGENTS.md
```


## Quick Start

### 1. Create `/skills.txt` (or `/agents.txt`)

```markdown
# Bob's Online Store

> E-commerce platform for electronics and gadgets.

Product search is open (no auth). Other endpoints require an API key — get one at https://bobs-store.com/developers.

## Skills

- [Product Search](/skills/search/SKILL.md): Search products by keyword, category, or price range
- [Place Order](/skills/order/SKILL.md): Add items to cart and complete checkout via API
```

### 2. Create a Skill

`/skills/search/SKILL.md` (or `/agents/search/SKILL.md`):

```markdown
---
name: search
description: >
  Search and browse products in Bob's Online Store catalog.
  Use when the user wants to find products by keyword, category, price, or brand.
version: 1.0.0
auth: none
base_url: https://api.bobs-store.com/v1
---

# Product Search

## Endpoint

GET /products

## Parameters

| Parameter  | Type   | Required | Description                     |
|------------|--------|----------|---------------------------------|
| q          | string | yes      | Search query                    |
| category   | string | no       | Filter by category              |
| min_price  | number | no       | Minimum price                   |
| max_price  | number | no       | Maximum price                   |
| sort       | string | no       | Sort by: relevance, price, rating |
| page       | number | no       | Page number (default: 1)        |

## Example

Request:
​```
GET /products?q=wireless+headphones&sort=rating&max_price=100
​```

Response:
​```json
{
  "products": [
    {
      "id": "prod_8x7k",
      "name": "SoundWave Pro Wireless Headphones",
      "price": 79.99,
      "rating": 4.7,
      "in_stock": true,
      "url": "https://bobs-store.com/products/prod_8x7k"
    }
  ],
  "total": 42,
  "page": 1,
  "per_page": 20
}
​```
```

That's it. An AI agent visiting your site will:

1. Fetch `/skills.txt` (or `/agents.txt`) → discover available skills
2. Match user intent → pick the right skill
3. Follow your SKILL.md → call your API correctly

## skills.txt Format

The discovery file has a **fixed structure** — not free-form Markdown:

```
# {Site Name}                          ← H1: REQUIRED. Exactly one.

> {Site description}                   ← Blockquote: RECOMMENDED.

{General notes: auth, rate limits...}  ← Prose: OPTIONAL.

## Skills                              ← H2: REQUIRED. At least one section.

- [Skill Name](url): Description      ← List entry: REQUIRED format.
- [Another Skill](url): Description

## Optional                            ← H2 "Optional": agents may skip these.

- [Extra Skill](url): Description
```

**Rules:**

| Element | Format | Required |
|---------|--------|----------|
| Site name | `# Name` (H1) | Yes — exactly one |
| Description | `> text` (blockquote) | Recommended |
| Prose | Paragraphs | No |
| Skill section | `## Section Name` (H2) | Yes — at least one |
| Skill entry | `- [Name](path/SKILL.md): description` | Yes — at least one per section |

The H2 section `## Optional` has special meaning: agents may skip these skills when context is limited. All other H2 sections are treated as primary.

## SKILL.md Format

Each skill file is a standard **AgentSkills** document — the same `SKILL.md` format already used by AI agent platforms (Claude, OpenClaw, and others). WSP does not modify this format.

- **YAML frontmatter** (`---`): `name`, `description`, `version` (required) + optional fields like `auth`, `base_url`, `rate_limit`
  - `rate_limit` is an object with two optional sub-fields: `agent` (recommended limit for AI agents, e.g., `20/minute`) and `api` (actual API rate limit, e.g., `100/minute`)
- **Markdown body**: Instructions for the agent — endpoints, parameters, examples, workflows

If you’ve written an agent skill before, you already know how to write a web skill. See [examples/](examples/) for complete samples.

## For Website Owners

**Why publish skills?**

- **Control the narrative.** Define how AI agents use your site — don't let them guess.
- **Replace scraping.** Structured skills are faster and more reliable than HTML parsing.
- **Reduce load.** One API call beats 50 page fetches.
- **Monetize agent traffic.** Require API keys. Track usage. Offer premium tiers.
- **Progressive adoption.** Start with one `skills.txt` (or `agents.txt`), add skills over time.

## For AI Agent Developers

**Why check for skills?**

- **Structured instructions** instead of parsing unpredictable HTML.
- **Auto-discovery** — one fetch to `/skills.txt` (or `/agents.txt`) reveals all capabilities.
- **Reliable integrations** — follow the site's official instructions, not brittle hacks.
- **Better results** — API calls return structured data, not rendered web pages.

Install the [web-skills-protocol agent skill](skill/SKILL.md) to make your agent automatically discover and use published skills.

## Dual-Path Compatibility

WSP supports two naming conventions — use whichever feels right:

| Component | Primary | Alternative |
|-----------|---------|-------------|
| Discovery file | `/skills.txt` | `/agents.txt` |
| Skills directory | `/skills/` | `/agents/` |
| Skill document | `/skills/{name}/SKILL.md` | `/agents/{name}/SKILL.md` |

Both conventions use the **exact same format**. `skills.txt` frames it as *"what the site can teach"*. `agents.txt` mirrors the `robots.txt` naming — *"talking to agents"*.

**For website owners:** Pick one convention and use it consistently.
**For AI agent developers:** Your agent MUST check both (`skills.txt` first, then `agents.txt`).

See [SPEC.md](SPEC.md) for the full dual-path discovery algorithm.

## Relationship to Other Standards

| Standard     | Purpose                              | Relationship                   |
|-------------|--------------------------------------|--------------------------------|
| robots.txt  | Access control for crawlers          | WSP does NOT override robots.txt. They coexist. |
| llms.txt    | Content summary for LLMs            | Complementary. llms.txt = read. skills.txt/agents.txt = act. |
| OpenAPI     | API schema for developers            | Skills MAY reference OpenAPI specs for detail. |
| MCP         | Runtime protocol for AI tools        | WSP is web-native discovery; MCP is runtime transport. |
| sitemap.xml | Page index for search engines        | skills.txt/agents.txt is a capability index for AI agents. |

## Project Structure

```
Web-Skills-Protocol/
├── README.md           ← You are here
├── README_ZH.md        ← 中文说明
├── SPEC.md             ← Formal protocol specification
├── skill/              ← Agent skill (install this to auto-discover web skills)
│   └── SKILL.md
└── examples/           ← Example implementations
    ├── bobs-store/     ← E-commerce example
    └── devtools-saas/  ← SaaS platform example
```

## Specification

See [SPEC.md](SPEC.md) for the complete protocol specification.

## Live Example

[**awesomeai.info**](https://www.awesomeai.info/) — A dashboard tracking 2800+ AI GitHub repositories and OpenClaw agent skills. This site has adopted WSP in production.

Try it yourself:

```bash
# 1. Discover what the site can do
curl https://www.awesomeai.info/skills.txt

# 2. Read a specific skill
curl https://www.awesomeai.info/skills/explore-ai-repos/SKILL.md

# 3. Call the API as the skill describes
curl "https://awesomeai.info/api/repos?q=llm&sort=stars&pageSize=5"
```

The site publishes two skills — both public, no auth required:

| Skill | Endpoint | What it does |
|-------|----------|--------------|
| [explore-ai-repos](https://www.awesomeai.info/skills/explore-ai-repos/SKILL.md) | `GET /api/repos` | Search/filter AI repositories by keyword, stars, AI score, growth trends |
| [explore-ai-skills](https://www.awesomeai.info/skills/explore-ai-skills/SKILL.md) | `GET /api/skills` | Search/browse OpenClaw agent skills by category, keyword, popularity |

This is what WSP looks like in the real world — a `skills.txt` file and a few `SKILL.md` files, and any AI agent can immediately understand and use the site.

## Examples

See [examples/](examples/) for reference implementations (fictional stores and SaaS platforms).

## Contributing

This is an early-stage open standard. Contributions welcome:

- **Spec feedback** — Open an issue to discuss protocol design
- **Reference implementations** — Add examples for different site types
- **Agent integrations** — Build skills.txt (or agents.txt) support into your AI agent
- **Adopt it** — Publish skills.txt (or agents.txt) on your website

## License

The Web Skills Protocol specification is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/).

Example code and the agent skill are licensed under [MIT](https://opensource.org/licenses/MIT).
