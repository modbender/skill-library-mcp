# Changelog

## 2.0.0

Breaking changes — new script name, rewritten SKILL.md.

### Changed
- **SKILL.md**: Restructured to match operational style. Added OpenClaw metadata to frontmatter. Removed marketing "Trigger Patterns" section. Consolidated time/frequency/channel tables into single "Supported Patterns" section. Added "How It Works" and "Command Reference" sections.
- **scripts/cron_builder.py**: New script replacing `cron_creator.py`. Written from scratch.

### Fixed
- `build_command` now includes `--session isolated` and `--deliver` flags (were missing in v1).
- One-shot schedules (`--at`) now use `--delete-after-run` and skip `--cron` (v1 always used `--cron`).
- Default channel changed from `whatsapp` to `telegram` (configurable via `CRON_DEFAULT_CHANNEL` env var).
- Removed dead `TIME_PATTERNS` dict that was never used by actual parsing.
- Removed `<YOUR_PHONE>` placeholder — defaults now match channel type.
- Frequency pattern ordering fixed: "weekly on Mondays" now correctly resolves to Monday, not generic weekly.

### Added
- `test/test_cron_builder.py` — 42 tests covering time parsing, frequency parsing, channel detection, command generation, and edge cases.
- OpenClaw frontmatter metadata (emoji, requires).
- Default time (9am) when no time specified for repeating schedules.

### Removed
- `scripts/cron_creator.py` (replaced by `cron_builder.py`).
- "Trigger Patterns" section from SKILL.md.

## 1.0.1

Initial fork from i-mw/cron-mastery. Published on ClawHub.
