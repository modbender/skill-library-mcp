# Context7 Library ID Format

## Overview

Context7 uses a unique library ID format to identify documentation sources. Understanding this format helps you query the right docs efficiently.

## Format

```
/org/project
```

or with a specific version:

```
/org/project/version
```

### Components

| Component | Description | Example |
|-----------|-------------|---------|
| `org` | The organization or author of the library | `vercel`, `mongodb`, `facebook` |
| `project` | The library or project name | `next.js`, `docs`, `react` |
| `version` | Optional version identifier | `v14.3.0`, `v5.0.0-canary.87` |

## Examples

### Common Library IDs

| Library | Context7 ID |
|---------|-------------|
| Next.js | `/vercel/next.js` |
| React | `/facebook/react` |
| Express | `/expressjs/express` |
| MongoDB | `/mongodb/docs` |
| Supabase | `/supabase/supabase` |
| LangChain (Python) | `/langchain-ai/langchainjs` |
| Tailwind CSS | `/tailwindlabs/tailwindcss` |
| Prisma | `/prisma/docs` |

### Version-Specific IDs

| Library + Version | Context7 ID |
|-------------------|-------------|
| Next.js 14.3.0 | `/vercel/next.js/v14.3.0` |
| Next.js canary | `/vercel/next.js/v14.3.0-canary.87` |

## How to Get a Library ID

### Option 1: Use the resolve-library script

```bash
bash scripts/resolve-library.sh --query "your question" --library-name "library-name"
```

The output will include the library ID for each match.

### Option 2: User provides it directly

Users may provide a library ID directly in their prompt using the slash format:

```
Use library /supabase/supabase for docs
```

When a user provides an ID in `/org/project` format, you can skip the resolve step and go directly to querying docs.

### Option 3: Construct from the GitHub URL

For many libraries, the Context7 ID mirrors the GitHub repository path:

```
https://github.com/vercel/next.js  →  /vercel/next.js
https://github.com/expressjs/express  →  /expressjs/express
```

However, this is not guaranteed — some libraries use different IDs (e.g., `/mongodb/docs` instead of `/mongodb/mongo`). Always verify with the resolve step if unsure.

## Using Versions

When a user asks about a specific version:

1. Run the resolve step to see available versions
2. Look for the version in the `versions` field of the results
3. Use the versioned ID (e.g., `/vercel/next.js/v14.3.0`) in your query

If the exact version is not listed, use the base library ID — Context7 will return the latest docs by default.

## Important Notes

- Library IDs are **case-sensitive**
- Library IDs always **start with `/`**
- Not every GitHub repo maps directly to a Context7 library ID — always verify with resolve if unsure
- The resolve endpoint ranks results by relevance to your query, so the first result is usually the best match
