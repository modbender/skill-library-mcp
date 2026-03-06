# Claude Code Best Practices

## The Fundamental Constraint: Context Window

**Everything else flows from this:** Claude's 200k token context window fills fast, and performance degrades as it fills. Managing context is the single most important meta-skill.

## Core Principles

### 1. Give Claude a Way to Verify Its Work

**This is the highest-leverage strategy.** Without verification, Claude produces plausible-looking code that may not work. You become the only feedback loop.

| Strategy | Before | After |
|----------|--------|-------|
| Verification criteria | "implement email validation" | "write validateEmail function. Test: test@example.com=true, invalid=false. Run tests after." |
| Visual verification | "make dashboard look better" | "[paste screenshot] implement this design. Screenshot result and compare. List differences." |
| Root cause focus | "the build is failing" | "build fails with [error]. Fix and verify build succeeds. Address root cause, don't suppress." |

**Verification options:**
- Tests (unit, integration)
- Linters and type checkers
- Screenshots (with Chrome integration)
- Bash commands that check output
- Manual inspection checkpoints

### 2. Explore First, Then Plan, Then Code

**The 4-phase workflow:**

1. **Explore:** Use Plan Mode (`Shift+Tab` or `--permission-mode plan`) to understand the codebase
2. **Plan:** Create detailed implementation plan with Claude, explicitly saying "don't write code yet"
3. **Execute:** Implement with verification checkpoints
4. **Verify:** Run tests, check outputs, iterate

This prevents wasted effort on poor architectural choices.

### 3. Provide Specific Context in Prompts

Claude can infer intent but can't read your mind.

| Strategy | Before | After |
|----------|--------|-------|
| Scope the task | "add tests for foo.py" | "write test for foo.py covering edge case where user is logged out. Avoid mocks." |
| Point to sources | "why does ExecutionFactory have weird api?" | "look through ExecutionFactory's git history and summarize how its api came to be" |
| Reference patterns | "add calendar widget" | "look at existing widgets (HotDogWidget.php is good example). Follow pattern for calendar widget." |
| Describe symptoms | "fix login bug" | "users report login fails after session timeout. Check auth flow in src/auth/, especially token refresh." |

**Rich context methods:**
- Use `@` to reference files directly
- Paste images (drag and drop)
- Give URLs for documentation
- Pipe data: `cat error.log | claude`
- Let Claude fetch what it needs

### 4. Manage Context Aggressively

| Trigger | Action |
|---------|--------|
| Between unrelated tasks | `/clear` |
| Long session | `/compact [focus area]` |
| Exploration without cluttering main context | Use subagents |
| Multiple failed corrections | `/clear` and write better initial prompt |
| Context filling | Create HANDOFF.md, start fresh session |

**HANDOFF.md pattern:**
```
Put progress in HANDOFF.md. Explain what you tried, what worked, 
what didn't work, so next agent with fresh context can continue.
```

Then start new session with just: `> HANDOFF.md`

### 5. Use Git for Safety

- Start every task on a new branch
- Use draft PRs for safe PR creation
- Allow pull automatically, but not push (riskier)
- Use Git worktrees for parallel branch work

```
"create branch feature/auth-fix, implement changes, write tests, 
commit with descriptive message, create draft PR"
```

## CLAUDE.md Best Practices

CLAUDE.md is loaded every session. Keep it **concise and actionable**.

### Include:
- Bash commands Claude can't guess
- Code style rules that differ from defaults
- Testing instructions and preferred test runner
- Repo conventions (branch naming, PR format)
- Architectural decisions specific to your project
- Environment quirks (required env vars)
- Common gotchas

### Exclude:
- Things Claude can figure out by reading code
- Standard language conventions
- Detailed API docs (link instead)
- Information that changes frequently
- Long explanations or tutorials
- Self-evident practices

**Example:**
```markdown
# Code style
- Use ES modules (import/export), not CommonJS
- Destructure imports when possible

# Workflow
- Typecheck when done making changes
- Prefer running single tests for performance

# Git
- Branch format: feature/TICKET-description
- Commit messages: [TICKET] Short description
```

### Debugging CLAUDE.md Issues

- If Claude ignores rules: File is probably too long
- If Claude asks questions answered in file: Phrasing may be ambiguous
- Add emphasis ("IMPORTANT", "YOU MUST") for critical rules
- Test changes by observing if Claude's behavior actually shifts

## Common Failure Patterns

### The Kitchen Sink Session
**Symptom:** Start with one task, ask unrelated things, go back to first task. Context full of irrelevant info.
**Fix:** `/clear` between unrelated tasks.

### Correcting Over and Over
**Symptom:** Claude does something wrong, you correct, still wrong, correct again.
**Fix:** After two failed corrections, `/clear` and write better initial prompt.

### Over-Specified CLAUDE.md
**Symptom:** CLAUDE.md too long, Claude ignores half of it.
**Fix:** Ruthlessly prune. If Claude already does it correctly, delete the instruction.

### Trust-Then-Verify Gap
**Symptom:** Claude produces plausible implementation missing edge cases.
**Fix:** Always provide verification. If you can't verify it, don't ship it.

### Infinite Exploration
**Symptom:** Ask Claude to "investigate" without scope. Claude reads hundreds of files.
**Fix:** Scope investigations narrowly or use subagents.

## Performance Optimization

### Reduce Token Usage

1. **Clear frequently:** `/clear` between unrelated tasks
2. **Compact proactively:** Don't wait for auto-compact
3. **Use subagents:** Exploration in separate context
4. **Lazy-load MCP tools:** Set `ENABLE_TOOL_SEARCH=true`
5. **Slim skills:** Only include what's needed
6. **Trim CLAUDE.md:** Remove anything redundant

### Session Naming

```
/rename oauth-migration
/rename debugging-memory-leak
```

Find sessions later with `claude -r`.

## Advanced Patterns

### Writer/Reviewer Pattern

| Session A (Writer) | Session B (Reviewer) |
|--------------------|----------------------|
| Implement rate limiter for API endpoints | Review rate limiter in @src/middleware/rateLimiter.ts. Look for edge cases, race conditions. |
| Here's feedback: [Session B output]. Address these issues. | |

### Test-First Pattern

Have one Claude write tests, then another write code to pass them.

### Fan-Out Pattern

For large migrations:
1. Generate file list with Claude
2. Distribute across parallel `claude -p` invocations
3. Aggregate results

```bash
# Example: migrate all TypeScript files
for file in $(cat files-to-migrate.txt); do
  claude -p "migrate $file to new API" &
done
wait
```
