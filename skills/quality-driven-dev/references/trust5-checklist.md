# TRUST 5 Quality Checklist

## T — Tested

### Automated Checks
- [ ] All acceptance criteria have corresponding tests
- [ ] Tests cover happy path, edge cases, and error cases
- [ ] Test coverage maintained or improved (never decreased)
- [ ] All tests pass (zero failures)
- [ ] No skipped/disabled tests without documented reason

### Manual Review
- [ ] Tests are readable and self-documenting
- [ ] Test names describe behavior, not implementation
- [ ] No test interdependencies (each test runs independently)
- [ ] Mocks/stubs are at boundaries only (not internal)

## R — Readable

### Naming
- [ ] Functions/methods describe WHAT they do (verb + noun)
- [ ] Variables describe WHAT they hold (not type prefixes)
- [ ] Boolean names read as questions (`isActive`, `hasPermission`)
- [ ] No single-letter names (except loop counters `i`, `j`)
- [ ] No abbreviations unless universally understood (`id`, `url`)

### Structure
- [ ] Functions under 30 lines (consider splitting if longer)
- [ ] Max 3 levels of nesting (extract to function if deeper)
- [ ] Early returns for guard clauses
- [ ] Comments explain WHY, not WHAT (code explains WHAT)

## U — Unified

### Style Consistency
- [ ] Matches existing project coding style
- [ ] Same indentation (tabs/spaces) as project
- [ ] Same naming convention (camelCase/snake_case) as project
- [ ] Same file organization pattern as project
- [ ] Linter/formatter passes with zero warnings

### Pattern Consistency
- [ ] Error handling follows project's existing pattern
- [ ] Logging follows project's existing pattern
- [ ] API response format matches existing endpoints
- [ ] Database queries follow project's ORM/query pattern

## S — Secured

### Input Validation
- [ ] All user inputs validated and sanitized
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (output encoding)
- [ ] Path traversal prevention (no user-controlled file paths)

### Authentication & Authorization
- [ ] New endpoints require appropriate auth
- [ ] Authorization checks before data access
- [ ] No hardcoded credentials or API keys
- [ ] Sensitive data not logged

### Dependencies
- [ ] No new dependencies with known vulnerabilities
- [ ] Minimum necessary permissions/scopes

## T — Trackable

### Documentation
- [ ] SPEC document updated with completion status
- [ ] API changes documented (endpoints, params, responses)
- [ ] Breaking changes clearly noted
- [ ] Migration steps documented if needed

### Git Hygiene
- [ ] Commit messages reference SPEC ID
- [ ] Changes limited to SPEC scope (no unrelated modifications)
- [ ] No debug code or console.log left in
- [ ] No commented-out code without explanation

## Quick Pass/Fail

All 5 must be ✅ to pass the quality gate:

```
✅ Tested    — Tests exist, pass, coverage ok
✅ Readable  — Clear names, clean structure
✅ Unified   — Matches project style
✅ Secured   — No vulnerabilities introduced
✅ Trackable — Documented and traceable
```

If ANY is ❌, fix before declaring complete.
