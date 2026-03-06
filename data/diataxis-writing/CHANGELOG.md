# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.1] - 2026-02-25

### Changed
- Restructured directory: moved checklist files from `references/` to dedicated `checklist/` directory
- Updated checklist reference paths in SKILL.md

### Added
- Created CHANGELOG.md (following Keep a Changelog specification)

## [1.2.0] - 2026-02-25

### Added
- Added output platform reference document (`references/output-platforms.md`)
- Added output handler script (`scripts/output-handler.py`) with auto-detection of available tools
- Added mandatory tool availability check step (before writing workflow)
- Added support for multiple output methods (Chat, Feishu MCP, Local Markdown, GitHub)

### Changed
- Improved output method documentation in SKILL.md, clarified MCP/mcporter usage for Feishu
- Updated script paths to use relative paths (avoid hardcoded absolute paths)
- Extended trigger words list to 40+ items (Chinese and English)

### Fixed
- Fixed script path dependency issues (changed to relative paths)
- Fixed MCP configuration path documentation (supports multiple locations)

---

## [1.1.0] - 2026-02-25

### Added
- Added 4 documentation type checklists:
  - `checklist-tutorial.md` - Tutorial checklist
  - `checklist-how-to.md` - How-to Guide checklist
  - `checklist-reference.md` - Reference checklist
  - `checklist-explanation.md` - Explanation checklist
- Added error logging mechanism and error logs directory (`error-logs/`)
- Added mandatory pre-task checklist (executed when receiving tasks)

### Changed
- Rewrote all files in English (maintain theoretical purity)
- Improved SKILL.md pre-writing questions (clarified language preference and output method)
- Extended trigger words list (includes Chinese and English trigger words)

### Fixed
- Fixed insufficient skill trigger words (expanded from 10+ to 40+)
- Fixed inaccurate document type diagnosis (improved compass tool documentation)

---

## [1.0.0] - 2026-02-25

### Added
- Initial release
- Complete Diataxis theoretical framework (based on https://diataxis.fr)
- Four documentation types detailed (Tutorial, How-to Guide, Reference, Explanation)
- Diataxis Compass decision tool
- Diataxis Map theoretical model
- Quality assessment framework (Functional Quality + Deep Quality)
- Common mistakes documentation
- Four type language style guide
- 8 scenario-based templates:
  - `template-tutorial.md`
  - `template-how-to.md`
  - `template-reference.md`
  - `template-explanation.md`
  - `template-troubleshooting.md`
  - `template-best-practices.md`
  - `template-learning-notes.md`
  - `template-exploration.md`
- Document type diagnosis script (`scripts/diagnose.py`)

---

## Version Notes

### Semantic Versioning (SemVer)

This project follows semantic versioning `Major.Minor.Patch`:

- **Major**: Incompatible API changes or major feature adjustments
- **Minor**: Backward-compatible feature additions
- **Patch**: Backward-compatible bug fixes

### Change Categories

- **Added**: New features
- **Changed**: Changes to existing functionality
- **Deprecated**: Features to be removed in future (deprecation notices)
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security improvements or vulnerability fixes

---

## Version History Summary

| Version | Release Date | Key Changes |
|---------|-------------|-------------|
| 1.2.1 | 2026-02-25 | Checklist directory restructuring + CHANGELOG creation |
| 1.2.0 | 2026-02-25 | Output management capabilities enhanced |
| 1.1.0 | 2026-02-25 | Checklists and error logging mechanism |
| 1.0.0 | 2026-02-25 | Initial release |

---

**Last Updated**: 2026-02-25  
**Maintainer**: Zhua Zhua  
**Theory Source**: https://diataxis.fr
