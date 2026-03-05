# Changelog

All notable changes to ClawGuard will be documented in this file.

## [1.3.0] - 2026-02-09

### Added
- **Security Level System**: Graduated approval "temperature" control
  - Level 0 (silent): Threat DB checks only, warnings logged silently (DEFAULT)
  - Level 1 (cautious): Ask approval for WARNING-level threats
  - Level 2 (strict): Ask approval for warnings + ALL commands/unknown URLs
  - Level 3 (paranoid): Ask approval for everything except file reads
  - New CLI command: `clawguard config --level <0-3|name>`
  - Supports both numeric (0-3) and string names (silent/cautious/strict/paranoid)
  
- **Key Principle**: Static threat DB checks ALWAYS run (zero friction), approval layer is optional and graduated
  
- **Level 0 is the DEFAULT**: Most users never change from silent mode — just threat intel + audit logging running in background

### Changed
- Updated `openclaw-plugin.js` to respect security levels
- Plugin now logs current security level on initialization
- `clawguard config` now shows current security level
- `clawguard stats` now includes security level in output
- Updated SKILL.md with comprehensive security levels documentation
- Version bumped to 1.3.0

### Documentation
- Added detailed security levels table to SKILL.md
- Explained when to use each level
- Clarified that Level 0 (silent) has ZERO user friction

## [1.2.0] - 2026-02-09

### Added
- **OpenClaw Plugin Hook**: Auto-check all tool calls before execution
  - Hooks into `before_tool_call` event
  - Automatically checks `exec` commands and `web_fetch`/`browser` URLs
  - Blocks on threats (exit code 1), requests approval on warnings (exit code 2)
  - Plugin file: `openclaw-plugin.js`
  
- **Decision Audit Trail**: Comprehensive logging of all security checks
  - Append-only JSONL log at `~/.clawguard/audit.jsonl`
  - Logs: timestamp, type, input, verdict, threat details, duration
  - New CLI command: `clawguard audit` to view recent checks
  - Flags: `--today` (today's checks only), `--lines N` (last N checks)
  - Auto-enabled by default
  
- **Discord Approval for Warnings**: Human-in-the-loop for edge cases
  - When plugin detects a warning (exit code 2), sends Discord message
  - Includes threat details and asks for YES/NO approval
  - Waits for reaction (✅/❌) with configurable timeout (default 60s)
  - Blocks if denied or timeout, allows if approved
  - Only active in plugin mode (CLI keeps existing behavior)
  
- **Configuration System**: Centralized config management
  - New CLI command: `clawguard config` to view/edit settings
  - Config file: `~/.clawguard/config.json`
  - Settings for Discord (channel ID, timeout), audit trail, detection thresholds
  - Flags: `--get`, `--set`, `--enable`, `--disable`

### Changed
- Detector now auto-logs every check to audit trail
- Version bumped to 1.2.0

### Documentation
- Updated SKILL.md with new features section
- Added PLUGIN.md with plugin installation and usage guide
- Added tests for new features in `tests/new-features.test.js`

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-02-06

### Added
- **MCP Configuration Scanner** (`clawguard mcp-scan`) - Comprehensive security scanner for Model Context Protocol server configurations
  - Auto-discovers MCP configs from Claude Desktop, Cursor, VS Code, Windsurf, Claude Code, and Clawdbot
  - Detects hardcoded API keys (OpenAI, Anthropic, GitHub, AWS, Slack, SendGrid, Google, and 7 more)
  - Identifies unrestricted shell access (bash/sh/zsh/powershell)
  - Catches dangerous command patterns (curl|bash, sudo, eval, rm -rf)
  - Detects prompt injection patterns in tool descriptions
  - Flags unencrypted HTTP transport and 0.0.0.0 binding
  - Cross-references server URLs and packages against ClawGuard threat database
  - Exit codes for CI/CD integration (0=clean, 1=high, 2=critical)
  - Supports `--fix`, `--json`, `--severity`, and `--quiet` flags
  - CWE references for all findings
  - Security scoring (0-100 scale)

### Changed
- Updated README with comprehensive MCP scanning documentation
- Enhanced threat database integration to work with MCP server discovery

## [1.0.2] - 2026-02-05

### Fixed
- Fixed github.com false positive (domain whitelist now applied to message pattern matching)
- Added missing prompt injection patterns
- Fixed package.json bin path (`openclaw-security` → `clawguard`)

### Changed
- Restructured SKILL.md for agent-actionable format
  - Added YAML frontmatter per Agent Skills spec
  - Added critical warning box
  - Split into First-Time Setup vs Daily Use lifecycle
  - Added trigger conditions and exit code handling
  - Added copy-pasteable HEARTBEAT.md and AGENTS.md sections
- Updated README to reflect database is included (not "coming soon")

## [1.0.0] - 2026-02-05

### Added
- Initial release of ClawGuard
- 86+ threat entries covering:
  - Malicious skills (ClawHavoc campaign)
  - Payment scams (x402 Bitcoin scams)
  - Social engineering attacks
  - Prompt injection patterns
  - Dangerous infrastructure (C2 domains, phishing sites)
- Full 6-tier threat taxonomy
- CLI commands: check, search, show, stats, sync, report
- SQLite database with <1ms exact lookups
- Pattern matching and confidence scoring
- Pre-action hook integration support
- Auto-sync every 24 hours
- Privacy-focused (local-only detection, no telemetry)

[1.1.0]: https://github.com/jugaad-lab/clawguard/compare/v1.0.2...v1.1.0
[1.0.2]: https://github.com/jugaad-lab/clawguard/compare/v1.0.0...v1.0.2
[1.0.0]: https://github.com/jugaad-lab/clawguard/releases/tag/v1.0.0
