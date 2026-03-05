# Changelog

All notable changes to the 1Password UI skill will be documented in this file.

## [1.1.0] - 2025-02-11

### Added
- **Full working implementation** with dashboard UI tab
- **Sign-in flow** directly from web interface
- **Connection status display** showing account, mode (CLI/Connect)
- **CLI mode support** for local installations
- **Connect mode support** for Docker installations
- **Credential mapping system** for skill integrations
- Complete reference implementations:
  - `1password-backend.ts` - Gateway RPC handlers (11 methods)
  - `1password-views.ts` - Lit template with sign-in UI
  - `1password-settings.ts` - Tab loading logic
- Detailed `INSTALL_INSTRUCTIONS.md` with exact code changes
- Agent installation prompt in SKILL.md

### Changed
- Skill now installs as a core tab (no plugin-architecture dependency)
- Updated all reference files with tested, working code
- Improved documentation with troubleshooting section

### Security
- Secrets never included in UI responses
- readSecret method is backend-only
- Mapping file contains references only, not actual secrets

## [1.0.0] - 2025-02-11

### Added
- Initial release with reference implementations
- Gateway RPC handlers design
- UI view templates
- Plugin registration (optional approach)
- Docker/Connect support documentation
- op-helper.py CLI bridge script
