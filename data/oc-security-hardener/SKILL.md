---
name: security-hardener
description: Audit and harden OpenClaw configuration for security. Scans openclaw.json for vulnerabilities, exposed credentials, insecure gateway settings, overly permissive exec rules, and missing security best practices. Use when asked to audit security, harden configuration, check for vulnerabilities, or secure an OpenClaw deployment.
---

# Security Hardener

Audit your OpenClaw configuration and apply security best practices automatically.

## Quick Start

```bash
# Full security audit (read-only, no changes)
python scripts/hardener.py audit

# Audit a specific config file
python scripts/hardener.py audit --config /path/to/openclaw.json

# Audit with JSON output
python scripts/hardener.py audit -f json

# Auto-fix issues (creates backup first)
python scripts/hardener.py fix

# Fix specific issues only
python scripts/hardener.py fix --only gateway,permissions

# Scan for exposed credentials in config
python scripts/hardener.py scan-secrets

# Generate a security report
python scripts/hardener.py report -o security-report.md

# Check file permissions
python scripts/hardener.py check-perms
```

## Commands

| Command | Args | Description |
|---------|------|-------------|
| `audit` | `[--config PATH] [-f FORMAT]` | Full security audit (read-only) |
| `fix` | `[--config PATH] [--only CHECKS]` | Auto-fix issues (with backup) |
| `scan-secrets` | `[--config PATH]` | Scan for exposed API keys/tokens |
| `report` | `[-o FILE]` | Generate detailed security report |
| `check-perms` | `[--config-dir PATH]` | Check file permissions |

## Security Checks

| Check | Severity | Description |
|-------|----------|-------------|
| `gateway-bind` | CRITICAL | Gateway not bound to loopback |
| `exposed-keys` | CRITICAL | API keys in config instead of .env |
| `insecure-auth` | HIGH | `allowInsecureAuth` or `dangerouslyDisableDeviceAuth` enabled |
| `exec-sandbox` | HIGH | exec sandbox mode not set to restricted |
| `file-perms` | HIGH | Config files readable by others (not 600) |
| `agent-allow-all` | MEDIUM | `agentToAgent.allow: ["*"]` is overly permissive |
| `no-heartbeat` | MEDIUM | No heartbeat configured (can't detect outages) |
| `no-session-reset` | MEDIUM | No session reset policy (memory leak risk) |
| `no-pruning` | LOW | No context pruning (cost and performance impact) |
| `no-memory-flush` | LOW | Memory flush disabled (context loss on pruning) |

## Scoring

The audit produces a security score from 0-100:
- **90-100**: Excellent — production-ready
- **70-89**: Good — minor improvements recommended
- **50-69**: Fair — several issues to address
- **0-49**: Poor — critical issues require immediate attention

## Example Output

```
╔══════════════════════════════════════════════════╗
║  OPENCLAW SECURITY AUDIT                         ║
╠══════════════════════════════════════════════════╣
║  Score: 75/100 (Good)                            ║
║                                                  ║
║  ✅ Gateway bound to loopback                    ║
║  ✅ No exposed API keys in config                ║
║  ⚠️  exec sandbox mode: unrestricted             ║
║  ⚠️  agentToAgent allow: * (too permissive)      ║
║  ❌ File permissions too open (644 → should be 600) ║
║  ✅ Heartbeat configured                         ║
║  ✅ Session reset policy active                   ║
║  ⚠️  No context pruning configured               ║
╚══════════════════════════════════════════════════╝
```
