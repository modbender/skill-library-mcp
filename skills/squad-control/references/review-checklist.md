# Code Review Checklist

Use this checklist when reviewing PRs. Not every item applies to every PR — use judgment.

## Correctness
- [ ] Does the code do what the task description asks for?
- [ ] Are there obvious bugs, off-by-one errors, or unhandled edge cases?
- [ ] Are error states handled gracefully (try/catch, fallbacks, user-facing messages)?

## Code Quality
- [ ] Is the code readable and well-structured?
- [ ] Are variable/function names descriptive?
- [ ] No unnecessary duplication — is shared logic extracted appropriately?
- [ ] No dead code, commented-out blocks, or console.logs left in?

## Architecture
- [ ] Does this fit the existing patterns in the codebase?
- [ ] Are new dependencies justified? (Check package.json changes)
- [ ] No over-engineering — is the solution proportional to the problem?

## Security
- [ ] No hardcoded secrets, tokens, or credentials
- [ ] User input is validated/sanitized where applicable
- [ ] API endpoints have proper auth checks

## UI/UX (if applicable)
- [ ] Components are responsive (mobile + desktop)
- [ ] Loading states and error states are handled
- [ ] Accessible (keyboard nav, screen reader basics)
- [ ] Consistent with existing design patterns

## Performance
- [ ] No obvious N+1 queries or unnecessary re-renders
- [ ] Large lists are paginated or virtualized
- [ ] No blocking operations on the main thread

## Review Output Format

After reviewing, provide:

1. **Summary**: 1-2 sentences on overall impression
2. **Issues** (if any): Specific file + line + what's wrong + suggested fix
3. **Nits** (optional): Minor style/preference suggestions (non-blocking)
4. **Verdict**: APPROVE or REQUEST_CHANGES

### Example

```
**Summary:** Clean implementation of toast notifications. Good use of sonner, consistent pattern across all CRUD operations.

**Issues:**
- `src/components/settings.tsx:45` — Missing error toast on API key generation failure. Add a catch handler.

**Nits:**
- Could group the toast messages into a constants file for easier i18n later.

**VERDICT: REQUEST_CHANGES**
Reason: The missing error handler on API key generation could fail silently.
```
