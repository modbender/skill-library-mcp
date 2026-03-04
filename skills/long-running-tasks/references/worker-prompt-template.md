# Worker Prompt Template

Copy and adapt this for each task prompt. The orchestrator inserts the specific task; this template ensures workers follow the right protocol.

## Template

```
You are working on [PROJECT_NAME]. Read [CONTEXT_FILE] and TODO.md for full context.

YOUR TASK:
[Paste the specific task description from TODO.md]

STEPS:
1. Read [CONTEXT_FILE] for project context and commands
2. Read TODO.md for the full task list and current status
3. Implement the task described above
4. Run tests: [TEST_COMMAND]
5. Fix any test failures before proceeding
6. Update TODO.md — check off the completed task: change "- [ ]" to "- [x]"
7. Commit and push using the project's commit convention
8. Run: openclaw system event --text "Done: [BRIEF_SUMMARY]" --mode now

RULES:
- Do NOT skip tests. If tests fail, fix them before committing.
- Do NOT exit without committing. If blocked, commit what you have with a note explaining what's blocking.
- Do NOT modify code outside the task scope.
- If a task is too large, implement what you can, update TODO.md to reflect remaining work, and commit.
```

## Scoping Tips

- **One task per worker.** Multi-task prompts lead to partial completion and silent exits.
- **Name specific files.** "Add retry logic to src/api/client.py" beats "add retry logic".
- **State acceptance criteria.** "All tests pass" or "endpoint returns 200 with valid payload".
- **Set boundaries.** "Only modify files in src/eval/" prevents scope creep.
- **Include the 'blocked' escape hatch.** Workers should always commit *something* — even a partial result with a BLOCKED note is better than a silent exit.
