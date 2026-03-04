# Parallel Workflow — Agentic Engineering

## Terminal Grid Setup

Use a 3x3 or 2x3 terminal grid. All visible without switching windows.

```
Recommended: 3840x1620+ monitor (ultrawide)
Tool: Ghostty, iTerm2, or tmux
```

## How Many Agents?

| Work Type | Agents | Why |
|-----------|--------|-----|
| Focused feature | 1-2 | Large blast radius, needs steering |
| Refactoring | 3-4 | Independent areas, low risk |
| UI polish | 4-6 | Small isolated changes |
| Tests/docs | 4-6 | Parallel, independent |

## Same Folder, Different Areas

Most agents work in the same repo, same folder. No worktrees needed.

Pick non-overlapping areas:
```
Agent 1: src/api/
Agent 2: src/components/
Agent 3: tests/
Agent 4: docs/
```

If changes must touch the same file → serialize, don't parallelize.

## Atomic Commits Per Agent

Each agent commits only its own changes. Configure in AGENTS.md:

```markdown
## Git Workflow
- Commit after completing each logical change
- Only commit files YOU edited
- Use descriptive commit messages
- Don't commit other agents' work
```

Result: Clean git history even with 4+ agents running.

## Switching Context

When one agent is thinking/working:
1. Check another agent's progress
2. Start new task in empty terminal
3. Review recent commits
4. Prep next prompt

Never wait idle. Context switching is your job.

## When to Serialize

Don't parallelize when:
- Changes touch the same files
- Work has hard dependencies
- You need to see result A before starting B
- Database migrations (one at a time)

## Recovery from Conflicts

If agents step on each other:
```bash
git stash           # Save current state
git log --oneline   # Find last good commit
git reset --hard    # Reset to good state
git stash pop       # Reapply if needed
```

Small, atomic commits make recovery easy.
