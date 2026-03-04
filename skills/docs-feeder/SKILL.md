# Docs Feeder

Auto-fetch project documentation and feed it to your AI agent for debugging and learning.

## Triggers

- `docs feed <project>`
- `fetch docs <URL>`

## How It Works

1. **Registry Lookup** — 50+ built-in projects (React, Next.js, Hono, Prisma, Anthropic, etc.)
2. **Fetch Priority:**
   - `/llms-full.txt` → Full LLM-friendly docs
   - `/llms.txt` → Compact version  
   - GitHub README → Fallback
3. **Smart Discovery** — Unknown projects try common patterns (`docs.xxx.com`, `xxx.dev`)
4. **Size Warning** — Alerts when docs exceed 500KB

## Usage

```bash
# By project name (auto-lookup)
node fetch-docs.js nextjs

# By URL (direct fetch)
node fetch-docs.js https://docs.anthropic.com

# Raw content only (no metadata header)
node fetch-docs.js react --raw

# Save to file
node fetch-docs.js prisma --save

# List all supported projects
node fetch-docs.js --list
```

## Built-in Registry

50+ projects including: React, Next.js, Vue, Svelte, Astro, Hono, Express, Fastify, NestJS, Prisma, Drizzle, tRPC, Zod, Tailwind CSS, shadcn/ui, TypeScript, Vite, Bun, Deno, Playwright, Vitest, Supabase, Stripe, Clerk, Anthropic, OpenAI, LangChain, Docker, Kubernetes, Terraform, Rust, Go, Python, FastAPI, Django, and more.

Edit `docs-registry.json` to add your own projects.

## Registry Format

```json
{
  "myproject": {
    "url": "https://myproject.dev",
    "llms": "/llms-full.txt",
    "github": "org/repo",
    "local": "/path/to/local/docs"
  }
}
```

## Workflow

Fetch docs, then describe your problem:

```
→ node fetch-docs.js nextjs
→ [docs loaded into context]

"I'm getting a hydration mismatch error with App Router..."
→ [AI gives solution based on complete documentation]
```

## Why This Works

Most modern doc sites ship `/llms.txt` or `/llms-full.txt` — a single file with the entire knowledge base formatted for LLMs. Instead of searching + reading + understanding docs manually, dump the whole thing into context and let the AI cross-reference.

## Requirements

- Node.js (no external dependencies)
