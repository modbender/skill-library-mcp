# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-07

### Added
- Initial release of SonarQube Analyzer skill
- Support for fetching issues from SonarQube API
- Intelligent rule analysis with suggested solutions
- Auto-fixable vs manual-fix classification
- JSON and Markdown report generation
- CLI tool for command-line usage
- Support for pull request analysis
- Quality Gate status checking
- Support for TypeScript rules:
  - S3358 (Nested ternary)
  - S6606 (Nullish coalescing)
  - S6749 (Redundant fragment)
  - S6759 (Readonly props)
  - S3776 (Cognitive complexity)
  - S6571 (Redundant any)
- Comprehensive documentation
- OpenClaw integration with plugin manifest

[1.0.0]: https://github.com/FelipeOFF/sonarqube-analyzer/releases/tag/v1.0.0