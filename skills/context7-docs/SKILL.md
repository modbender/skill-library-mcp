---
name: context7-docs
description: >-
  Fetches up-to-date, version-specific documentation and code examples for any
  programming library or framework from Context7. Use this skill when the user
  needs current API docs, code examples, setup guides, or configuration help for
  any library, package, or framework — especially when you are unsure if your
  training data is current. Activate when the user mentions needing docs, examples,
  or asks about library APIs, versions, or configuration.
license: MIT
compatibility: Requires curl, jq, and internet access. Optional CONTEXT7_API_KEY env var for higher rate limits.
metadata:
  author: context7
  version: "1.0"
  source: https://github.com/upstash/context7
allowed-tools: Bash(curl:*) Bash(jq:*) Read
---

# Context7 Documentation Lookup

## Overview

Context7 provides up-to-date, version-specific documentation and code examples for thousands of programming libraries and frameworks. Use this skill whenever you need current documentation that may differ from your training data — especially for fast-moving libraries like Next.js, React, Supabase, LangChain, etc.

## When to Use This Skill

- The user asks about a library's API and you're unsure if your knowledge is current
- The user requests code examples for a specific library version
- The user asks for setup, configuration, or migration guides
- The user mentions "use context7" or asks for up-to-date docs
- You need to verify whether an API or method still exists in the latest version

## Two-Step Workflow

### Step 1: Resolve the Library ID

First, find the Context7-compatible library ID for the library the user is asking about.

```bash
bash scripts/resolve-library.sh --query "How to set up authentication" --library-name "next.js"
```

This returns a list of matching libraries with:
- **Library ID** — e.g., `/vercel/next.js` (use this in Step 2)
- **Name** and **Description**
- **Code Snippets** — number of available examples (prefer higher counts)
- **Benchmark Score** — quality indicator out of 100 (prefer higher)
- **Source Reputation** — High, Medium, Low, or Unknown (prefer High/Medium)
- **Versions** — available version-specific IDs like `/vercel/next.js/v14.3.0`

**Selection criteria** — Pick the library that best matches based on:
1. Name similarity (exact matches first)
2. Description relevance to the user's task
3. Higher Code Snippet count
4. Higher Benchmark Score
5. High or Medium Source Reputation

If the user already provides a library ID in `/org/project` format, skip this step.

### Step 2: Query the Documentation

Use the library ID from Step 1 to fetch relevant documentation:

```bash
bash scripts/query-docs.sh --library-id "/vercel/next.js" --query "How to set up authentication with JWT"
```

This returns documentation text with code examples directly relevant to the query.

### Shortcut: Direct curl

You can also call the API directly without the scripts:

**Search for a library:**
```bash
curl -s "https://context7.com/api/search" \
  -H "Content-Type: application/json" \
  ${CONTEXT7_API_KEY:+-H "Authorization: Bearer $CONTEXT7_API_KEY"} \
  -d '{"query": "How to set up auth", "libraryName": "next.js"}' | jq .
```

**Query documentation:**
```bash
curl -s "https://context7.com/api/context" \
  -H "Content-Type: application/json" \
  ${CONTEXT7_API_KEY:+-H "Authorization: Bearer $CONTEXT7_API_KEY"} \
  -d '{"query": "JWT authentication middleware", "libraryId": "/vercel/next.js"}' | jq .
```

## Important Guidelines

- **Call resolve at most 3 times** per question. If you can't find what you need, use the best result.
- **Call query-docs at most 3 times** per question. Use the best information you have.
- **Be specific with queries.** Good: "How to set up authentication with JWT in Express.js". Bad: "auth".
- **Use versions when relevant.** If the user specifies a version, look for it in the resolve results and use the versioned library ID (e.g., `/vercel/next.js/v14.3.0`).
- **Do NOT include sensitive data** (API keys, passwords, credentials) in your queries — they are sent to the Context7 API.

## Handling Edge Cases

| Situation | Action |
|-----------|--------|
| No results from resolve | Try a different library name or broader search term |
| Multiple good matches | Pick the one with the best name match + highest snippet count |
| User specifies a version | Look for versioned IDs in resolve results |
| Empty docs response | Try a more specific or different query |
| Rate limit hit | Wait a moment and retry, or suggest the user set CONTEXT7_API_KEY |

## Environment Setup

For higher rate limits, set a free API key:

```bash
export CONTEXT7_API_KEY="your-key-here"
```

Get a free key at: https://context7.com/dashboard

## Next Steps

- See [API-REFERENCE.md](references/API-REFERENCE.md) for full endpoint documentation
- See [LIBRARY-ID-FORMAT.md](references/LIBRARY-ID-FORMAT.md) for details on library ID format and versioning
