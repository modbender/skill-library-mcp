# Rules Files Configuration

Rules files teach AI your project conventions. Put it once, applies to every interaction.

## File Locations by Tool

| Tool | File |
|------|------|
| Cursor | `.cursorrules` or `.cursor/rules/*.md` |
| Claude Code | `CLAUDE.md` |
| Windsurf | `.windsurfrules` |
| Aider | `.aider.conf.yml` + conventions file |
| GitHub Copilot | `.github/copilot-instructions.md` |

## Template: Basic Rules File

```markdown
# Project: [Name]
Stack: [Framework, Language, DB, etc.]

## Conventions
- [Convention 1]
- [Convention 2]
- [Convention 3]

## File Structure
- /src/components — React components
- /src/lib — Shared utilities
- /src/api — API routes

## Patterns to Follow
- [Reference existing file for pattern]
- [Specific code style requirement]

## Do NOT
- [Anti-pattern 1]
- [Anti-pattern 2]
```

## Example: Next.js SaaS Project

```markdown
# Project: SaaS Dashboard
Stack: Next.js 14, TypeScript strict, Tailwind, Supabase, Stripe

## Conventions
- Use server components by default
- Client components only for interactivity
- All database queries through /lib/db.ts
- Error handling uses custom AppError class
- No console.log — use structured logging (/lib/logger.ts)

## File Structure
- /app — Next.js App Router pages
- /components — React components (ui/ for primitives, features/ for domain)
- /lib — Shared utilities, DB client, auth helpers
- /types — TypeScript type definitions

## Auth
- Supabase Auth for user management
- Middleware in middleware.ts validates sessions
- Protected routes under /app/(dashboard)/

## Payments
- Stripe for billing
- Webhook handler at /api/webhooks/stripe
- Subscription status cached in users table

## Do NOT
- Direct SQL queries outside /lib/db.ts
- Import server-only code in client components
- Store sensitive data in localStorage
- Use deprecated App Router APIs
```

## What to Include

**Always include:**
- Tech stack with versions
- File structure overview
- Naming conventions
- Error handling patterns

**Include if relevant:**
- Auth flow explanation
- API patterns
- Testing requirements
- CI/CD constraints

## Updating Rules Files

When you correct AI behavior:
1. Note what it got wrong
2. Add explicit rule to prevent recurrence
3. Rules file becomes your "common AI mistakes" documentation

## Multi-File Rules (Cursor)

For large projects, split by domain:

```
.cursor/rules/
├── general.md      # Stack, conventions
├── auth.md         # Authentication patterns
├── database.md     # Query patterns, migrations
└── testing.md      # Test conventions
```

Reference in prompts: "Follow rules in .cursor/rules/auth.md"
