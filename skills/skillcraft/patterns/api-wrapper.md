# Web API Wrapper Pattern

Wrap a web API for use through OpenClaw.

## Execution Methods

| Method | When |
|--------|------|
| `web_fetch` | Simple GET, public endpoints, no auth |
| `exec` + `curl` | Custom headers, POST/PUT/DELETE, auth |
| Script | Repeated calls, response parsing, caching |

## OpenClaw-Specific Concerns

### Polling via Cron
For periodic API checks, use `cron` tool. Document: what endpoint, what constitutes "new" (vs stored state), notification format.

### State & Caching
Store in `{baseDir}/state.json`:
- Incremental polling (last-seen ID/timestamp)
- Response cache with expiry
- Rate limit tracking

### Heavy Processing
Use `sessions_spawn` for large responses or analysis. Include API key env var name in the task context.

### Secrets
**Always environment variables.** Document the requirement in SKILL.md setup section. Never hardcode. Common patterns: env vars (most portable), macOS Keychain, `~/.config/`, 1Password CLI.

## Checklist

- [ ] Execution method chosen (web_fetch / curl / script)
- [ ] Cron polling documented (if periodic)
- [ ] State/cache uses `{baseDir}/` or `<workspace>/`
- [ ] Heavy operations spawn subagents
- [ ] Secrets via environment, documented in setup
- [ ] Output formatting considers channel constraints
