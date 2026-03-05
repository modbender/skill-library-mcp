# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-02-24

### Added
- **Edit reminders**: `edit --id ID [--title ...] [--due ...] [--note ...]` to modify existing reminders
- **Delete reminders**: `delete --id ID` to remove reminders
- **Complete reminders**: `complete --id ID` to mark reminders as done
- **List with IDs**: `list` now returns `id` (calendarItemIdentifier) for each reminder via EventKit
- Locale strings for edit/delete/complete responses (en, ko, ja, zh)
- Trigger examples for edit/delete/complete in locales.json

### Changed
- **License**: Changed from CC-BY-NC-4.0 to MIT (commercial use now allowed)
- `list` command now uses Swift EventKit instead of AppleScript (returns IDs and richer data)
- Updated SKILL.md with edit/delete/complete documentation
- Updated README.md with new command examples

## [1.1.1] - 2026-02-10

### Fixed
- Timezone handling: now accepts any timezone offset (was limited to +09:00)
- Swift error propagation: JSON parse failures now properly reported as errors

## [1.1.0] - 2026-02-10

### Added
- **Native Recurrence**: `--repeat daily|weekly|monthly|yearly` option
- `--interval` option for custom repeat intervals (e.g., bi-weekly)
- `--repeat-end` option for recurrence end date
- Swift EventKit integration for native macOS recurrence rules
- Repeat indicator in title: `제목 (매주)`, `Title (Weekly)`, etc.
- Multi-language repeat labels in title (매주, Weekly, 毎週, 每周)

### Changed
- Updated documentation (SKILL.md, README.md) with recurrence examples

## [1.0.0] - 2026-02-04

### Added
- Initial release
- Multi-language support (en, ko, ja, zh)
- `locales.json` for language-specific triggers and responses
- `--locale` parameter for explicit language selection
- List reminders (`--scope today|week|all`)
- Add reminders (`--title`, `--due`, `--note`)
- AppleScript integration via `applescript` npm module
- iCloud sync support (automatic via macOS Reminders)
