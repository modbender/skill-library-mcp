# Changelog

All notable changes to the Shortcut skill will be documented in this file.

## [1.4.1] - 2026-02-08

### Changed
- Cleaned up personal/workspace-specific references from README
- Updated documentation to use standard config paths (~/.config/shortcut/)
- Removed internal submission documentation

## [1.4.0] - 2026-02-08

### Added
- `shortcut-init-workflow.sh` script to auto-detect workspace-specific state IDs
- Support for configuring state IDs via `~/.config/shortcut/workflow-states`
- Environment variable overrides for all workflow states

### Changed
- Removed hardcoded "coalface" workspace references (now workspace-agnostic)
- Scripts now auto-load state IDs from config file or fall back to env vars/defaults
- Updated documentation to recommend running init script during setup

### Fixed
- Made skill portable across different Shortcut workspaces

## [1.3.0] - 2026-02-08

### Fixed
- Corrected workflow state IDs in `shortcut-update-story.sh` to match actual coalface workspace states
  - Backlog: 500000006
  - To Do: 500000007 (was incorrectly 500000006)
  - In Progress: 500000008 (was incorrectly 500000007)
  - In Review: 500000009 (new)
  - Done: 500000010

### Changed
- Updated SKILL.md documentation to reflect correct state IDs
- Added instructions for finding workspace-specific state IDs via API

## [1.2.0] - 2026-02-07

### Added
- Full checklist task management (create, update, edit, delete tasks)
- Comment management (add, update, delete comments)
- Story description support in create/update operations

## [1.1.0] - 2026-02-06

### Added
- Initial release with basic story management
- Create, list, show, and update stories
- Support for feature/bug/chore story types
