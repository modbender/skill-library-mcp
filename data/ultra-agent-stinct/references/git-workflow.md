# Git Workflow Reference

## Branching

Create a feature branch before risky changes:
```bash
git checkout -b fix/description
```

Switch back:
```bash
git checkout main
```

## Stashing

Save work temporarily:
```bash
git stash
git stash pop
```

## Viewing History

```bash
git log --oneline -20
git log --oneline --graph -10
git diff HEAD~1
git show <commit-hash>
```

## PR Review

Check PR diff:
```bash
git diff main...HEAD
```

Read specific file at a commit:
```bash
git show <commit>:<file>
```

## Undoing (ASK THE USER FIRST)

Unstage a file:
```bash
git reset HEAD <file>
```

Discard changes to a file (DESTRUCTIVE — confirm first):
```bash
git restore <file>
```

Legacy alternative: `git checkout -- <file>`

## Merge Conflicts

1. Read the conflicted file — look for `<<<<<<<`, `=======`, `>>>>>>>`
2. Edit to resolve: keep the correct version
3. `git add <file>` then `git commit`

## Commit Message Style

Follow the project's existing style. If none:
```
type: short description

Optional longer explanation
```
Types: `fix`, `feat`, `refactor`, `docs`, `test`, `chore`
