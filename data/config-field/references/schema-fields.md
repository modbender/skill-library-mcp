# OpenClaw Configuration Schema Fields

Auto-generated from official Zod schema.

## Legend

- **Field**: Configuration field path
- **Type**: Data type
- **Optional**: Whether field is optional (✓) or required (✗)

## Field Reference

| Field | Type | Optional |
|-------|------|----------|
| `$schema` | string | ✓ |
| `agents` | object | ✓ |
| `agents.defaults` | object | ✓ |
| `agents.defaults.contextTokens` | number | ✓ |
| `agents.defaults.elevatedDefault` | enum (off, on, ask, full) | ✓ |
| `agents.defaults.imageMaxDimensionPx` | number | ✓ |
| `agents.defaults.imageModel` | object | ✓ |
| `agents.defaults.imageModel.fallbacks` | array | ✓ |
| `agents.defaults.imageModel.primary` | string | ✓ |
| `agents.defaults.mediaMaxMb` | number | ✓ |
| `agents.defaults.memorySearch` | object | ✓ |
| `agents.defaults.memorySearch.enabled` | boolean | ✓ |
| `agents.defaults.memorySearch.provider` | enum (openai, local, gemini, voyage, mistral) | ✓ |
| `agents.defaults.model` | object | ✓ |
| `agents.defaults.model.fallbacks` | array | ✓ |
| `agents.defaults.model.primary` | string | ✓ |
| `agents.defaults.models` | object | ✓ |
| `agents.defaults.repoRoot` | string | ✓ |
| `agents.defaults.sandbox` | object | ✓ |
| `agents.defaults.sandbox.mode` | enum (off, non-main, all) | ✓ |
| `agents.defaults.sandbox.workspaceAccess` | enum (none, ro, rw) | ✓ |
| `agents.defaults.skipBootstrap` | boolean | ✓ |
| `agents.defaults.thinkingDefault` | enum (off, minimal, low, medium, high, ...) | ✓ |
| `agents.defaults.timeFormat` | enum (auto, 12, 24) | ✓ |
| `agents.defaults.timeoutSeconds` | number | ✓ |
| `agents.defaults.userTimezone` | string | ✓ |
| `agents.defaults.verboseDefault` | enum (off, on, full) | ✓ |
| `agents.defaults.workspace` | string | ✓ |
| `agents.list` | array | ✓ |
| `agents.list.default` | boolean | ✓ |
| `agents.list.id` | string | ✗ |
| `agents.list.model` | string | ✓ |
| `agents.list.name` | string | ✓ |
| `agents.list.skills` | array | ✓ |
| `agents.list.workspace` | string | ✓ |
| `bindings` | array | ✓ |
| `browser` | object | ✓ |
| `browser.defaultProfile` | string | ✓ |
| `browser.enabled` | boolean | ✓ |
| `browser.headless` | boolean | ✓ |
| `channels` | object | ✓ |
| `channels.discord` | object | ✓ |
| `channels.discord.dmPolicy` | enum (allowlist, open, disabled, pairing) | ✓ |
| `channels.discord.enabled` | boolean | ✓ |
| `channels.discord.groupPolicy` | enum (allowlist, open, disabled) | ✓ |
| `channels.discord.historyLimit` | number | ✓ |
| `channels.discord.token` | string | ✓ |
| `channels.imessage` | object | ✓ |
| `channels.irc` | object | ✓ |
| `channels.signal` | object | ✓ |
| `channels.slack` | object | ✓ |
| `channels.slack.appToken` | string | ✓ |
| `channels.slack.botToken` | string | ✓ |
| `channels.slack.enabled` | boolean | ✓ |
| `channels.slack.mode` | enum (socket, http) | ✓ |
| `channels.slack.signingSecret` | string | ✓ |
| `channels.telegram` | object | ✓ |
| `channels.telegram.allowFrom` | array | ✓ |
| `channels.telegram.botToken` | string | ✓ |
| `channels.telegram.defaultTo` | string | ✓ |
| `channels.telegram.dmPolicy` | enum (allowlist, open, disabled, pairing) | ✓ |
| `channels.telegram.enabled` | boolean | ✓ |
| `channels.telegram.groupPolicy` | enum (allowlist, open, disabled) | ✓ |
| `channels.telegram.historyLimit` | number | ✓ |
| `channels.telegram.tokenFile` | string | ✓ |
| `channels.whatsapp` | object | ✓ |
| `commands` | object | ✓ |
| `commands.config` | boolean | ✓ |
| `commands.debug` | boolean | ✓ |
| `commands.native` | boolean | ✓ |
| `commands.nativeSkills` | boolean | ✓ |
| `commands.restart` | boolean | ✓ |
| `cron` | object | ✓ |
| `cron.enabled` | boolean | ✓ |
| `diagnostics` | object | ✓ |
| `diagnostics.enabled` | boolean | ✓ |
| `diagnostics.flags` | array | ✓ |
| `env` | object | ✓ |
| `env.shellEnv` | object | ✓ |
| `env.shellEnv.enabled` | boolean | ✓ |
| `env.shellEnv.timeoutMs` | number | ✓ |
| `env.vars` | object | ✓ |
| `hooks` | object | ✓ |
| `hooks.enabled` | boolean | ✓ |
| `logging` | object | ✓ |
| `logging.consoleLevel` | enum (silent, fatal, error, warn, info, ...) | ✓ |
| `logging.consoleStyle` | enum (pretty, compact, json) | ✓ |
| `logging.file` | string | ✓ |
| `logging.level` | enum (silent, fatal, error, warn, info, ...) | ✓ |
| `logging.maxFileBytes` | number | ✓ |
| `logging.redactPatterns` | array | ✓ |
| `logging.redactSensitive` | enum (off, tools) | ✓ |
| `meta` | object | ✓ |
| `meta.lastTouchedAt` | string | ✓ |
| `meta.lastTouchedVersion` | string | ✓ |
| `models` | object | ✓ |
| `models.mode` | enum (merge, replace) | ✓ |
| `models.providers` | object | ✓ |
| `session` | object | ✓ |
| `session.idleMinutes` | number | ✓ |
| `session.scope` | enum (per-sender, global) | ✓ |
| `tools` | object | ✓ |
| `tools.allow` | array | ✓ |
| `tools.alsoAllow` | array | ✓ |
| `tools.deny` | array | ✓ |
| `tools.exec` | object | ✓ |
| `tools.exec.ask` | enum (off, on-miss, always) | ✓ |
| `tools.exec.host` | enum (sandbox, gateway, node) | ✓ |
| `tools.exec.security` | enum (allowlist, deny, full) | ✓ |
| `tools.exec.timeoutSec` | number | ✓ |
| `tools.fs` | object | ✓ |
| `tools.fs.workspaceOnly` | boolean | ✓ |
| `tools.links` | object | ✓ |
| `tools.media` | object | ✓ |
| `tools.profile` | enum (minimal, coding, messaging, full) | ✓ |
| `tools.sessions` | object | ✓ |
| `tools.web` | object | ✓ |
| `tools.web.fetch` | object | ✓ |
| `tools.web.fetch.enabled` | boolean | ✓ |
| `tools.web.fetch.maxChars` | number | ✓ |
| `tools.web.fetch.timeoutSeconds` | number | ✓ |
| `tools.web.search` | object | ✓ |
| `tools.web.search.apiKey` | string | ✓ |
| `tools.web.search.enabled` | boolean | ✓ |
| `tools.web.search.maxResults` | number | ✓ |
| `tools.web.search.provider` | enum (brave, perplexity, grok) | ✓ |
| `ui` | object | ✓ |
| `ui.seamColor` | string | ✓ |
| `update` | object | ✓ |
| `update.channel` | enum (stable, beta, dev) | ✓ |
| `update.checkOnStart` | boolean | ✓ |
| `web` | object | ✓ |
| `web.enabled` | boolean | ✓ |
| `wizard` | object | ✓ |
| `wizard.lastRunAt` | string | ✓ |
| `wizard.lastRunVersion` | string | ✓ |

## Usage Examples

### Validate a field:
```bash
python3 scripts/validate_field.py agents.defaults.model.primary
```

### Validate config file:
```bash
python3 scripts/validate_config.py ~/.config/openclaw/openclaw.json
```

---

*Generated automatically from OpenClaw Zod Schema*