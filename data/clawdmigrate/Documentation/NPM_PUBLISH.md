# NPM Publish – Feature Tracking

## Overview

**clawd_migrate** is deployable to NPM so users can install and run it with `npm install clawd-migrate` or `npx clawd-migrate`. The NPM package wraps the Python tool; Node runs the bin script, which invokes Python with the bundled package.

## Status

- **Added:** 2025-02-01
- **Package name:** `clawd-migrate`
- **Bin:** `clawd-migrate` → `bin/clawd-migrate.js`

## Requirements for users

- **Node.js** 14+ (to run the npm-installed command)
- **Python** 3.x (required by the migration tool)

## Package layout (published tarball)

- `package.json`
- `bin/clawd-migrate.js` – runs `python -m clawd_migrate` with `PYTHONPATH=lib`
- `lib/clawd_migrate/` – Python package (copied on prepublish from repo root)

## Repo layout (development)

- Python source stays at repo root (`__init__.py`, `config.py`, etc.).
- `prepublishOnly` runs `scripts/copy-py.js`, which copies `.py` files and `Documentation/` into `lib/clawd_migrate/` so the npm pack includes the correct structure.

## Files added

| File | Purpose |
|------|--------|
| `package.json` | NPM package manifest, bin, files, prepublishOnly |
| `bin/clawd-migrate.js` | Cross-platform bin: sets PYTHONPATH, runs Python module |
| `scripts/copy-py.js` | Copies Python package into `lib/clawd_migrate/` for publish |
| `README.md` | Install and usage for npm/GitHub |
| `Documentation/NPM_PUBLISH.md` | This doc |

## Publishing (manual)

1. Bump version in `package.json` (and optionally in `__init__.py`).
2. From repo root: `npm run prepublishOnly` (optional; runs automatically on publish).
3. `npm publish` (requires npm login and publish rights).

Scoped package (e.g. `@yourscope/clawd-migrate`): set `"name": "@yourscope/clawd-migrate"` in `package.json` and use `npm publish --access public` if the scope is unscoped by default.

## Notes

- The bin script uses `python3` on non-Windows and `python` on Windows; users must have Python on PATH.
- Only `bin/` and `lib/` are included in the tarball (`files` in package.json).
- Do not commit `lib/` if it’s generated; it’s created during prepublish and packed from there.
