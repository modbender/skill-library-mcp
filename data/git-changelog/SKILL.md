---
name: git-changelog
description: Auto-generate beautiful changelogs from git history, grouped by conventional commit types
version: 1.0.0
author: Sovereign Skills
tags: [openclaw, agent-skills, automation, productivity, free, git, changelog, devops]
triggers:
  - generate changelog
  - create changelog
  - git changelog
  - release notes
---

# git-changelog — Auto-Generate Changelogs

Generate polished, categorized changelogs from git commit history. Outputs markdown ready for CHANGELOG.md or GitHub releases.

## Steps

### 1. Verify Git Repository

```bash
git rev-parse --is-inside-work-tree
```

If this fails, stop — not a git repository.

### 2. Determine Range

The user may specify:
- **Tag-to-tag**: `v1.0.0..v1.1.0`
- **Since date**: `--since="2025-01-01"`
- **Last N commits**: `-n 50`
- **Since last tag**: auto-detect with `git describe --tags --abbrev=0`

Default behavior — find the last tag and generate from there to HEAD:

```bash
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null)
```

If no tags exist, use the full history.

### 3. Extract Commits

```bash
# Tag-to-HEAD
git log ${LAST_TAG}..HEAD --pretty=format:"%H|%s|%an|%ad" --date=short

# Date range
git log --since="2025-01-01" --until="2025-02-01" --pretty=format:"%H|%s|%an|%ad" --date=short

# Full history
git log --pretty=format:"%H|%s|%an|%ad" --date=short
```

### 4. Categorize by Conventional Commits

Parse each commit subject and group into categories:

| Prefix | Category | Emoji |
|--------|----------|-------|
| `feat` | ✨ Features | New functionality |
| `fix` | 🐛 Bug Fixes | Corrections |
| `docs` | 📚 Documentation | Docs changes |
| `style` | 💄 Styling | Formatting, no logic change |
| `refactor` | ♻️ Refactoring | Code restructuring |
| `perf` | ⚡ Performance | Speed improvements |
| `test` | ✅ Tests | Adding/fixing tests |
| `build` | 📦 Build | Build system, deps |
| `ci` | 👷 CI/CD | Pipeline changes |
| `chore` | 🔧 Chores | Maintenance |
| *(other)* | 📝 Other | Uncategorized |

Parse pattern: `type(scope): description` or `type: description`

### 5. Generate Markdown

Output format:

```markdown
# Changelog

## [v1.2.0] — 2025-02-15

### ✨ Features
- **auth**: Add OAuth2 support ([abc1234])
- **api**: New rate limiting middleware ([def5678])

### 🐛 Bug Fixes
- **db**: Fix connection pool leak ([ghi9012])

### 📚 Documentation
- Update API reference ([jkl3456])
```

Rules:
- Include scope in bold if present: `**scope**: message`
- Include short hash as reference: `([abc1234])`
- Sort categories: Features → Fixes → everything else
- Omit empty categories
- If commits include `BREAKING CHANGE` in body/footer, add a `### 💥 Breaking Changes` section at the top

### 6. Detect Breaking Changes

```bash
git log ${LAST_TAG}..HEAD --pretty=format:"%H|%B" | grep -i "BREAKING CHANGE"
```

Also flag commits with `!` after type: `feat!: remove legacy API`

### 7. Output

- Default: print to chat for review
- If user requests file output: write/append to `CHANGELOG.md` at project root
- When prepending to existing CHANGELOG.md, insert after the `# Changelog` header, before previous entries

## Edge Cases

- **No conventional commits**: Fall back to listing all commits as "Other"
- **Merge commits**: Skip merge commits (`Merge branch...`, `Merge pull request...`) unless user requests them
- **Monorepo**: If user specifies a path, use `git log -- path/to/package`
- **No tags**: Use full history or ask user for a date range
- **Empty range**: Report "No commits found in the specified range"

## Error Handling

| Error | Resolution |
|-------|-----------|
| Not a git repo | Tell user to navigate to a git repository |
| No commits found | Confirm the range/date filter; suggest broader range |
| Binary/garbled output | Ensure `--pretty=format` is used correctly |
| Permission denied | Check file permissions on CHANGELOG.md |

---
*Built by Clawb (SOVEREIGN) — more skills at [coming soon]*
