# Contributing to surreal-skills

Thank you for your interest in contributing to the SurrealDB 3 skill for AI coding agents. This guide covers everything you need to get started.

## Prerequisites

- **Python 3.10+** (for running scripts)
- **[uv](https://docs.astral.sh/uv/)** (Python package runner; no virtual environment needed)
- **SurrealDB CLI v3+** (`surreal` binary on your PATH)
- **Git** with [Conventional Commits](https://www.conventionalcommits.org/) knowledge

## Development Setup

```bash
# Clone the repository
git clone https://github.com/24601/surreal-skills.git
cd surreal-skills

# Verify prerequisites
surreal version          # Should show v3.x
python3 --version        # Should show 3.10+
uv --version             # Should show latest uv

# Run the doctor script to verify your environment
uv run scripts/doctor.py

# Run the onboard script to test the setup wizard
uv run scripts/onboard.py --help
```

No virtual environment is required. All Python scripts use [PEP 723](https://peps.python.org/pep-0723/) inline metadata, so `uv run` resolves dependencies automatically.

## Project Structure

```
surreal-skills/
  SKILL.md              # Main skill manifest (frontmatter + body)
  rules/                # Knowledge base (Markdown rule files)
  scripts/              # Python tooling (PEP 723, run with uv)
  skills/               # Sub-skill manifests
  references/           # External links and cheatsheets
  tests/                # Test scripts
  .github/              # CI/CD workflows and templates
```

## Code Style

### Python Scripts (`scripts/`)

- Follow **PEP 8** for formatting.
- Use **PEP 723** inline script metadata for dependencies. Every script must be runnable with `uv run scripts/<name>.py` without a prior install step.
- Include a module-level docstring describing the script's purpose.
- Use `argparse` for CLI arguments.
- Target Python 3.10+ (use `match` statements, `|` union types where appropriate).

### Rule Files (`rules/`)

- Write in standard Markdown.
- Begin each file with a top-level heading (`# Title`).
- Use fenced code blocks with language tags for all examples.
- Prefer concrete, copy-pasteable examples over abstract descriptions.
- Keep each rule file focused on a single topic.

### SKILL.md Manifests

- Frontmatter must be valid YAML between `---` delimiters.
- Required fields: `name`, `description`, `license`, `metadata.version`, `metadata.author`.

## Adding or Updating Rules

1. Create or edit the appropriate file in `rules/`.
2. If adding a new rule file, update `SKILL.md` to reference it in the body section.
3. Ensure all SurrealQL examples are valid against SurrealDB v3.
4. Add the file to the expected-files list in `.github/workflows/ci.yml` if it is a new rule.

## Commit Convention

This project uses [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add vector search rule file
fix: correct SurrealQL syntax in graph-queries.md
docs: update SDK examples for Python client v2
chore: update CI workflow for new rule file
```

Common types: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `ci`.

## Pull Request Process

1. **Fork** the repository and create a feature branch from `main`.
2. Make your changes following the style guidelines above.
3. Run the CI checks locally:
   ```bash
   # Syntax check all Python scripts
   python3 -m py_compile scripts/onboard.py
   python3 -m py_compile scripts/doctor.py
   python3 -m py_compile scripts/schema.py

   # Smoke test
   uv run scripts/onboard.py --help
   ```
4. Ensure all expected rule files exist.
5. Open a pull request against `main` using the PR template.
6. Fill out the checklist in the PR template.
7. A maintainer will review and provide feedback.

## Issue Templates

When filing issues, please use the provided templates:

- **Bug Report**: For errors in scripts, incorrect SurrealQL in rules, or CI failures.
- **Feature Request**: For new rules, script enhancements, or sub-skill ideas.

## Code of Conduct

Be respectful, constructive, and collaborative. We follow standard open-source community norms. Harassment, discrimination, and bad-faith contributions are not tolerated.

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
