---
name: git-hooks
description: Auto-generate and manage Git hooks for pre-commit, pre-push,
  commit-msg, and more.
---


# Git Hooks

Set up and manage Git hooks for any repository.

**Use when** adding automated checks to git workflows — linting, testing, commit message validation.

## Requirements

- Git repository (`.git/` directory must exist)
- No API keys needed

## Instructions

1. **Verify repo root**: `test -d .git && echo "OK" || echo "Not a git repo"`. Never create hooks outside a git repo.

2. **Back up existing hooks** before overwriting:
   ```bash
   [ -f .git/hooks/pre-commit ] && cp .git/hooks/pre-commit .git/hooks/pre-commit.bak
   ```

3. **Create the hook** and make it executable:
   ```bash
   cat > .git/hooks/<hook-name> << 'EOF'
   #!/bin/sh
   # hook content here
   EOF
   chmod +x .git/hooks/<hook-name>
   ```

## Common Hooks

### Pre-commit: Lint Staged Files
```bash
#!/bin/sh
STAGED=$(git diff --cached --name-only --diff-filter=ACM)
# JavaScript/TypeScript
echo "$STAGED" | grep -E '\.(js|ts|jsx|tsx)$' | xargs -r npx eslint --quiet 2>/dev/null
[ $? -ne 0 ] && echo "❌ ESLint failed" && exit 1
# Python
echo "$STAGED" | grep -E '\.py$' | xargs -r python3 -m py_compile 2>&1
[ $? -ne 0 ] && echo "❌ Python syntax check failed" && exit 1
exit 0
```

### Pre-push: Run Tests
```bash
#!/bin/sh
[ -f package.json ] && npm test
[ -f pytest.ini ] || [ -d tests/ ] && python3 -m pytest -q
exit $?
```

### Commit-msg: Enforce Conventional Commits
```bash
#!/bin/sh
MSG=$(cat "$1")
if ! echo "$MSG" | grep -qE '^(feat|fix|docs|style|refactor|test|chore|ci|perf|build)(\(.+\))?: .+'; then
  echo "❌ Commit message must follow Conventional Commits format"
  echo "   Example: feat(auth): add login page"
  exit 1
fi
```

### Pre-commit: Prevent Secret Leaks
```bash
#!/bin/sh
STAGED=$(git diff --cached --diff-filter=ACM -p)
if echo "$STAGED" | grep -qEi '(api[_-]?key|secret|password|token)\s*[=:]\s*["\x27][^\s]+'; then
  echo "❌ Potential secret detected in staged changes!"
  echo "   Review your changes and use environment variables instead."
  exit 1
fi
```

## Management Commands

```bash
# List active hooks (non-sample)
ls .git/hooks/ | grep -v '\.sample$'

# Disable a hook temporarily
chmod -x .git/hooks/pre-commit

# Re-enable
chmod +x .git/hooks/pre-commit

# Remove a hook
rm .git/hooks/pre-commit
```

## Edge Cases & Troubleshooting

- **Hook not running**: Check `chmod +x` and shebang line (`#!/bin/sh` or `#!/bin/bash`).
- **Bypass when needed**: `git commit --no-verify` skips pre-commit and commit-msg hooks.
- **Team sharing**: Hooks in `.git/hooks/` aren't committed. Use a `hooks/` directory in repo root + `git config core.hooksPath hooks/` for team-wide hooks.
- **Windows compatibility**: Use `#!/bin/sh` (not bash) for cross-platform support. Avoid bash-specific syntax.
- **Slow hooks**: Keep pre-commit hooks under 5 seconds. Only lint staged files, not the whole project.

## Security Considerations

- Add a secret-detection hook (see above) to prevent accidental credential commits.
- Never store API keys or passwords in hook scripts themselves.
