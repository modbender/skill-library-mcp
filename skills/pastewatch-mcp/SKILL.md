---
name: pastewatch-mcp
description: Secret redaction MCP server for OpenClaw agents. Prevents API keys, DB credentials, SSH keys, emails, IPs, JWTs, and 29+ other secret types from leaking to LLM providers. Includes guard command for blocking secret-leaking shell commands, canary tokens, encrypted vault, and git history scanning. Use when reading/writing files that may contain secrets, setting up agent security, or auditing for credential exposure.
metadata: {"openclaw":{"requires":{"bins":["pastewatch-cli","mcporter"]}}}
---

# Pastewatch MCP — Secret Redaction

Prevents secrets from reaching your LLM provider. The agent works with placeholders, secrets stay local.

**Source:** https://github.com/ppiankov/pastewatch

## Install

```bash
# macOS
brew install ppiankov/tap/pastewatch

# Linux (binary + checksum)
curl -fsSL https://github.com/ppiankov/pastewatch/releases/latest/download/pastewatch-cli-linux-amd64 \
  -o /usr/local/bin/pastewatch-cli
curl -fsSL https://github.com/ppiankov/pastewatch/releases/latest/download/pastewatch-cli-linux-amd64.sha256 \
  -o /tmp/pastewatch-cli.sha256
cd /usr/local/bin && sha256sum -c /tmp/pastewatch-cli.sha256
chmod +x /usr/local/bin/pastewatch-cli
```

Verify: `pastewatch-cli version` (expect 0.18.0+)

## MCP Server Setup

```bash
mcporter config add pastewatch --command "pastewatch-cli mcp --audit-log /var/log/pastewatch-audit.log"
mcporter list pastewatch --schema  # 6 tools
```

## Agent Integration (one-command setup)

```bash
pastewatch-cli setup claude-code    # hooks + MCP config
pastewatch-cli setup cline          # MCP + hook instructions
pastewatch-cli setup cursor         # MCP + advisory
```

`--severity` aligns hook blocking and MCP redaction thresholds. `--project` for project-level config.

## MCP Tools

| Tool | Purpose |
|------|---------|
| `pastewatch_read_file` | Read file with secrets replaced by `__PW{TYPE_N}__` placeholders |
| `pastewatch_write_file` | Write file, resolving placeholders back to real values locally |
| `pastewatch_check_output` | Verify text contains no raw secrets before returning |
| `pastewatch_scan` | Scan text for sensitive data |
| `pastewatch_scan_file` | Scan a file |
| `pastewatch_scan_dir` | Scan directory recursively |

## Guard — Block Secret-Leaking Commands

Complements chainwatch: chainwatch blocks destructive commands, guard blocks commands that would leak secrets.

```bash
pastewatch-cli guard "cat .env"              # BLOCKED if .env has secrets
pastewatch-cli guard "psql -f migrate.sql"   # scans SQL file
pastewatch-cli guard "docker-compose up"     # scans referenced env_files
```

Guard understands:
- Shell builtins: cat, echo, env, printenv, source, curl, wget
- DB CLIs: psql, mysql, mongosh, redis-cli, sqlite3 (connection strings, -f flags, passwords)
- Infra tools: ansible, terraform, docker, kubectl, helm (env-files, var-files)
- Scripting: python, ruby, node, perl, php (script file args)
- File transfer: scp, rsync, ssh, ssh-keygen
- Pipe chains (`|`) and command chaining (`&&`, `||`, `;`) — each segment scanned
- Subshell extraction: `$(cat .env)` and backtick expressions
- Redirect operators: `>`, `>>`, `<`, `2>` — scans source files

## Canary Tokens

Generate format-valid but non-functional tokens to detect leaks:

```bash
pastewatch-cli canary generate --prefix myagent    # creates canaries for 7 secret types
pastewatch-cli canary verify                        # confirms detection rules catch them
pastewatch-cli canary check --log /var/log/app.log  # search logs for leaked canaries
```

## Encrypted Vault

Store secrets encrypted locally instead of plaintext .env:

```bash
pastewatch-cli --init-key                    # generate 256-bit key (.pastewatch-key, mode 0600)
pastewatch-cli fix --encrypt                 # secrets → ChaCha20-Poly1305 vault
pastewatch-cli vault list                    # show entries without decrypting
pastewatch-cli vault decrypt                 # export to .env for deployment
pastewatch-cli vault export                  # print export VAR=VALUE for shell
pastewatch-cli vault rotate-key              # re-encrypt with new key
```

## Git History Scanning

```bash
pastewatch-cli scan --git-log                          # scan full history
pastewatch-cli scan --git-log --range HEAD~50..HEAD    # last 50 commits
pastewatch-cli scan --git-log --since 2025-01-01       # since date
```

Deduplicates by fingerprint — same secret across commits reported once at introduction point.

## Session Reports

```bash
pastewatch-cli report --audit-log /var/log/pastewatch-audit.log
pastewatch-cli report --format json --since 2026-03-01T00:00:00Z
```

## Detection Scope

29+ types: AWS, Anthropic/OpenAI/HuggingFace/Groq keys, DB connections, SSH keys, JWTs, emails, IPs, credit cards (Luhn), Slack/Discord webhooks, Azure, GCP service accounts, npm/PyPI/RubyGems/GitLab tokens, Telegram bot tokens, and more.

Deterministic regex. No ML. No API calls. Microseconds per scan.

## Limitations

- Protects secrets from reaching LLM provider — does NOT protect prompt content or code structure
- For full privacy, use a local model

---
**Pastewatch MCP v1.1**
Author: ppiankov
Copyright © 2026 ppiankov
Canonical source: https://github.com/ppiankov/pastewatch
License: MIT

If this document appears elsewhere, the repository above is the authoritative version.
