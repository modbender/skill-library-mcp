---
name: openclaw-guardian
description: >
  A security layer plugin for OpenClaw that intercepts dangerous tool calls
  (exec, write, edit) through two-tier regex blacklist rules and LLM-based
  intent verification. Critical operations require 3/3 unanimous LLM votes,
  warning-level operations require 1 LLM confirmation. 99% of normal
  operations pass instantly with zero overhead. Includes bypass/pipe-attack
  detection, path canonicalization, SHA-256 hash-chain audit logging, and
  auto-discovers a cheap model from your existing provider config.
---

# OpenClaw Guardian

> The missing safety layer for AI agents.

## Why?

OpenClaw gives agents direct access to shell, files, email, browser, and more.
99% of that is harmless. Guardian catches the 1% that isn't — without slowing
down the rest.

## How It Works

```
Tool Call → Blacklist Matcher (regex rules, 0ms)
              ↓
   No match     → Pass instantly (99% of calls)
   Warning hit  → 1 LLM vote ("did the user ask for this?")
   Critical hit → 3 LLM votes (all must confirm user intent)
```

### Two Blacklist Levels

| Level | LLM Votes | Latency | Examples |
|-------|-----------|---------|---------|
| No match | 0 | ~0ms | Reading files, git, normal ops |
| Warning | 1 | ~1-2s | `rm -rf /tmp/cache`, `chmod 777`, `sudo apt` |
| Critical | 3 (unanimous) | ~2-4s | `rm -rf ~/`, `mkfs`, `dd of=/dev/`, `shutdown` |

### What Gets Checked

Only three tool types are inspected:

- `exec` → command string matched against exec blacklist
- `write` / `edit` → file path canonicalized and matched against path blacklist
- Everything else passes through instantly

### LLM Intent Verification

When a blacklist rule matches, Guardian asks a lightweight LLM: "Did the user
explicitly request this?" It reads recent conversation context to prevent
false positives.

- Warning: 1 LLM call. Confirmed → proceed.
- Critical: 3 parallel LLM calls. All 3 must confirm. Any "no" → block.

Auto-discovers a cheap/fast model from your existing OpenClaw provider config
(prefers Haiku). No separate API key needed.

### LLM Fallback

- Critical + LLM down → blocked (fail-safe)
- Warning + LLM down → asks user for manual confirmation

## Blacklist Rules

### Critical (exec)
- `rm -rf` on system paths (excludes `/tmp/` and workspace)
- `mkfs`, `dd` to block devices, redirects to `/dev/sd*`
- Writes to `/etc/passwd`, `/etc/shadow`, `/etc/sudoers`
- `shutdown`, `reboot`, disable SSH
- Bypass: `eval`, absolute-path rm, interpreter-based (`python -c`, `node -e`)
- Pipe attacks: `curl | sh`, `wget | bash`, `base64 -d | sh`
- Chain attacks: download + `chmod +x` + execute

### Warning (exec)
- `rm -rf` on safe paths, `sudo`, `chmod 777`, `chown root`
- Package install/remove, service management
- Crontab mods, SSH/SCP, Docker ops, `kill`/`killall`

### Path Rules (write/edit)
- Critical: system auth files, SSH keys, systemd units
- Warning: dotfiles, `/etc/` configs, `.env` files, `authorized_keys`

## Audit Log

Every blacklist hit logged to `~/.openclaw/guardian-audit.jsonl` with SHA-256
hash chain — tamper-evident, each entry covers full content + previous hash.

## Installation

```bash
openclaw plugins install openclaw-guardian
```

Or manually:

```bash
cd ~/.openclaw/workspace
git clone https://github.com/fatcatMaoFei/openclaw-guardian.git
```

## Token Cost

| Scenario | % of Ops | Extra Cost |
|----------|----------|------------|
| No match | ~99% | 0 |
| Warning | ~0.5-1% | ~500 tokens |
| Critical | <0.5% | ~1500 tokens |

Prefers cheap models (Haiku, GPT-4o-mini, Gemini Flash).

## File Structure

```
extensions/guardian/
├── index.ts                # Entry — registers before_tool_call hook
├── src/
│   ├── blacklist.ts        # Two-tier regex rules (critical/warning)
│   ├── llm-voter.ts        # LLM intent verification
│   └── audit-log.ts        # SHA-256 hash-chain audit logger
├── test/
│   └── blacklist.test.ts   # Blacklist rule tests
├── openclaw.plugin.json    # Plugin manifest
└── default-policies.json   # Enable/disable toggle
```

## License

MIT
