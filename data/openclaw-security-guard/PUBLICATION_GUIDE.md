# Publication Guide -- What's Done & What's Left

## DONE (automated)

### 1. GitHub Discussion on openclaw/openclaw
- **URL:** https://github.com/openclaw/openclaw/discussions/15124
- **Category:** Show and tell
- **Status:** Posted

### 2. Issue on openclaw/trust
- **URL:** https://github.com/openclaw/trust/issues/5
- **Title:** Proposal: Integration with OpenClaw Security Guard for automated threat detection
- **Status:** Posted

---

## TO DO (requires your interaction)

### 3. Publish on ClawHub

The `SKILL.md` file is ready in the project root. Run these commands:

```bash
# Login (opens browser for GitHub OAuth)
npx clawhub login

# Verify login
npx clawhub whoami

# Dry run to preview
npx clawhub publish . --version 1.0.0 --dry-run

# Publish
npx clawhub publish . --version 1.0.0
```

### 4. Share on Discord

1. Join the OpenClaw Discord: https://discord.gg/qkhbAGHRBT
2. Find the `#showcase` or `#community-tools` channel
3. Post the message below:

---

**Discord message (copy-paste):**

```
🛡️ **OpenClaw Security Guard** -- CLI security scanner + live dashboard

Just released an open-source tool that audits your OpenClaw installation for security issues:

• Secrets scanning (15+ API key formats + entropy analysis)
• Config hardening (sandbox, DM policy, gateway binding)
• Prompt injection detection (50+ patterns)
• MCP server verification (allowlist-based)
• npm dependency scanning

Plus a real-time dashboard, auto-fix with backup, and pre-commit hooks.

**Zero telemetry. 100% local. MIT licensed.**

npm install -g openclaw-security-guard
openclaw-guard audit

GitHub: https://github.com/2pidata/openclaw-security-guard
Discussion: https://github.com/openclaw/openclaw/discussions/15124

Stars welcome! ⭐
```

---

## Summary of all links

| What | URL |
|---|---|
| GitHub repo | https://github.com/2pidata/openclaw-security-guard |
| GitHub Discussion | https://github.com/openclaw/openclaw/discussions/15124 |
| Trust repo issue | https://github.com/openclaw/trust/issues/5 |
| ClawHub | https://clawhub.ai (publish with `npx clawhub publish . --version 1.0.0`) |
| Discord | https://discord.gg/qkhbAGHRBT |
