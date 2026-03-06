# Changelog

All notable changes to this project are documented here.

## [2.0.1] - 2026-03-03

### Changed
- Set `x-client-type` header to `youmind-skill` (was `web`) so server-side can distinguish skill requests from browser requests

## [2.0.0] - 2026-02-22

### Added
- **Youmind adaptation** of the original NotebookLM skill architecture
- New `board_manager.py` for Youmind board library management
- New `board_manager.py smart-add` workflow with two-pass discovery and fallback parsing

### Changed
- Reworked `ask_question.py` from NotebookLM notebook flow to Youmind board chat flow
- Reworked `auth_manager.py` for Youmind sign-in and validation routes
- Updated `config.py` selectors and URL constants for Youmind
- Updated `SKILL.md`, `README.md`, and `references/*` to Youmind terminology/workflow
- Updated `run.py` command guidance to `board_manager.py`

### Fixed
- Added missing `random_mouse_movement` utility used by `browser_session.py`
- Aligned browser install target to Chrome in `scripts/__init__.py`

## [1.3.0] - 2025-11-21

### Added
- Modular architecture refactor (`config.py`, `browser_utils.py`)

### Changed
- Query timeout increased to 120 seconds

### Fixed
- Thinking-message detection and response stability polling
- NotebookLM selector updates for then-current UI

## [1.2.0] - 2025-10-28

### Added
- Initial public release
- NotebookLM browser automation integration
