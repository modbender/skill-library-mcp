---
name: project-summary
description: Generate an instant codebase overview — language, framework, architecture, entry points, and key files
version: 1.0.0
author: Sovereign Skills
tags: [openclaw, agent-skills, automation, productivity, free, project, summary, overview, onboarding]
triggers:
  - summarize project
  - project overview
  - codebase summary
  - project summary
  - what is this project
---

# project-summary — Instant Codebase Overview

Generate a structured project summary for onboarding developers or providing context to agents.

## Steps

### 1. Scan Project Root

Read these files first (all optional):
- `package.json` / `pyproject.toml` / `Cargo.toml` / `go.mod` / `*.sln` / `*.csproj`
- `README.md` — existing description
- `LICENSE`
- `Dockerfile` / `docker-compose.yml`
- `.github/workflows/*.yml` / `.gitlab-ci.yml` / `Jenkinsfile`
- `tsconfig.json` / `babel.config.*` / `webpack.config.*` / `vite.config.*`
- `.eslintrc*` / `.prettierrc*` / `pyproject.toml [tool.ruff]`

### 2. Detect Language & Framework

**Primary language** — count file extensions:
```bash
find . -type f -not -path '*/node_modules/*' -not -path '*/.git/*' -not -path '*/dist/*' -not -path '*/target/*' -not -path '*/__pycache__/*' -not -path '*/.venv/*' | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -10
# Windows:
Get-ChildItem -Recurse -File -Exclude node_modules,.git,dist,target | Group-Object Extension | Sort-Object Count -Descending | Select-Object -First 10 Count,Name
```

**Framework** — check dependencies (see readme-generator skill for detection table).

### 3. Map Architecture

Identify the architecture pattern from directory structure:

| Structure | Pattern |
|-----------|---------|
| `src/controllers/`, `src/models/`, `src/routes/` | MVC |
| `src/features/*/`, each with components+hooks+api | Feature-based |
| `src/domain/`, `src/application/`, `src/infrastructure/` | Clean Architecture / DDD |
| `pages/` or `app/` (Next.js/Nuxt) | File-based routing |
| `cmd/`, `internal/`, `pkg/` | Go standard layout |
| `src/lib.rs`, `src/main.rs` | Rust binary/library |
| Flat structure, few files | Simple / Script |

### 4. Identify Entry Points

```bash
# Look for common entry points
ls -la src/index.* src/main.* app.* main.* index.* manage.py server.* 2>/dev/null
# Check package.json "main", "module", "bin", "scripts.start"
# Check Cargo.toml [[bin]] or src/main.rs
# Check pyproject.toml [project.scripts]
```

### 5. Catalog Key Files

List the most important files with one-line descriptions:

```markdown
## Key Files
| File | Purpose |
|------|---------|
| `src/index.ts` | Application entry point |
| `src/routes/` | API route definitions |
| `src/models/` | Database models / schemas |
| `src/middleware/` | Express middleware (auth, logging) |
| `prisma/schema.prisma` | Database schema |
| `docker-compose.yml` | Local development services |
| `.github/workflows/ci.yml` | CI pipeline — test + lint + build |
```

Focus on files a new developer needs to know about. Skip generated files, configs that are self-explanatory, and boilerplate.

### 6. Document Test Setup

```bash
# Detect test framework
grep -l "jest\|vitest\|mocha\|pytest\|unittest\|cargo test\|go test" package.json pyproject.toml Cargo.toml Makefile 2>/dev/null
# Find test files
find . -name "*.test.*" -o -name "*.spec.*" -o -name "test_*" -not -path '*/node_modules/*' 2>/dev/null | head -20
```

Report: test framework, test location, how to run tests, approximate test count.

### 7. Check CI/CD

If CI config exists, summarize:
- What triggers the pipeline (push, PR, schedule)
- What steps run (lint, test, build, deploy)
- Where it deploys to (if detectable)

### 8. Map Dependencies

List the top 10 most important dependencies (not all of them):
- Focus on framework, database, auth, testing, and build tools
- Note the approximate total count

```markdown
## Key Dependencies
| Package | Purpose |
|---------|---------|
| express | Web framework |
| prisma | Database ORM |
| jsonwebtoken | JWT authentication |
| jest | Testing framework |
| **Total** | **47 dependencies (12 dev)** |
```

### 9. Output Structured Summary

```markdown
# Project Summary: [name]

**Description:** [from package.json or README]
**Language:** TypeScript | **Framework:** Express.js | **Runtime:** Node.js 20
**Architecture:** MVC | **Package Manager:** pnpm
**License:** MIT

## Quick Start
[install + run commands]

## Structure
[architecture description + key directories]

## Key Files
[table from Step 5]

## Dependencies
[table from Step 8]

## Testing
- **Framework:** Jest
- **Run:** `pnpm test`
- **Coverage:** `pnpm test -- --coverage`

## CI/CD
- **Platform:** GitHub Actions
- **Triggers:** Push to main, PRs
- **Pipeline:** Lint → Test → Build → Deploy to Vercel

## Notes
[Anything unusual or important — monorepo setup, required services, known issues from README]
```

## Edge Cases

- **Monorepo**: Summarize root structure, then briefly describe each package/workspace
- **No manifest file**: Infer from file extensions and directory structure
- **Very large project (1000+ files)**: Limit scan depth to 3, focus on src/ and root
- **Multiple languages**: Report primary and secondary languages with percentages
- **Empty/new project**: Report as scaffold; note what's been set up vs. what's missing

## Error Handling

| Error | Resolution |
|-------|-----------|
| Permission denied on files | Skip and note which files couldn't be read |
| Massive repo, scan timeout | Limit to `src/`, root configs, and `find -maxdepth 3` |
| Unrecognized framework | Report as "custom" and describe what IS detectable |
| No README or description | Use directory name; note absence |

---
*Built by Clawb (SOVEREIGN) — more skills at [coming soon]*
