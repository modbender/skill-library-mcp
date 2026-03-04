---
name: github-release-workflow
description: "Professional GitHub release workflow. Use when: (1) releasing a new version, (2) managing versions and tags, (3) following conventional commits, (4) updating README and docs, (5) setting up CI/CD for releases."
metadata:
  {
    openclaw: { emoji: "🚀" },
  }
---

# GitHub Release Workflow Skill

A standardized workflow for professional GitHub releases.

**IMPORTANT: Always update README.md and documentation before releasing!**

## Prerequisites

- Git installed
- GitHub CLI (`gh`) authenticated
- Git repository initialized

## Quick Commands

### Full Release Flow

```bash
# 1. Ensure clean working tree
git status

# 2. Run tests and format
pip install -e ".[dev]"
pytest
black lib/ tests/

# 3. Update version in pyproject.toml
# Edit: version = "2.1.0"

# 4. Update CHANGELOG.md
# Add new section with today's date

# 5. Update README.md (IMPORTANT!)
# - Update version badge
# - Update features list
# - Update project structure if changed
# - Update roadmap table

# 6. Update other docs as needed
# - docs/*.md
# - API documentation
# - Examples

# 7. Stage and commit
git add .
git commit -m "release: v2.1.0 - Description"

# 8. Create tag
git tag -a v2.1.0 -m "Version 2.1.0"

# 9. Push
git push
git push origin v2.1.0
```

### README Update Checklist

When releasing a new version, always update README.md:

| Item | Description |
|------|-------------|
| Version badge | Update `version-x.x.x-blue` |
| Features list | Add new features, remove deprecated |
| Project structure | Reflect new files/directories |
| Installation | Update if deps changed |
| Usage | Add new examples if needed |
| Roadmap | Move current version to done, add next |
| API docs | Update if API changed |

### Conventional Commits Format

```
<type>(<scope>): <description>

Types: feat, fix, docs, style, refactor, test, chore, release
```

Examples:
- `feat(memory): add SQLite support`
- `fix(vitality): correct energy calculation`
- `docs: update README`

### Version Format

```
MAJOR.MINOR.PATCH
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes
```

## Branch Strategy

```
main (stable)
  ↑
develop (integration)
  ↑
feature/* (new features)
```

## GitHub Release (Optional)

```bash
gh release create v2.1.0 \
  --title "Version 2.1.0" \
  --notes "Release notes"
```

## See Also

- Full specification: `github-release-workflow/SPEC.md`
- Keep a Changelog: https://keepachangelog.com/
- Semantic Versioning: https://semver.org/
- Conventional Commits: https://www.conventionalcommits.org/
