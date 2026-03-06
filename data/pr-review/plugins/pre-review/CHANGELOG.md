# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-24

### Added
- Initial release
- `/pre-review` command for reviewing branch changes before PR
  - 5 parallel Sonnet agents for deep analysis
  - Haiku agents for coordination and confidence scoring
  - Auto-fix for issues with confidence >= 70
  - Git history analysis for regression detection
- `/code-audit` command for auditing existing code
  - Risk-based file prioritization (auth, payments, data access)
  - Security-focused analysis agents
  - Conservative auto-fix threshold (>= 80)
  - Comprehensive audit reports with security checklist
- Support for project guidelines discovery (CLAUDE.md, eslint, prettier, etc.)
- Confidence scoring system (0-100) to filter false positives
- Progress tracking via todo list
