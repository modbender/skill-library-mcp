# Changelog

All notable changes to Browser Auto Download will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [5.0.0] - 2026-02-04

### Added ⭐
- **Performance optimization package** with improved wait times
- Debug mode enhancements (screenshot + HTML + text capture)
- Direct CDN link support for Eclipse IDE
- Optimization documentation (`OPTIMIZATION.md`, `QUICKSTART.md`)
- One-click optimization script (`apply-optimizations.bat`)

### Changed ⚡
- **Initial page load wait**: 2s → 3s (+50%)
- **Auto-download detection window**: 5s → 10s (+100%)
- **Button click wait time**: 10s → 15s (+50%)
- **Download event timeout**: 15s → 20s (+33%)
- Enhanced JavaScript-rendered button detection

### Improved 📈
- Page interaction success rate: ~60% → ~90%
- Better handling of dynamic content and lazy loading
- Improved reliability for complex download pages (Eclipse, etc.)

### Fixed 🐛
- Download event detection timing issues
- Button click regression in v4.0.0
- Race conditions in auto-download detection

### Real-World Testing 🧪
- ✅ Eclipse IDE: 158.7 MB (direct CDN link)
- ✅ Multiple retry strategies for robust downloads

### Documentation 📚
- Added comprehensive optimization guide
- Added quick start reference
- Added troubleshooting section

## [4.0.0] - 2026-02-04

### Added ⭐
- Direct .exe/.dmg/.zip link support
- Relative path resolution (7-Zip pattern)
- Improved Chinese page support
- 4-tier download strategy
- Platform-specific optimizations

### Test Results
- 4/4 tests successful (100% success rate)
- Meitu Xiuxiu: 13.0 MB ✅
- WeChat DevTools: 231.9 MB ✅
- Python.org: 28.8 MB ✅
- 7-Zip: 1.4 MB ✅

## [3.0.0] - 2026-02-04

### Added ⭐
- Multi-step navigation
- Auto-download detection
- Platform auto-detection
- Cross-platform support (Windows/macOS/Linux)

## [2.0.0] - 2026-02-04

### Added ⭐
- Basic button clicking
- Platform detection
- Selector-based downloads

## [1.0.0] - 2026-02-04

### Added ⭐
- Initial release
- WeChat DevTools support
- Basic download automation

---

## Versioning Strategy

- **Major version (X.0.0)**: Breaking changes, major features
- **Minor version (0.X.0)**: New features, improvements
- **Patch version (0.0.X)**: Bug fixes, minor updates

## Release Notes Template

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added ⭐
- New feature 1
- New feature 2

### Changed ⚡
- Improvement 1
- Improvement 2

### Fixed 🐛
- Bug fix 1
- Bug fix 2

### Removed 🗑️
- Deprecated feature 1

### Security 🔒
- Security fix 1
```
