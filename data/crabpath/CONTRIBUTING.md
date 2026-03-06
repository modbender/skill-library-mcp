# Contributing

## Development setup

1. Clone the repository and enter it:
   - `git clone <repo-url>`
   - `cd <repo>`
2. Create or activate your environment, then install editable:
   - `pip install -e .`
3. Run the test suite:
   - `pytest`

## Code style

- No linter is currently required by the project.
- Public functions must have docstrings.
- Keep interfaces focused and backward-compatible where possible.

## Test requirements

- All tests must pass before opening a PR.
- The test suite currently has 200 tests.
- Run the full suite with:
  - `python3 -m pytest tests/ -x -q`
- Add tests for new features and bug fixes when behavior changes or new API
  shapes are introduced.

## Running simulations

Use the deterministic simulation harness to validate behavior after graph and CLI updates:

- Build and run all simulation suites with:
  - `python3 sims/run_all.py`
- The script prints per-simulation pass/fail summaries and should complete with
  exit code `0` before merging changes that affect learning behavior.

## Release process

1. Bump version in both:
   - `pyproject.toml`
   - `crabpath/__init__.py`
2. Create a release commit/tag:
   - `git tag vX.Y.Z`
3. Push commits and tags:
   - `git push`
   - `git push --tags`

## Releasing

Releases are published via GitHub Actions with OIDC (trusted publishing):

- Ensure `secrets` are not used for package credentials.
- Push a signed tag that matches `vX.Y.Z` to trigger `.github/workflows/publish.yml`.
- The workflow requires `permissions: id-token: write` and publishes through
  `pypa/gh-action-pypi-publish` in the `pypi` environment.
- Confirm a successful publish in the Actions tab after the tag workflow completes.
