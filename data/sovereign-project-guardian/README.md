# sovereign-project-guardian

Project health and best practices enforcer. Evaluates security, quality, documentation, CI/CD, and code hygiene. Produces a letter grade (A-F) with a prioritized action plan.

## What It Does

When you install this skill, your AI agent can evaluate any project and tell you exactly what is wrong, how severe it is, and how to fix it -- in priority order.

The guardian checks 18 aspects of your project across 5 categories:

### Security (30% of score) -- Checked First
- No secrets in repository (API keys, passwords, tokens)
- Environment files protected via .gitignore
- Dependencies pinned with lock files
- Security middleware/configuration present

### Quality (25% of score)
- Tests exist with proper configuration
- Test coverage configured with thresholds
- Linting and formatting set up
- Type safety enabled (TypeScript, mypy, etc.)

### Documentation (20% of score)
- README exists and is substantive
- LICENSE file present
- CHANGELOG or release notes maintained
- API documentation for libraries/APIs

### CI/CD and Operations (15% of score)
- Automated build/test pipeline configured
- Code review process artifacts (CODEOWNERS, PR templates)
- Reproducible deployment (Dockerfile, IaC)

### Code Hygiene (10% of score)
- .gitignore covers all standard patterns
- No large binary files committed
- Consistent code style with enforcement

## Grading Scale

| Grade | Score | Meaning |
|-------|-------|---------|
| A | 90-100 | Excellent. Production-ready |
| B | 75-89 | Good. Minor improvements needed |
| C | 60-74 | Acceptable. Several gaps |
| D | 40-59 | Poor. Not production-ready |
| F | 0-39 | Failing. Major work needed |

Grade caps apply: secrets in repo caps at D, no tests caps at C, no README caps at C.

## Supported Project Types

- **Node.js** -- web apps, APIs, libraries, CLI tools
- **Python** -- packages, web apps, scripts
- **Go** -- services, libraries, CLI tools
- **Rust** -- binaries, libraries

## Install

```bash
clawhub install sovereign-project-guardian
```

## Usage

```
Evaluate the health of this project and give me a grade with action items.
```

```
What is my project's health score? What should I fix first?
```

```
Run a project guardian check and tell me the top 3 things to improve.
```

## Files

| File | Description |
|------|-------------|
| `SKILL.md` | Complete evaluation methodology with 18 checks across 5 categories |
| `EXAMPLES.md` | Step-by-step example taking a Node.js project from F to A |
| `README.md` | This file |

## License

MIT
