# Claude Code Example Prompts

## Debugging Examples

### Bug Fix with Verification
```
users report login fails after session timeout.
check the auth flow in src/auth/, especially token refresh.
write a failing test that reproduces the issue, then fix it.
```

### Error Investigation
```
there's an error: [paste full error message here]

1. find the root cause, don't just suppress it
2. explain why this is happening
3. fix it and verify the fix works
4. add a test to prevent regression
```

### Performance Investigation
```
the /api/search endpoint is slow (taking 5+ seconds)
profile it, identify bottlenecks, and suggest optimizations
show me the tradeoffs for each option
```

## Feature Development Examples

### New Feature with Context
```
implement user avatar upload

1. look at how we handle file uploads elsewhere in the codebase
2. check existing patterns in src/features/
3. create a plan before writing code
4. implement with proper validation and error handling
5. write tests alongside
```

### Refactoring
```
refactor src/services/payment.js from callbacks to async/await

1. show me the current implementation first
2. ensure backward compatibility
3. migrate incrementally with tests at each step
4. run all tests after completion
```

### API Endpoint
```
add a new endpoint POST /api/users/:id/preferences

- follow the patterns in existing endpoints
- add input validation
- include proper error responses
- write integration tests
- update API documentation
```

## Code Review Examples

### Self Review
```
review the changes I've made in this branch

focus on:
- edge cases I might have missed
- security issues
- consistency with existing patterns
- performance implications

be specific with file names and line numbers
```

### Security Review
```
use a subagent to review src/auth/ for security issues

look for:
- injection vulnerabilities
- authentication/authorization flaws
- secrets or credentials in code
- insecure data handling

provide specific line references and fixes
```

## Git & PR Examples

### Complete PR Workflow
```
1. create branch feature/TICKET-123-add-auth
2. implement the authentication middleware
3. write tests
4. commit with message "[TICKET-123] Add authentication middleware"
5. push and create a draft PR with detailed description
```

### Commit Message
```
commit my changes with a descriptive message
group related changes if appropriate
```

### PR Description
```
write a PR description for these changes that includes:
- what changed and why
- how to test
- any migration steps needed
- screenshots if UI changed
```

## Documentation Examples

### Code Documentation
```
add comprehensive JSDoc comments to all public functions in src/utils/
follow the existing documentation style in the codebase
include parameter descriptions and examples
```

### README Update
```
update README.md with:
- installation instructions for the new Redis dependency
- configuration options
- usage example
- troubleshooting section
```

## Testing Examples

### Unit Tests
```
write unit tests for src/utils/validation.js

- cover happy path
- test edge cases: null, undefined, empty string, very long strings
- follow existing test patterns
- avoid mocks unless necessary
```

### Integration Tests
```
write integration tests for the user registration flow

test:
- successful registration
- duplicate email error
- invalid email format
- missing required fields
```

## Exploration Examples

### Codebase Understanding
```
explain how logging works in this project
trace the flow from log call to output destination
```

### Pattern Discovery
```
how do existing API endpoints in this codebase handle:
- authentication
- validation
- error responses
- pagination

show me examples from the code
```

### Architecture Analysis
```
analyze the authentication system and suggest improvements
consider security, maintainability, and performance
```

## Interview Pattern Example
```
I want to build a notification system that supports email, SMS, and push notifications.

Interview me in detail about:
- technical requirements
- delivery guarantees
- retry logic
- user preferences
- rate limiting

don't ask obvious questions, dig into the edge cases and tradeoffs.
keep interviewing until we've covered everything.
then write a complete spec to docs/notification-system-spec.md
```

## Handoff Example
```
put our progress in HANDOFF.md

include:
- the original goal
- what you tried
- what worked and what didn't
- current state of the code
- clear next steps for the next agent

so someone with fresh context can pick up where we left off
```

## Headless/Automation Examples

### Lint Check
```bash
claude -p 'check for issues compared to main branch. report filename:line and description' --output-format text
```

### Code Analysis
```bash
claude -p 'list all TODO comments in the codebase with file locations' --output-format json
```

### Migration Script
```bash
cat files-to-migrate.txt | xargs -I {} claude -p "migrate {} from API v1 to v2 format"
```

### Budget-Limited Analysis
```bash
claude -p "comprehensive security audit of src/auth/" --max-budget-usd 5.00
```
