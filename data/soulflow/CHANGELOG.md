# Changelog

All notable changes to SoulFlow will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-02-12

### Added
- **Workflow completion notifications**: Workflows now automatically notify the main session when complete
- Success notifications include workflow name, run ID, duration, and key results
- Failure notifications include error details and failed step name
- Notifications sent via `chat.send` to `agent:main` session

### Changed
- Improved error handling for notification delivery (non-blocking)

## [1.0.0] - 2026-02-12

### Added
- Initial release of SoulFlow workflow framework
- Zero-dependency Node.js 22 implementation with native WebSocket
- Gateway-native integration with challenge-response auth
- Session isolation per workflow step
- Dedicated `soulflow-worker` agent with minimal context
- JSON workflow definitions with variable interpolation
- Natural language workflow invocation support
- Interactive workflow builder (`lib/workflow-builder.js`)
- Natural language handler for agent integration (`lib/nl-handler.js`)
- Three example dev workflows:
  - `security-audit`: Scan → Prioritize → Fix → Verify
  - `bug-fix`: Triage → Fix → Verify
  - `feature-dev`: Plan → Implement → Review
- Two general-purpose example workflows:
  - `content-pipeline`: Research → Draft → Edit
  - `deploy-pipeline`: Test → Build → Deploy → Verify
- CLI commands: `run`, `list`, `runs`, `status`, `test`
- Run history tracking in JSON state files
- 10-minute timeout per step (configurable)
- Comprehensive documentation (README.md, SKILL.md)
- MIT license
- Package.json for npm compatibility

### Architecture
- Pure Node.js 22 (no external dependencies)
- WebSocket connection to OpenClaw gateway
- Challenge-response authentication
- Isolated agent sessions per step
- Variable extraction from step output (KEY: value format)
- Automatic worker agent creation with minimal brain files
- JSON state persistence to `~/.openclaw/workspace/.soulflow/runs/`

### Requirements
- OpenClaw 2026.2.x or later
- Node.js 22+ (native WebSocket support)
- Gateway with token authentication configured
