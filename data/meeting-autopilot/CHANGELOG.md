# Changelog

## 0.1.1 (2026-02-16)

### Added
- Discord v2 delivery guidance in `SKILL.md` for OpenClaw v2026.2.14+:
  - Compact first response for meeting outcomes
  - Component-style quick actions
  - Numbered fallback when components are unavailable
- `discord` and `discord-v2` tags in skill metadata

### Changed
- Metadata normalization: `author` set to `CacheForge`.
- README: added "OpenClaw Discord v2 Ready" compatibility section.
- Script and metadata versions bumped to `0.1.1`.

### Fixed
- Added URL scheme validation for custom `ANTHROPIC_API_URL` / `OPENAI_API_URL` (http/https only) before API calls.

## 0.1.0 (2026-02-15)

### Added
- Initial release
- **Transcript parsing:** VTT, SRT, and plain text format support with auto-detection
- **Multi-pass LLM extraction:** decisions, action items, open questions, parking lot, key points
- **Follow-up email drafts:** professional, ready-to-send email generation
- **Ticket/issue drafts:** Jira/Linear/GitHub-ready descriptions for each action item
- **Beautiful Markdown report:** screenshot-ready output with tables, emoji indicators, and structured sections
- **Cross-meeting history:** extracted items stored locally at `~/.meeting-autopilot/history/` as JSON
- **Dual API support:** works with Anthropic (Claude) or OpenAI (GPT-4o)
- **Custom API URLs:** `ANTHROPIC_API_URL` and `OPENAI_API_URL` env vars for proxies/self-hosted
- **CLI flags:** `--title`, `--format`, `--output`, `--no-history`
- **Safety-first:** all JSON via `jq --arg`, no eval, no injection patterns, stdin-based Python parsing
- Security model documented in SECURITY.md
- Test plan with sample transcript in TESTING.md
