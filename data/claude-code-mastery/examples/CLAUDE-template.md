# Example CLAUDE.md Template

This is a template showing best practices for CLAUDE.md files.
Customize for your project, keeping it concise.

---

# CLAUDE.md

## Build & Test
```bash
npm run dev        # Start development server
npm run test       # Run tests (prefer single file: npm run test -- path/to/file)
npm run typecheck  # TypeScript check (run after changes)
npm run lint       # Lint check
```

## Code Style
- Use ES modules (import/export), not CommonJS (require)
- Destructure imports when possible: `import { foo } from 'bar'`
- Prefer `const` over `let`, never use `var`
- Use TypeScript strict mode patterns

## Testing
- Write tests alongside code, not after
- Prefer integration tests over unit tests for business logic
- Avoid mocks unless testing external dependencies
- Name test files: `*.test.ts` next to source file

## Git Workflow
- Branch naming: `feature/TICKET-123-short-description`
- Commit messages: `[TICKET-123] Short description`
- Always create draft PRs first for review
- Squash commits before merge

## Architecture Notes
- API routes in `src/routes/` follow RESTful patterns
- Shared utilities in `src/utils/` - check before creating new ones
- Database models in `src/models/` use TypeORM
- Validation uses Zod schemas in `src/schemas/`

## Common Gotchas
- Auth tokens expire after 1 hour - check token refresh logic
- Database connections pool max is 10 - don't hold connections
- Redis cache TTL is 5 minutes for user data

## Don't Forget
- IMPORTANT: Run typecheck after code changes
- IMPORTANT: Update API docs if endpoints change

---

## What NOT to Include (Anti-patterns)

❌ Self-evident practices:
```markdown
- Write clean code
- Follow best practices
- Make sure tests pass
```

❌ Standard conventions Claude already knows:
```markdown
- Use camelCase for variables
- Use PascalCase for classes
- Add semicolons in JavaScript
```

❌ Detailed API documentation (link instead):
```markdown
See @docs/api-reference.md for API details
```

❌ Long explanations:
```markdown
<!-- Instead of paragraphs explaining why, just state the rule -->
```

❌ Information that changes frequently:
```markdown
<!-- Version numbers, current sprint items, etc. -->
```
