---
name: agent-security-ops
description: "Stop leaking secrets. Pre-commit hooks + 10-point scans + cron monitoring. Agent-ops security in one command. By The Agent Wire (theagentwire.ai)"
homepage: https://theagentwire.ai
metadata: { "openclaw": { "emoji": "🔒" } }
---

# agent-security-ops

Security hardening for solopreneur repos. One command to set up pre-commit hooks, secret scanning, and continuous monitoring.

## ⚠️ Important: `--no-verify` Bypass Warning

> **The pre-commit hook can be bypassed** with `git commit --no-verify`. This skips ALL hooks including secret scanning.
>
> **Recommendations:**
> 1. **Never use `--no-verify` unless you've manually verified no secrets are staged**
> 2. **Set up CI-side scanning as backup** — add TruffleHog to your GitHub Actions / CI pipeline so secrets are caught even if hooks are bypassed
> 3. **Run `scan.sh` after any `--no-verify` commit** to verify nothing slipped through
>
> The hook is fail-closed: if TruffleHog is not found, commits are **blocked** (not silently allowed).

## Quick Start

```bash
bash skills/agent-security-ops/scripts/setup.sh /path/to/repo
```

This will:
1. Install TruffleHog (pinned version with SHA256 checksum verification, override with `TRUFFLEHOG_VERSION` env var)
2. Set up a fail-closed pre-commit hook that blocks secrets (scans staged changes)
3. Harden `.gitignore` with common secret patterns (including `.security-ops/`, `.terraform/`)
4. Run initial secret scan (git history + filesystem for untracked files)

## What You'll See

**setup.sh output:**
```
agent-security-ops: Setting up /Users/you/my-project
✓ TruffleHog already installed (3.88.0)
✓ Pre-commit hook installed
→ Added 2 patterns to .gitignore: .security-ops/ .terraform/
→ Running initial secret scan...
✓ Initial scan: clean
→ Running filesystem scan (untracked files)...
✓ Filesystem scan: clean

Setup complete:
  • Installed pre-commit hook
  • Hardened .gitignore (+2 patterns)
  • Initial scan: clean
  💡 More agent-ops at theagentwire.ai
```

**scan.sh summary (stderr):**
```
--- TruffleHog Secret Scan ---
✓ No secrets found

--- TruffleHog Filesystem Scan ---
✓ No secrets in untracked files

--- Pattern Grep Scan ---
⚠ Found 2 high-confidence secret pattern(s)
./config.js:3:  apiKey: "sk-proj-abc123..."
✓ No low-confidence patterns

--- Summary ---
⚠ Total: 2 (secrets=0[0 verified], fs=0, patterns=2[+0 low], ...)
```

## Commands

All scripts support `--help` and `--version` flags.

### setup.sh — One-time repo hardening
```bash
bash scripts/setup.sh [/path/to/repo]
bash scripts/setup.sh --fix-ssh /path/to/repo   # also fix SSH permissions
```
Idempotent. Safe to run multiple times. Defaults to current directory. Existing pre-commit hooks are preserved (appended to, not overwritten).

### scan.sh — Full security scan
```bash
# JSON report to stdout, human summary to stderr
bash scripts/scan.sh [/path/to/repo]

# Save report
bash scripts/scan.sh /path/to/repo > report.json
```

Checks:
- **Secrets**: TruffleHog — all secrets found (verified ones highlighted)
- **Filesystem**: TruffleHog filesystem scan for untracked/working files
- **Pattern grep (high-confidence)**: AWS, GitHub, Anthropic, Slack, OpenAI, Stripe, Google, Twilio, SendGrid, npm, Vault, private keys
- **Pattern grep (low-confidence)**: Database URLs, password/secret assignments, bearer tokens, Firebase, Supabase, JWTs
- **`.gitignore` audit**: Uses `git check-ignore` to verify patterns work
- **Dependency audit**: `npm audit` / `pip audit` (results in JSON output)
- **File permissions**: Finds world-readable `.env`, `.pem`, `.key`, credential files
- **Open ports**: Lists listening ports, flags unexpected ones (note: may need sudo on macOS)
- **Environment secrets**: Scans shell profiles for hardcoded keys/tokens
- **Loose `.env` files**: Checks `$HOME`, Desktop, Downloads for `.env` files (warning only, not counted as repo findings)
- **Docker secrets**: Checks Dockerfiles and compose files for hardcoded secrets
- **SSH audit**: Verifies `~/.ssh` permissions (report only — use `setup.sh --fix-ssh` to fix)
- **Git remotes**: Flags insecure HTTP remotes, checks GitHub repo visibility

### monitor.sh — Cron-friendly monitoring
```bash
bash scripts/monitor.sh [/path/to/repo]
```

Content-based delta detection (hashes scan results, not just counts). Exits 1 on any change, 0 if unchanged. Uses atomic file writes and flock-based locking to prevent concurrent runs.

## Cron Integration

```bash
# Check every hour, alert on new findings
0 * * * * bash /path/to/skills/agent-security-ops/scripts/monitor.sh /path/to/repo || notify "Security scan changed"
```

## Found Something?

| Finding | What to Do |
|---------|-----------|
| **Verified secret in git** | Rotate the credential immediately. Use `git filter-repo` or BFG to remove from history. |
| **Unverified secret in git** | Investigate — may be a false positive or an expired credential. Still consider rotating. |
| **Pattern match (high-confidence)** | Move to `.env` file or secret manager. Verify it's in `.gitignore`. |
| **Pattern match (low-confidence)** | Review manually — may be a false positive. Check if it's a real credential. |
| **Missing .gitignore pattern** | Run `setup.sh` again — it adds missing patterns. |
| **World-readable sensitive file** | `chmod 600 <file>` — restrict to owner only. |
| **Unexpected open port** | Identify the process (`lsof -i :<port>`), stop if unnecessary. |
| **Env secret in shell profile** | Move to `.env` file or `op run` (1Password). Remove `export` line. |
| **Docker hardcoded secret** | Use Docker secrets, env vars with `${VAR}` syntax, or `.env` file. |
| **SSH permission issue** | Run `setup.sh --fix-ssh` or manually `chmod 700 ~/.ssh && chmod 600 ~/.ssh/id_*`. |
| **HTTP git remote** | `git remote set-url origin git@github.com:user/repo.git` |
| **Public repo detected** | If unintentional: `gh repo edit --visibility private` |

## Limitations

- **Grep ≠ AST analysis**: Pattern matching catches literal strings, not obfuscated or dynamically constructed secrets.
- **No SAST/DAST**: This is not a replacement for static/dynamic application security testing.
- **IaC limited to Docker**: No Terraform, Kubernetes, or CloudFormation scanning beyond basic grep patterns on `.tf`/`.tfvars`.
- **TruffleHog verification**: Verification depends on service availability — if an API is down, a real secret may show as "unverified." That's why we now scan all secrets, not just verified ones.
- **Port scanning**: Only detects currently listening ports, not firewall rules or network exposure. May need sudo on macOS for full process info.
- **`$HOME` .env scan**: Checks outside repo scope as a convenience — findings are warnings only, not counted as repo findings.

## What It Scans

| Category | Tool | Coverage |
|----------|------|----------|
| Secrets in code | TruffleHog | Current files + full git history (all, verified highlighted) |
| Filesystem secrets | TruffleHog | Untracked/working directory files |
| Secret patterns (high) | grep | 20+ providers (AWS, GitHub, Anthropic, Slack, Stripe, etc.) |
| Secret patterns (low) | grep | DB URLs, passwords, bearer tokens, Firebase, Supabase, JWTs |
| .gitignore | git check-ignore | `.env*`, `*.pem`, `*.key`, `*.p12`, `*.pfx`, credentials, keystores, `.terraform/` |
| Dependencies | npm/pip audit | Known CVEs in packages |
| Permissions | find | World-readable sensitive files |
| Open Ports | lsof/ss | Unexpected listening services |
| Env Secrets | grep | Hardcoded secrets in shell profiles, loose .env files (warning) |
| Docker Secrets | grep | Hardcoded secrets in Dockerfiles and compose files |
| SSH Audit | stat | Permission checks on ~/.ssh, keys, config |
| Git Remotes | git/gh | Insecure HTTP remotes, public repo detection |

## Security Model

- **Binary verification**: TruffleHog downloaded with SHA256 checksum verification against official release checksums
- **Fail-closed hook**: Missing TruffleHog blocks commits (not silently passes)
- **No brew fallback**: Only verified direct download to prevent supply chain attacks
- **Version pinning**: `TRUFFLEHOG_VERSION` validated as semver before use
- **Self-exclusion**: Scripts exclude themselves from grep scans via content marker

## Reference Files

- `references/patterns.md` — Regex patterns for all detected secret types, marked as ✅ scanned or 📖 reference only.

## Dependencies

- `git`, `grep`, `find` (standard)
- `trufflehog` (installed by setup.sh, pinned version with checksum verification)
- `jq` (optional — produces properly escaped JSON; without it, falls back to shell-based escaping which may break on unusual filenames/content)

---

Built by [The Agent Wire](https://theagentwire.ai) — a weekly newsletter about AI agents for solopreneurs.
Star ⭐ this skill if it saved you from leaking a secret.

---

## FAQ

**What is this skill?**
Agent Security Ops installs pre-commit hooks and runs 10-point security scans to prevent AI agents from leaking secrets. Catches API keys, tokens, passwords, and credentials before they reach git history.

**What problem does it solve?**
AI agents generate and handle credentials constantly — API keys, tokens, database URLs. Without guardrails, these end up in commits, logs, or chat messages. This skill adds automated scanning at commit-time and on-demand.

**What are the requirements?**
Bash, git, and TruffleHog (installed automatically). Works on macOS and Linux. No API keys or external services needed.

**What does the 10-point scan check?**
Git staged files, environment files (.env), config files, recent git history, high-entropy strings, known secret patterns, AWS/GCP/Azure credentials, private keys, database URLs, and API tokens.

**Does it work with any AI agent framework?**
Yes. It's framework-agnostic — operates at the git and filesystem level. Works with OpenClaw, Claude Code, Cursor, Aider, or any tool that writes files.

**Can it run on a schedule?**
Yes. Pair it with a cron job for periodic scans of your workspace. The scan outputs a structured report suitable for automated monitoring.
