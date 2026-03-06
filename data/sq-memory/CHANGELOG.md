# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-02-11

### Added
- Initial release of SQ Memory skill for OpenClaw
- Core memory functions: `remember()`, `recall()`, `forget()`, `list_memories()`
- Support for both SQ Cloud and self-hosted SQ endpoints
- Namespace isolation for multi-agent setups
- Shorthand coordinate syntax (e.g., `user/preferences/theme`)
- Automatic coordinate expansion to full 11D phext format
- HTTP and HTTPS endpoint support
- Optional API key authentication for SQ Cloud
- Comprehensive test suite (`test.js`)
- Three usage examples:
  - `user-preferences.js` - Personal preference tracking
  - `conversation-history.js` - Long-term conversation memory
  - `multi-agent-coordination.js` - Distributed task coordination
- Documentation:
  - `README.md` - Overview and quick reference
  - `SKILL.md` - Full skill documentation
  - `QUICKSTART.md` - 5-minute setup guide
  - `SELF-HOSTED.md` - Self-hosting instructions
- OpenClaw skill.json manifest for tool registration

### Features
- **Persistent Memory**: Survives agent restarts
- **11D Addressing**: Hierarchical coordinate system
- **JSON Support**: Store complex objects as JSON strings
- **Large Text**: Tested up to 10KB+ per coordinate
- **Multi-Agent**: Shared memory at agreed coordinates
- **No Database**: Direct text storage via SQ
- **WAL Support**: Write-ahead logging for durability

### Requirements
- Node.js >= 18.0.0
- OpenClaw >= 2026.2.0
- SQ endpoint (local or cloud)

### Known Limitations
- Max 1MB per coordinate (SQ limitation)
- No built-in search (use `list_memories()` + filter)
- No transactions across multiple coordinates

## [1.0.1] - 2026-02-11

### Fixed
- **CRITICAL: Missing `p=` parameter in API calls** - All API endpoints now include `&p=${phext}` parameter for proper phext isolation (discovered during Tester onboarding)
- Install command in docs updated from `openclaw skill install` to `npx clawhub install` (correct method)

### Added
- `phext` config option (defaults to `namespace` value if not specified)

### Changed
- All API calls now include phext name parameter for proper multi-tenant isolation

## [Unreleased]

### Planned
- WebSocket support for real-time memory updates
- Batch operations for multiple remember/recall/forget calls
- Built-in search with coordinate pattern matching
- Memory snapshots for point-in-time recovery
- Integration with OpenClaw session context
- Agent memory profiling tools
- Memory garbage collection helpers
- Coordinate migration utilities
