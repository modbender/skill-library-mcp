# Memory Template — Cypress

This skill typically doesn't need persistent memory. Test configuration lives in the project itself (`cypress.config.ts`, `cypress/support/`).

## Project-Level Memory (Optional)

If tracking Cypress patterns across multiple projects, create `~/cypress/memory.md`:

```markdown
# Cypress Memory

## Status
status: ongoing
version: 1.0.0
last: YYYY-MM-DD

## Project Patterns
<!-- How different projects handle testing -->

### Project A
- Selector strategy: data-cy attributes
- Auth: cy.session with API login
- Fixtures: shared user/product data

### Project B
- Selector strategy: data-testid
- Auth: Mock auth state directly
- Component testing enabled

## Learned Preferences
<!-- User's testing style preferences -->
- Prefers explicit waits over implicit
- Uses TypeScript for all tests
- Wants video on CI failures only

## Common Issues Encountered
<!-- Track recurring problems and solutions -->
- Issue: Flaky dropdown tests
  Solution: Wait for animation completion

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning |
|-------|---------|
| `ongoing` | Learning project patterns |
| `complete` | Knows all project conventions |

## Typical Usage

Most Cypress work is project-specific:
- Config in `cypress.config.ts`
- Commands in `cypress/support/commands.ts`
- Fixtures in `cypress/fixtures/`

Memory is optional for cross-project pattern tracking.
