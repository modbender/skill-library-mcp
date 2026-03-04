## v2.4.1 — 2026-03-01

### Fixed
- skill.yml: add permissions block (exec/filesystem/network/credentials) to resolve OpenClaw security scan "Suspicious" flag
- Version bump for re-scan

## v2.4.0 — 2026-03-01

### Added
- Vendored baoyu-markdown-to-html renderer into `scripts/renderer/` — no longer requires separate clone
- Persistent preview server via systemd (`wechat-preview.service`, port 8898, auto-restart)
- `setup.sh`: installs bun runtime + renderer deps + systemd service in one step

### Changed
- `format.sh`: switched from wenyan-cli to bundled baoyu renderer (default theme: classic WeChat H2 headers)
- Theme selection: `bash format.sh <dir> <file> [default|grace|simple]`
- SKILL.md frontmatter: stripped to name+description only (skill-creator spec compliance)
- SKILL.md: Step 6/7 updated for new renderer and port 8898
- `REFERENCES/` renamed to `references/` (all lowercase)

### Removed
- Dependency on wenyan-cli
- Dependency on /tmp/baoyu-skills clone
