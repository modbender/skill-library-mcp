# Claude Code Workflows

## Codebase Understanding

### Quick Overview
```
what does this project do?
```

### Deep Dive
```
1. explain the folder structure
2. what technologies does this project use?
3. where is the main entry point?
4. how does logging work?
5. trace the flow from [entry point] to [outcome]
```

### Pattern Discovery
```
how do existing API endpoints handle authentication?
what patterns does this codebase use for error handling?
show me examples of how validation is implemented
```

## Debugging

### Error Investigation
```
there's an error: [paste error]

1. Find the root cause, don't just suppress it
2. Write a failing test that reproduces the issue
3. Fix it and verify the test passes
```

### Performance Issues
```
this endpoint is slow. Profile it, identify bottlenecks, 
and suggest optimizations with tradeoffs explained.
```

### Regression Hunting
```
/compact started throwing 400 errors. Use git bisect to find 
which commit broke it. Write a test script that verifies the 
behavior at each commit.
```

## Feature Development

### New Feature
```
implement [feature description]

1. First explore how similar features work in the codebase
2. Create a detailed plan before writing code
3. Follow existing patterns and conventions
4. Write tests alongside implementation
5. Verify everything works end-to-end
```

### Refactoring
```
refactor the authentication module to use async/await

1. Show me the current implementation
2. Create a plan that maintains backward compatibility
3. Migrate incrementally with tests at each step
4. Ensure all existing tests still pass
```

### Migration
```
migrate all API endpoints from v1 to v2 format

1. List all affected files
2. Show me one example migration
3. After I approve, migrate the rest following the same pattern
4. Run the test suite after each batch
```

## Testing Workflows

### Writing Tests
```
write unit tests for the calculator functions

- Cover happy path and edge cases
- Follow existing test patterns in the codebase
- Avoid mocks unless necessary
- Run tests after writing
```

### Test-First Development
```
write tests for [feature] first. Don't implement yet.
I want to review the test cases before implementation.
```

### Coverage Improvement
```
identify untested code paths in src/auth/
write tests for the missing coverage
focus on error handling and edge cases
```

## Git Workflows

### Feature Branch
```
1. create branch feature/TICKET-123-add-auth
2. implement the changes
3. commit with message "[TICKET-123] Add authentication middleware"
4. push and create draft PR
```

### PR Creation
```
/commit-push-pr
```

Or step-by-step:
```
1. what files have I changed?
2. commit with a descriptive message summarizing all changes
3. push to origin
4. create a PR with detailed description
```

### Merge Conflict Resolution
```
help me resolve merge conflicts
show me what's conflicting and explain the differences
```

### Git History Analysis
```
look through ExecutionFactory's git history
summarize how its API evolved and why
```

## Code Review

### Self-Review
```
review the changes in this branch

- Look for edge cases I might have missed
- Check for security issues
- Verify consistency with existing patterns
- Be specific about line numbers
```

### External PR Review
```
review PR #123

- Focus on correctness and maintainability
- Identify potential bugs or edge cases
- Suggest improvements
- Note anything that looks good
```

## Documentation

### Code Documentation
```
add JSDoc comments to all public functions in src/utils/
follow the existing documentation style in the codebase
```

### README Updates
```
update README with installation instructions for the new dependency
include a usage example
```

### Architecture Documentation
```
document the authentication flow in docs/auth.md
include sequence diagrams if helpful
```

## Plan Mode Workflows

### Safe Exploration
```bash
claude --permission-mode plan
> analyze the authentication system and suggest improvements
```

### Architecture Review
```bash
claude --permission-mode plan -p "identify technical debt in src/"
```

### Change Impact Analysis
```bash
claude --permission-mode plan
> if I change the User model schema, what else would break?
```

## Agent Handoff Pattern

When a task needs multiple specialists, use HANDOFF.md to pass context between agents:

### Example: Frontend → Backend → DevOps

**Step 1: Frontend builds the UI**
```bash
claude --agent frontend-dev -p "Build a user dashboard component. When done, write what backend APIs you need to HANDOFF.md"
```

**Step 2: Backend reads handoff, builds APIs**
```bash
claude --agent backend-dev -p "Read HANDOFF.md. Build the APIs that frontend requested. Add deployment notes to HANDOFF.md"
```

**Step 3: DevOps reads handoff, deploys**
```bash
claude --agent devops -p "Read HANDOFF.md. Set up CI/CD pipeline and deploy the new endpoints"
```

### HANDOFF.md Template
```markdown
# Handoff: [Feature Name]

## Completed By: [agent-name]
- What was built
- Key decisions made
- Files created/modified

## Needs From Next Agent:
- Specific requirements
- Constraints to respect
- Questions to resolve

## Context:
- Relevant background
- Links to specs/docs
```

This pattern keeps each agent focused while maintaining continuity across the task.

---

## Session Management

### Long Session Handoff
```
put progress in HANDOFF.md:
- what was the goal
- what you tried
- what worked, what didn't
- next steps

so the next agent can continue
```

### Resume Previous Work
```bash
# Continue most recent
claude -c

# Pick from recent sessions
claude -r

# Resume specific session
claude -r "auth-refactor"

# Resume from PR
claude --from-pr 123
```

### Parallel Sessions

Using terminal tabs:
1. Open new tab for each task
2. Sweep left to right (oldest to newest)
3. Keep to 3-4 active tasks max

Using Git worktrees:
```
create a git worktree in ../feature-branch for feature/new-auth
cd there and start working on authentication
```

## Headless/Automation Workflows

### CI Integration
```bash
# Lint with Claude
claude -p 'check for issues vs main branch' --output-format json

# PR review
claude -p 'review changes in this PR' --output-format text

# Migration
cat files.txt | xargs -P 4 -I {} claude -p "migrate {} to new API"
```

### Structured Output
```bash
claude -p "list all API endpoints" --output-format json \
  --json-schema '{"type":"array","items":{"type":"object","properties":{"path":{"type":"string"},"method":{"type":"string"}}}}'
```

### Budget-Limited Tasks
```bash
claude -p "complex analysis task" --max-budget-usd 5.00
```

## Browser Integration Workflows

### Visual Testing
```
/chrome

take a screenshot of localhost:3000/dashboard
compare it to the design mockup I provided
list any differences
```

### E2E Verification
```
with Chrome, test the login flow:
1. go to /login
2. enter test credentials
3. verify redirect to dashboard
4. check that user menu shows correct name
```

### Debugging Live Apps
```
/chrome

open the app in my browser
inspect the network tab for the failing API call
show me the request/response
```

## Interview Pattern

For complex features:
```
I want to build [brief description]. Interview me in detail.

Ask about:
- technical implementation
- UI/UX considerations
- edge cases
- concerns and tradeoffs

Don't ask obvious questions, dig into the hard parts.
Keep interviewing until we've covered everything.
Then write a complete spec to SPEC.md.
```

Start fresh session to implement the spec.
