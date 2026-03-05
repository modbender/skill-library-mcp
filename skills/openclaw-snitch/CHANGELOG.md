# Changelog

## 1.0.0 — 2026-02-25

- Initial release
- Configurable blocklist with `clawhub`/`clawdhub` as defaults
- `before_tool_call` hard block with Telegram broadcast to all `allowFrom` IDs
- `agent:bootstrap` hook for security directive injection
- `message:received` hook for incoming message warnings
- `SNITCH_BLOCKLIST` env var support for hook customization
