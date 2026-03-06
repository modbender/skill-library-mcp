# Contributing to agent-deep-research

Thanks for your interest in contributing. This document covers the development workflow and conventions.

## Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (see [install docs](https://docs.astral.sh/uv/getting-started/installation/))
- A Google API key (set `GOOGLE_API_KEY` or `GEMINI_API_KEY`)

## Development Setup

```bash
git clone https://github.com/24601/agent-deep-research.git
cd agent-deep-research
```

No virtual environment or `pip install` needed -- all scripts use [PEP 723](https://peps.python.org/pep-0723/) inline metadata and run directly via `uv run`.

## Running Locally

```bash
# Verify syntax
python3 -m py_compile scripts/research.py scripts/store.py scripts/upload.py scripts/state.py

# Smoke test
uv run scripts/state.py --help

# Manual integration tests (requires a Google API key)
uv run scripts/research.py start "test query" --timeout 120
uv run scripts/store.py list
```

## Code Style

- **PEP 8** for Python formatting
- **PEP 723** inline script metadata (dependencies declared in each script, not a central `requirements.txt`)
- **Dual-output convention**: stderr for human-readable output (rich formatting), stdout for machine-readable JSON
- Keep scripts self-contained -- each script in `scripts/` should be independently runnable via `uv run`

## Commit Convention

This project uses [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add store export command
fix: handle empty API response in research polling
docs: update README with new flags
chore: update CI workflow
```

Prefixes: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `ci`

## Pull Request Process

1. Fork the repository and create a feature branch from `main`
2. Make your changes
3. Verify your changes:
   ```bash
   python3 -m py_compile scripts/*.py
   uv run scripts/state.py --help
   ```
4. Commit using the conventional commit format
5. Open a pull request against `main`
6. Fill out the PR template

## Reporting Issues

Use the [issue templates](https://github.com/24601/agent-deep-research/issues/new/choose) to report bugs or request features. For security vulnerabilities, see [SECURITY.md](SECURITY.md).

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
