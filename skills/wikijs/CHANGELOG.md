# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.0] - 2026-02-04

### Added
- `clone` command - Duplicate a page to a new location with `--with-tags` option
- `orphans` command - Find pages with no incoming links
- `replace` command - Search and replace text across multiple pages
- `toc` command - Generate table of contents for a page (markdown/json/html)
- `duplicates` command - Find pages with similar content
- `sitemap` command - Generate XML sitemap for SEO
- `shell` command - Interactive shell mode (REPL)
- `watch` command - Watch a page for changes with configurable interval
- `spellcheck` command - Basic spell checking with multilingual support (en/fr)
- `validate` command - Comprehensive page validation (images, links, content quality)
- Enhanced `stats` command with word count and reading time metrics

### Changed
- Improved shell completion with all new commands

## [1.3.0] - 2026-02-04

### Added
- `lint` command - Lint markdown files or wiki pages with `--fix` option
- `--lint` flag for `create` command to validate markdown before creating
- Offline mode support for `list` command:
  - `--offline` flag to use cached data when server is unavailable
  - `--save-offline` flag to cache page list for offline use
  - Automatic fallback to cached data on connection failure
- Unit tests with Jest
- Shell completion now includes all commands

### Changed
- Improved shell completion scripts with all available commands
- Test script now uses Jest instead of health check

### Fixed
- Various edge cases in markdown linting
- Better handling of offline scenarios

## [1.2.0] - 2026-02-04

### Added
- `tree` command - Display page hierarchy as a visual tree
- `diff` command - Compare page versions
- `check-links` command - Find broken internal links across all pages
- `template` command - Manage page templates (list, show, create, delete)
- `completion` command - Generate shell completion scripts (bash/zsh/fish)
- `cache` command - Manage local cache (clear, info)
- `--template` option for `create` command
- Global options: `--verbose`, `--debug`, `--no-color`, `--rate-limit`
- Progress bars for bulk operations
- Rate limiting support for API calls
- Local caching system for improved performance
- Input sanitization for GraphQL queries (security)

### Changed
- Bulk operations now show progress bars
- API calls can be rate-limited with `--rate-limit <ms>`
- Debug output available with `--debug` flag
- Colors can be disabled with `--no-color` for CI/scripts

### Security
- Added `sanitizeString()` to prevent GraphQL injection
- Added `validateId()` and `validatePath()` for input validation

## [1.1.0] - 2026-02-03

### Added
- `restore-backup` command to restore pages from backup files
- `bulk-update` command to update multiple pages from local files
- `revert` command to restore a page to a previous version
- `sync --watch` mode for periodic synchronization
- Interactive confirmation prompts for delete operations (pages and assets)
- `--locale` option for `get` command to specify locale for path lookups
- Escape sequence interpretation (`\n`, `\t`, `\r`) in `--content` flag

### Changed
- Improved GraphQL error handling with detailed error messages
- Delete commands now prompt for confirmation (use `--force` to skip)
- Updated documentation to English

### Fixed
- GraphQL errors now show actual error message instead of "status 400"

## [1.0.0] - 2026-02-03

### Added
- Initial release
- Core commands: `list`, `search`, `get`, `create`, `update`, `move`, `delete`
- Tag management: `tags`, `tag add/remove/set`
- Asset management: `images`, `upload`, `delete-image`
- Export/backup: `export`, `backup`
- Search: `grep` for content search across pages
- System: `health`, `stats`, `info`, `versions`
- Bulk operations: `bulk-create`, `sync`
- Support for Wiki.js 2.x GraphQL API
- JSON and table output formats
- Configuration via `~/.config/wikijs.json`
