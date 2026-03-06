# Repository Context Gathering

Before creating a PR, gather this context from the target repository.

## Essential Files to Read

### CONTRIBUTING.md
- Required PR format
- Branch naming conventions
- Commit message format
- CLA/DCO requirements
- Issue-first policies
- AI contribution policies

### .github/PULL_REQUEST_TEMPLATE.md
- Expected PR description format
- Required sections

### README.md
- Project purpose and scope
- Setup instructions
- Contribution guidelines if no CONTRIBUTING.md

---

## Code Style Detection

### Configuration Files to Check
| File | Reveals |
|------|---------|
| `.editorconfig` | Indentation, line endings |
| `.prettierrc` | Code formatting rules |
| `.eslintrc` | Linting rules |
| `tsconfig.json` | TypeScript strictness |
| `pyproject.toml` | Python formatting |

### Test Command Detection
| File | Check For |
|------|-----------|
| `package.json` | scripts.test, scripts.lint |
| `Makefile` | test, lint targets |
| `pyproject.toml` | pytest, ruff config |
| `.github/workflows/` | CI commands |

---

## Project Health Signals

### Activity Indicators
- Last commit date (stale if >6 months)
- Open PR response time
- Issue close rate

### Red Flags
- Many stale PRs with no response
- "Not accepting contributions" notice
- Archived repository

---

## What NOT to Read or Log

### Secrets
- `.env`, `.env.*` files
- `secrets/`, `credentials/`, `keys/` directories

### Sensitive Infrastructure
- Production URLs or IPs
- Database connection strings

---

## Quick Context Checklist

Before coding:
- [ ] Read CONTRIBUTING.md completely
- [ ] Check if issue exists and is open
- [ ] Verify no duplicate PRs
- [ ] Note target branch
- [ ] Note commit message format
- [ ] Sample code style from 5 files
- [ ] Understand test framework
- [ ] Verify project is actively maintained
- [ ] Check for AI contribution policy
