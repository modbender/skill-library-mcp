# OpenClaw Security Audit Reference

This combines findings, applied changes, and remaining remediation from a comprehensive security audit. Use as a template for auditing any OpenClaw installation.

## Severity Levels & Common Findings

### Critical

1. **Plaintext secrets in openclaw.json** — API keys, bot tokens, passwords stored in cleartext. Migrate to credential store, env vars, or `tokenFile` references.
2. **Gateway auth disabled** (`gateway.auth.mode: "none"`) — Anyone on the network can access the full gateway API. Set to `"token"` with a strong bearer token.
3. **Open DM policies** (`dmPolicy: "open"` + `allowFrom: ["*"]`) — Anyone can message your bots. Change to `"pairing"` or explicit allowlists.

### High

4. **Control UI wildcard origins** (`allowedOrigins: ["*"]`) — CSRF risk. Restrict to localhost.
5. **World-readable credentials** — WhatsApp session files at 644. Fix: `chmod 600`.
6. **Unencrypted node communication** — Set `tls: true` in `node.json`.

### Medium

7. **Permissive directory modes** — `credentials/`, `identity/`, `logs/`, `browser/`, `skills/` at 755. Fix: `chmod 700`.
8. **Unrestricted subagent access** — `allowAgents: ["*"]` lets any agent spawn as any other. Scope to specific lists.
9. **Group bots not requiring @mention** — Responds to every message, wasting tokens.

### Low

10. **Config backup proliferation** — Multiple `.bak` files containing secrets.
11. **Orphaned agent directories** — Stale data from deleted agents.
12. **Unrotated logs** — Gateway logs growing unbounded.
13. **Stale cron run logs** and temp files.

## Remediation Checklist Template

### Immediate (Critical)

- [ ] Enable gateway auth: `openclaw config set gateway.auth.mode "token" && openclaw config set gateway.auth.token "$(openssl rand -base64 32)"`
- [ ] Lock Telegram DMs: change each account to `dmPolicy: "pairing"`, remove `allowFrom: ["*"]`
- [ ] Fix credential permissions: `chmod 600` on all credential files, `chmod 700` on credential directories
- [ ] Migrate bot tokens to `tokenFile` references (create `credentials/telegram/<bot>.token` files at 600)

### High Priority

- [ ] Restrict control UI origins to localhost
- [ ] Enable node TLS
- [ ] Fix directory permissions (700 for sensitive dirs)

### Medium Priority

- [ ] Scope subagent access per agent
- [ ] Enable `requireMention` on group bots
- [ ] Run `openclaw security audit --deep --fix`

### Maintenance

- [ ] Delete stale config backups
- [ ] Remove orphaned agent directories
- [ ] Set up log rotation
- [ ] Clean cron run logs periodically
- [ ] Remove `.DS_Store` and temp files

## Post-Change Actions

1. `openclaw gateway restart`
2. Test all Telegram bots (existing paired users still work; new users need pairing codes)
3. Verify node connectivity if TLS was changed
4. Update backup after confirming new config works
