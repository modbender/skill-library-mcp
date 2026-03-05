# Agent Pipeline Skill

Standard development workflow for code tasks using spawned sub-agents.

## Pipeline Order
```
[Researcher] → Coder → Reviewer → Security → Tester → Commit
```

### Researcher (optional)
- Use when: new APIs, unfamiliar tech, "figure out how" tasks
- Gathers context, reads existing code patterns, documents findings

### Coder
- Writes the code changes
- Does NOT commit or push
- Creates branch if needed
- Runs build to verify compilation

### Reviewer
- Runs `git diff` to review all changes
- Checks: code quality, patterns, minimal scope, consistency
- Reports PASS or FAIL

### Security
- Audits for: injection, XSS, auth issues, data exposure, CSRF
- Reports PASS or FAIL

### Tester
- Verifies build compiles (0 errors)
- Structural checks (files exist, actions registered, links correct)
- Reports PASS or FAIL

### Commit
- Done by DevJarvis (main agent), not a sub-agent
- Commit with descriptive message
- Push to feature branch
- Update Planner task with dev notes

## Rules
- **ALWAYS log to the board** before, during, and after
- Create board item under the relevant project category
- Each agent gets clear, specific instructions
- Agents use `agentId` matching their role (coder, reviewer, security, tester, researcher)
- If an agent fails, fix the issue and re-run that stage
- Auth: all agents need `auth-profiles.json` copied from main agent

## Board API
- Create item: POST `http://10.0.0.40:3000/api/board/projects/{project}/items`
- Body: `{"title": "...", "status": "in-progress", "detail": "..."}`

## Planner Updates
- Update task description with branch name, changes summary, pipeline results
- Add comments for back-and-forth with Rich

## Branch Naming
- `feature/{short-description}`
- Always branch from master
- Rich handles merges to master
