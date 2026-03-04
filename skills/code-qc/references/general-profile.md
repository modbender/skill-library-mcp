# General QC Profile (Language-Agnostic)

Use this for cross-cutting checks that apply to any language, or when the project isn't Python, TypeScript, or GDScript.

## Git State

```bash
# Current commit (for baseline)
git log --oneline -1

# Working directory state
git status --short          # Should be empty (clean) or document changes

# Conflict markers (should never exist)
git diff --check            # Returns non-zero if conflict markers found

# Uncommitted changes summary
git diff --stat
```

## File Structure Verification

Verify expected project files exist:

### Required Files (WARN if missing)
- README.md or README
- License file (LICENSE, LICENSE.md, LICENSE.txt)

### Standard Files (INFO if missing)
- Test directory (`tests/`, `test/`, `__tests__/`)
- CI config (`.github/workflows/`, `.gitlab-ci.yml`, `.circleci/`)
- CHANGELOG (CHANGELOG.md, HISTORY.md, NEWS.md)
- CONTRIBUTING guide

### Configuration Files
- `.gitignore` — should exist
- `.editorconfig` — nice to have for consistency

## Documentation Freshness

Check if docs match actual state:

### Version Number Consistency
```bash
# Find version declarations
grep -rn "version" pyproject.toml package.json Cargo.toml 2>/dev/null
grep -rn "Version:" README.md 2>/dev/null

# These should match
```

### Stale Markers
```bash
# Find TODO/FIXME that might be stale
grep -rn "TODO\|FIXME\|XXX\|HACK" --include="*.md" .

# Find "Coming soon" or "WIP" claims
grep -rni "coming soon\|work in progress\|wip\|not yet implemented" --include="*.md" .
```

### Status Badges
If README has badges, verify they're current:
- Build status badge links to actual CI
- Coverage badge URL is correct
- Version badge matches package version

## Dependency Security

Run language-appropriate security audit:

| Language | Tool | Command |
|----------|------|---------|
| Python | pip-audit | `pip-audit --json` |
| Python | safety | `safety check --json` |
| Node | npm | `npm audit --json` |
| Node | pnpm | `pnpm audit --json` |
| Rust | cargo-audit | `cargo audit --json` |
| Go | govulncheck | `govulncheck -json ./...` |
| Ruby | bundler-audit | `bundle audit check --format json` |

### Interpreting Results
- **Critical/High** → Must fix before release
- **Moderate** → Should fix, but not blocking
- **Low** → Document and track

## Code Size Analysis

### Line Count Summary
```bash
# Top 20 largest files
find . -name "*.py" -o -name "*.ts" -o -name "*.rs" -o -name "*.go" -o -name "*.gd" | \
  xargs wc -l 2>/dev/null | sort -n | tail -20
```

### Large File Detection
Files over 500 lines may need splitting:
```bash
find . \( -name "*.py" -o -name "*.ts" -o -name "*.gd" \) \
  -exec sh -c 'lines=$(wc -l < "$1"); [ "$lines" -gt 500 ] && echo "$lines $1"' _ {} \;
```

### Complexity Indicators
- Single file > 500 lines: Consider splitting
- Single function > 50 lines: Consider refactoring
- Deep nesting (>4 levels): Consider extraction

## CI/CD Check

### CI Config Exists
```bash
ls -la .github/workflows/*.yml .gitlab-ci.yml .circleci/config.yml Jenkinsfile 2>/dev/null
```

### CI Should Include
- [ ] Tests run on every PR
- [ ] Linting runs on every PR
- [ ] Build step exists
- [ ] Security scanning (optional but recommended)
- [ ] Coverage reporting (optional)

### CI Health
If CI badges exist, verify:
- Recent runs are passing
- Runs complete in reasonable time (<10 min for most projects)

## Changed Files Only Mode

For CI on pull requests, only check changed files:

```bash
# Get changed files vs main branch
git diff --name-only origin/main...HEAD

# Get changed files (staged)
git diff --name-only --cached

# Get changed files (unstaged)
git diff --name-only
```

### Filter by Extension
```bash
# Python files only
git diff --name-only origin/main...HEAD -- '*.py'

# TypeScript files only
git diff --name-only origin/main...HEAD -- '*.ts' '*.tsx'

# GDScript files only
git diff --name-only origin/main...HEAD -- '*.gd'
```

## Environment Detection

### Container/VM
```bash
# Docker
[ -f /.dockerenv ] && echo "Running in Docker"

# Kubernetes
[ -n "$KUBERNETES_SERVICE_HOST" ] && echo "Running in Kubernetes"

# CI environments
[ -n "$CI" ] && echo "Running in CI"
[ -n "$GITHUB_ACTIONS" ] && echo "Running in GitHub Actions"
[ -n "$GITLAB_CI" ] && echo "Running in GitLab CI"
```

### Required Tools
Check that required tools are available:
```bash
command -v ruff && ruff --version
command -v eslint && npx eslint --version
command -v gdlint && gdlint --version
command -v mypy && mypy --version
```

## Cross-Platform Considerations

### Line Endings
```bash
# Check for mixed line endings
file * | grep -i "crlf\|dos"

# Git config should handle this
git config core.autocrlf
```

### Path Separators
- Code should use `pathlib.Path` (Python) or `path.join` (Node)
- Avoid hardcoded `/` or `\`

### Shell Scripts
```bash
# Check shebang
head -1 scripts/*.sh 2>/dev/null

# Shellcheck (if available)
shellcheck scripts/*.sh 2>/dev/null
```

## Quick Mode Subset

For `--quick` mode, run only these checks:
1. Git state (clean working directory)
2. Syntax check (files parse without error)
3. Critical lint rules only (E722, B006)
4. README exists

Skip:
- Full test suite
- Import checking
- Smoke tests
- Documentation completeness
