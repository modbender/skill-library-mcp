# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog (https://keepachangelog.com/en/1.1.0/)
and this project adheres to Semantic Versioning (https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-02-12

### Added

- `pair` command for ADB wireless pairing with Chromecast devices.
- `--show-instructions` flag for `pair` command to display detailed pairing setup guide.
- Interactive pairing flow when connection is refused with options to retry, pair, or view instructions.
- `adb_pair()` function to handle ADB wireless pairing.
- `print_pairing_instructions()` function to display step-by-step pairing guide.
- `prompt_for_pairing()` function to interactively guide users through pairing or port retry.
- Unit tests for ADB pairing functionality.

### Changed

- Updated `ensure_connected()` to offer pairing option when connection is refused in interactive mode.
- Enhanced `try_prompt_new_port()` to use new interactive pairing flow.
- Updated documentation in README.md and SKILL.md to include pairing prerequisites and instructions.
- Updated module docstring to document new pairing command.

## [1.0.1] - 2026-02-08

### Documentation

- Updated runtime requirements in `README.md` to require `adb`, `scrcpy`, `yt-api`, and `uv`.
- Updated `SKILL.md` metadata and setup/dependency notes to include `yt-api` installation and PATH requirements.
- Clarified fallback behavior notes in `SKILL.md`.

## [1.0.0] - 2026-02-07

### Fixed

- Improved ADB command execution and error handling in global search.
- Handled subprocess timeout in the global search helper.

### Documentation

- Updated `SKILL.md` description.
- Added `scrcpy` requirement and install helper metadata.

## [0.1.0] - 2026-02-06

- Initial release.
