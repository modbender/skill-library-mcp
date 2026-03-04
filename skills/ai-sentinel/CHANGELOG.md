# Changelog

## 1.2.0 (2026-02-10)

- Set `disableModelInvocation: true` to prevent autonomous agent invocation (skill now requires explicit user action)
- Add registry metadata checklist to README so publish form fields match SKILL.md declarations

## 1.1.0 (2026-02-10)

- Move declarations into structured metadata fields (Requires-Config, Requires-Env, Installs-Packages, Writes-Files, External-Services) so registry parsers read them
- Add Data Transmission Notice section explaining what Pro tier sends externally
- Add File Write Policy section confirming no files are written without user approval
- Add explicit consent gate when user selects Pro tier (data transmission to api.zetro.ai)
- Add explicit AskUserQuestion confirmation before every file write (openclaw.config.ts, .env, data/, .gitignore)
- Add agent instruction: never write files autonomously

## 1.0.1 (2026-02-10)

- Add declarations table (config paths, env vars, filesystem writes, npm packages)
- Add homepage, source, and package registry links to metadata
- Replace literal injection strings in test examples with benign-to-scan payloads to avoid false positive flags from security scanners

## 1.0.0 (2026-02-10)

- Initial release
- Interactive setup wizard for OpenClaw integration
- Supports Community (free, local-only) and Pro (remote API + dashboard) tiers
- Configures message, tool output, document, and skill validation middleware
- Per-channel detection threshold configuration (Pro)
- Optional SQLite audit logging setup
- Optional custom blocklist rule configuration
- Built-in test verification step with CLI commands
