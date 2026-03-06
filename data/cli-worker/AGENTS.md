# CLI Worker Skill - Agent Quick Reference

## What this skill does

Delegates coding tasks to Kimi CLI agents in isolated git worktrees.

## Quick commands

```bash
# Run a task (creates worktree if in a git repo)
cli-worker execute "Your task prompt"

# With constraints and success criteria
cli-worker execute "Create hello.py" --constraint "Python 3.11" --success "Tests pass"

# Get full plain-text output (not just final answer)
cli-worker execute "Your task" --output-format text

# Check task status
cli-worker status <taskId>

# Worktree management
cli-worker worktree list
cli-worker worktree remove <taskId>
cli-worker cleanup --older-than 24
```

## Merge or cleanup after task

- **Keep the work:** From main repo: `git merge openclaw/<taskId>` then `cli-worker worktree remove <taskId>`
- **Discard:** `cli-worker worktree remove <taskId>`

## Important notes

- **Auth is a human-only step:** Users must install Kimi CLI and run `/login` themselves. This skill does not store or use credentials.
- **Prefer CLI over sessions_spawn:** For single coding tasks, use `cli-worker execute` directly rather than spawning a sub-agent session.
- Use `--output-format text` when you need to consume the full output as readable text.

See SKILL.md for full details.
