# Changelog

## 1.0.0 (2026-02-24)

### Initial Release

- Claude Code hooks for automatic agent lifecycle reporting
- 5 hook events: `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `Stop`
- 21-agent hierarchy with full subagent_type mapping
- Non-blocking fire-and-forget HTTP reporting (< 50ms overhead)
- One-command setup script with hook installer
- Bootstrap script for pre-populating agent organogram
- 3 documented usage examples (basic, multi-agent, error handling)
- Graceful degradation: silent exit if env vars missing or API unreachable
