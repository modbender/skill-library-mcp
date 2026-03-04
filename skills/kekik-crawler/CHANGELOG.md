# Changelog

## v0.1.0-rc1 - 2026-02-26

### Added
- Scrapling-only backend (`backends/scrapling_backend.py`)
- Deterministic crawl pipeline with role-friendly orchestration
- Presets: `person-research`, `deep-research`
- Core modules split by responsibility:
  - `core/crawl_runner.py`
  - `core/fetcher.py`
  - `core/plugin_manager.py`
  - `core/robots.py`
  - `core/storage.py`
  - `core/checkpoint.py`
  - `core/mode.py`
  - `core/errors.py`
  - `core/metrics.py`
  - `core/search_engines.py`
  - `core/urlutils.py`
- Basic test suite under `tests/`
- Project metadata via `pyproject.toml`

### Changed
- `crawler.py` converted to compatibility wrapper
- Output convention standardized under `outputs/`
- README rewritten with clean architecture + usage

### Fixed
- URL canonicalization robustness (scheme-less, empty input, case-insensitive tracking params)
- Plugin fallback behavior when domain plugin/default plugin load fails
- Checkpoint load safety for corrupted checkpoint content
- Improved error classification behavior in runner paths

### Quality Gates
- `pytest`: 5 passed
- Bytecode compile checks passed

