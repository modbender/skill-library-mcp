# Repository Guidelines

## Project Structure & Module Organization
- `google_tv_skill.py`: primary CLI entrypoint for ADB connection management, content routing, and media controls.
- `play_show_via_global_search.py`: helper for Google TV UI automation after a device is already connected.
- `test_google_tv_skill.py`: unit tests for parsing, routing helpers, cache handling, and package/env behavior.
- `run`: wrapper script that validates `uv` and `adb`, then runs the CLI.
- `README.md`, `SKILL.md`, `CHANGELOG.md`: usage, skill behavior, and change history.
- `.last_device.json`: local device cache (`ip` + `port`); runtime artifact, not source.

## Build, Test, and Development Commands
- `./run status --device <ip> --port <port>`: verify ADB connectivity and visible devices.
- `./run play "<query_or_id_or_url>" --device <ip> --port <port>`: route playback to YouTube, Tubi, or fallback flow.
- `./run pause --device <ip> --port <port>` / `./run resume ...`: media transport controls.
- `uv run test_google_tv_skill.py`: run full unit suite.
- `uv run test_google_tv_skill.py -v`: verbose test output.
- `uv run test_google_tv_skill.py TestYouTubeIDExtraction`: run a focused test class.

## Coding Style & Naming Conventions
- Target Python 3.11+ and standard library-first implementation.
- Use 4-space indentation, snake_case for functions/variables, and UPPER_CASE for module constants.
- Keep CLI behavior in `google_tv_skill.py`; keep UI-keypress automation isolated in `play_show_via_global_search.py`.
- Prefer small, testable helpers (e.g., `extract_youtube_id`, `looks_like_tubi`) over inline logic.

## Testing Guidelines
- Framework: `unittest` (pytest-compatible execution is optional).
- Name tests with `test_` methods inside `Test...` classes.
- Add or update tests with every behavior change, especially parsing, fallback routing, and cache edge cases.
- Run the full suite locally before opening a PR.

## Commit & Pull Request Guidelines
- Follow existing conventional prefixes seen in history: `fix:`, `test:`, `docs:`.
- Keep commit subjects concise and imperative (example: `fix: handle subprocess timeout in global search helper`).
- PRs should include:
  - clear behavior summary,
  - test evidence (command + result),
  - any manual device validation performed for ADB/UI automation changes.

## Security & Configuration Tips
- Never commit real network details from `.last_device.json`.
- Use env vars (`CHROMECAST_HOST`, `CHROMECAST_PORT`, `YOUTUBE_PACKAGE`, `TUBI_PACKAGE`) instead of hardcoding local values.
