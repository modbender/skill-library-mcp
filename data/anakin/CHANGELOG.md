# Changelog

All notable changes to the Anakin OpenClaw skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-02-27

### Added
- Initial release of unified Anakin skill for OpenClaw
- Support for `anakin scrape` - single URL scraping with markdown, JSON, and raw formats
- Support for `anakin scrape-batch` - batch scraping up to 10 URLs simultaneously
- Support for `anakin search` - AI-powered web search
- Support for `anakin research` - deep agentic research with autonomous exploration
- Comprehensive documentation with examples and decision guides
- Error handling and troubleshooting guidance
- pip installer specification for anakin-cli
- Environment variable gating for ANAKIN_API_KEY
- Binary requirement check for anakin CLI

### Features
- JavaScript-heavy site support with `--browser` flag
- Geo-targeted scraping with `--country` flag
- Custom timeout configuration
- Multiple output formats (markdown, JSON, raw)
- Batch processing for parallel scraping
- Autonomous multi-source research

[1.0.0]: https://github.com/Anakin-Inc/anakin-cursor-plugin/releases/tag/v1.0.0
