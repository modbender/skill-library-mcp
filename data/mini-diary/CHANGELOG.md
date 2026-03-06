# Changelog

All notable changes to Mini Diary will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.2] - 2026-02-23

### Security
- 🔒 Fixed critical security vulnerability: arbitrary file write via environment variables
- 🛡️ Added comprehensive path validation to all scripts
- 🔐 Implemented strict bash security mode (set -euo pipefail)
- ⚠️ Added security disclaimers to all scripts
- 🚫 Safe permission operations with ownership checks
- 📋 Restricted file operations to user directories only

### Changes
- Updated install.sh with safe chmod operations
- Added security headers to all bash scripts
- Improved error handling and user feedback
- Enhanced documentation for security features

## [0.1.0] - 2026-02-23

### Added
- Initial release of Mini Diary
- Core functionality: add notes with auto-tagging
- Search by tags, date, and content
- Basic statistics and tag frequency analysis
- Optional NextCloud integration with detailed guide
- Complete documentation and examples
- Installation script for easy setup

### Features
- **Auto-tagging system**: AI-powered content analysis
- **Smart search**: Multiple search options with context
- **Markdown format**: Open, portable diary files
- **Cloud sync**: NextCloud integration (optional)
- **Customizable**: Environment variables and configuration
- **Lightweight**: Minimal dependencies, fast operation

### Technical Details
- Built for OpenClaw agents
- Bash scripts for core functionality
- MIT licensed
- Full documentation included

### Known Limitations (v0.1.0)
- Basic keyword-based tagging (not full AI)
- No GUI interface (command-line only)
- NextCloud sync requires manual scan command
- Limited to predefined tag set

### Upcoming Features (Planned)
- Enhanced AI tagging with context understanding
- More search options and filters
- Export to various formats (PDF, CSV, etc.)
- Web interface option
- Mobile app integration
- Advanced statistics and charts

---

## Versioning Scheme

- **Major version (1.x.x)**: Breaking changes, major rewrites
- **Minor version (0.2.x)**: New features, backward compatible
- **Patch version (0.1.1)**: Bug fixes, minor improvements

## Contributing

Please see [CONTRIBUTING.md](docs/CONTRIBUTING.md) for how to contribute to Mini Diary.

## Support

For questions and support, please:
1. Check the [documentation](docs/usage_guide.md)
2. Search [existing issues](https://github.com/PrintXDreams/mini-diary/issues)
3. Create a new issue if needed