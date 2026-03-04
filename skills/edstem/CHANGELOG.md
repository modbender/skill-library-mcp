# Changelog

All notable changes to the EdStem skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-02-17

### Changed
- **BREAKING**: Removed hardcoded Columbia course ID mappings
- Made skill institution-agnostic to work with any EdStem-using institution
- Changed Python script to accept command-line arguments instead of hardcoded mappings
- Default output directory now `./edstem-<course_id>` instead of fixed course paths
- Updated bash script to accept `[output_dir]` instead of `<course_dir_name>`

### Added
- `--course-name` option to specify custom course name
- `--limit` option to control number of threads fetched (default: 10)
- `output_dir` positional argument for flexible output location
- Auto-detection of course name from EdStem API
- Improved error handling for missing user data in threads
- VERSION file with semver version tracking
- README.md for ClawHub/repository listing
- CHANGELOG.md for version history
- Comprehensive documentation for multi-institution use
- Examples for different institutions (Stanford, MIT, etc.)
- Troubleshooting section in SKILL.md
- Integration examples for LLM agents and automation

### Fixed
- Handle missing user data gracefully (shows "(Unknown)" instead of crashing)
- Better error messages when course not found
- Improved path resolution (shows absolute path on completion)

### Documentation
- Removed all Columbia-specific language from SKILL.md
- Added "Finding Your Course ID" section
- Added "Integration Examples" section
- Added "Troubleshooting" section
- Updated all usage examples to be institution-neutral
- Clarified authentication token setup process

## [1.0.0] - 2025-02-17

### Added
- Initial release of EdStem skill
- Python script for fetching and formatting EdStem threads
- Bash script alternative for raw JSON fetching
- Staff/student role differentiation
- Markdown formatting for threads, answers, and comments
- JSON cache of thread metadata
- Support for Columbia courses (hardcoded mappings)
- SKILL.md documentation
