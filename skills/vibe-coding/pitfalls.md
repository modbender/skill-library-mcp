# Common Pitfalls and Fixes

These are HARD FAILURES — bugs, crashes, security issues. Not style preferences.

## Architecture Pitfalls

### Over-Engineering Simple Solutions
**What happens**: Ask for simple feature, get 5 abstraction layers.
**Fix prompt**: "Simplest possible implementation. No abstractions unless I ask."

### Context Amnesia
**What happens**: AI "forgets" what you said 3 messages ago.
**Fix**: 
- Keep sessions focused (one feature per session)
- Restart with summary: "We're building X. So far: [done]. Next: [task]"

### Phantom Imports
**What happens**: AI uses libraries not installed.
**Fix prompt**: "Only use dependencies already in package.json. List any new ones needed."

### Wrong API Versions
**What happens**: Uses deprecated APIs or wrong library version syntax.
**Fix**: Include versions in rules file. Prompt: "Check [library] docs for v[X] syntax."

## Code Quality Pitfalls

### Compiles But Fails at Runtime
**What happens**: TypeScript happy, app crashes.
**Fix**: "After changes, describe how to test this manually."

### Silent Data Corruption
**What happens**: Code runs but produces wrong results.
**Fix**: Add assertions. "Add validation that [expected condition] is true."

### Dead Code Accumulation
**What happens**: Old code left behind after refactors.
**Fix**: "Show me any code that's no longer used after this change."

## Security Pitfalls

### Vibe Coding Auth
**DO NOT vibe code authentication.** Review every line.

**Common AI auth mistakes:**
- JWT stored in localStorage (XSS vulnerable)
- No CSRF protection
- Passwords compared with `===` instead of timing-safe compare
- Session tokens in URL parameters

### Exposed Secrets
**What happens**: AI hardcodes API keys or shows them in examples.
**Fix**: "Use environment variables. Never hardcode secrets."

### SQL Injection
**What happens**: String concatenation in queries.
**Fix**: "Use parameterized queries only. No string interpolation in SQL."

## Testing Pitfalls

### Tests That Prove Nothing
**What happens**: Tests pass but don't catch bugs.
**Verify**: "What bug would this test catch? Show me input that would fail."

### Over-Mocked Tests
**What happens**: Mocks hide real integration bugs.
**Fix**: "Write integration test that uses real [database/API]."

## Workflow Pitfalls

### Infinite Error Loop
**What happens**: Fix one error, create another, repeat.
**Fix**: Stop. "Let's start fresh. Here's what I need: [requirement]."

### Scope Creep Per Prompt
**What happens**: Each prompt adds more than asked.
**Fix**: "Only do exactly what I asked. Nothing extra."

### Lost Progress
**What happens**: Code worked, then broke after more changes.
**Fix**: 
- Commit working states
- "Before making changes, what currently works that we shouldn't break?"

## Recovery Commands

When stuck:
```
"Stop all changes. Summarize current state of [feature]."

"What's the minimal change needed to fix [bug]?"

"Show me what you think the code currently does, step by step."

"Forget the approach we tried. What would you do differently?"
```
