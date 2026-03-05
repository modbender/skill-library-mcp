# AGENTS.md

Instructions for AI agents working on this repository.

## Overview

**airbnb-search** is a CLI tool for searching Airbnb listings. Uses Airbnb's internal GraphQL API (no browser automation).

## Development

### Setup

```bash
git clone https://github.com/Olafs-World/airbnb-search.git
cd airbnb-search
uv sync
```

### Running Tests

```bash
uv run pytest                        # All tests
uv run pytest -m "not integration"   # Unit tests only (CI uses this)
uv run ruff check .                  # Linting
```

### Testing Locally

```bash
uv run airbnb-search "Denver, CO" --checkin 2025-03-01 --checkout 2025-03-03
```

## Project Structure

```
airbnb_search/
├── __init__.py      # Package exports
├── cli.py           # CLI entry point (argparse)
├── search.py        # Core search logic (GraphQL API calls)
tests/
├── test_cli.py      # CLI tests
├── test_search.py   # Search function tests (unit + integration)
```

## Making a Release

**⚠️ NEVER manually publish to PyPI!** Always use git tags - CI handles PyPI automatically.

### Release Process

1. **Bump version** in `pyproject.toml`
2. **Update CHANGELOG.md** with changes under new version header
3. **Commit**: `git add -A && git commit -m "Bump version to X.Y.Z"`
4. **Tag**: `git tag vX.Y.Z`
5. **Push both**: `git push && git push --tags`

CI will automatically:
- Run tests on Python 3.8-3.12
- Publish to PyPI (only on tag push)

6. **Create GitHub Release** (optional but recommended):
   - Go to Releases → Draft new release
   - Select the tag you just pushed
   - Copy release notes from CHANGELOG.md

### Why not manual PyPI publish?

- Keeps GitHub releases and PyPI versions in sync
- Ensures tests pass before publishing
- Creates audit trail via CI logs
- Prevents accidental publishes of broken code

## Code Style

- Use `ruff` for linting
- Follow existing patterns in the codebase
- Keep CLI output user-friendly with emoji
- Support both `--output text` and `--output json`

## API Notes

- Uses Airbnb's internal `StaysSearch` GraphQL endpoint
- No authentication required
- Rate limiting: be respectful, don't hammer the API
- API may change without notice (Airbnb doesn't publish it)

## Dependencies

- `requests` - HTTP client
- `pytest` - Testing (dev)
- `ruff` - Linting (dev)

## Git Conventions

- Commit messages: imperative mood ("Add feature" not "Added feature")
- Co-author AI contributions: `Co-authored-by: olaf-s-app[bot] <259723076+olaf-s-app[bot]@users.noreply.github.com>`
