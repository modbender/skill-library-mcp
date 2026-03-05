# Keychain Bridge for OpenClaw

Stop storing API keys in plaintext. Migrate your OpenClaw secrets to macOS
Keychain with one command — and never worry about credential leaks again.

## The Problem

macOS Tahoe 26.x introduced several breaking changes to keychain access that
affect OpenClaw deployments:

- **`security find-generic-password -w` hangs indefinitely** — the standard CLI
  method for reading keychain items is broken on Tahoe (exit code 36 or infinite hang)
- **Plaintext files in `~/.openclaw/secrets/`** are discoverable by any process
  with file access — and 283 ClawHub skills were found with credential exposure
- **Keychain ACLs are per-binary** — an item created by Python 3.9 can't be read
  by Python 3.14 unless both binaries are in the ACL
- **Python keyring hangs from bash LaunchAgents** — a novel finding where the
  SecurityAgent session attachment is lost in bash-to-python subprocess transitions

## The Solution

Keychain Bridge is a battle-tested skill built from a real production deployment
on a Mac Mini M4 Pro running OpenClaw 24/7 with 12+ API keys, 25 scripts, and
15 cron jobs. It provides:

- **One-command migration** from plaintext files to macOS Keychain
- **Auto-detection** of all Python versions on the system with full ACL coverage
- **Group A/B architecture** for mixed Python/bash environments
- **Plaintext leak auditor** that catches forgotten secret files
- **Diagnostic tools** for every known Tahoe keychain failure mode
- **Boot-time file bridge** for bash scripts that can't use keychain directly

## What You Get

| File | Purpose |
|------|---------|
| `SKILL.md` | Full agent instructions — your OpenClaw agent knows how to use everything |
| `scripts/migrate_secrets.py` | Batch migration with multi-Python ACL injection and verification |
| `scripts/audit_secrets.py` | Continuous plaintext leak detection and keychain health checks |
| `scripts/keychain_helper.py` | Drop-in Python module — replaces file reads with keychain lookups |
| `scripts/populate_secrets.sh` | Boot-time bridge that populates files from keychain for bash tools |
| `scripts/get_secret.py` | CLI wrapper for interactive/terminal use |

## Novel Findings Included

This skill documents several behaviors not found in Apple documentation or
existing guides:

1. **Bash subprocess SecurityAgent detachment** — Python keyring works when Python
   IS the LaunchAgent, but hangs when spawned as a subprocess from bash
2. **Per-binary Keychain ACL** — each Python binary needs its own ACL entry;
   migration tool handles this automatically
3. **Group A/B secret architecture** — a practical pattern for mixed Python/bash
   environments where Group A uses keychain directly and Group B uses boot-time
   file bridges
4. **Security CLI regression on Tahoe** — `security find-generic-password -w`
   hangs even after `security unlock-keychain` with the correct password

## Requirements

- macOS 14+ (Sonoma, Sequoia, or Tahoe)
- Python 3.9+ with `pip install keyring`
- OpenClaw v2024.2+

## Quick Start

After installing the skill, just tell your OpenClaw agent:

> "Migrate my secrets to keychain"

or

> "Audit my secrets directory for plaintext leaks"

The agent has full instructions for every operation.

## Security & Privacy

- **100% local** — no network calls, no telemetry, no data leaves your machine
- **No obfuscation** — all scripts are readable Python and bash
- **Minimal permissions** — only requires `bash` and `python3` binaries
- **No API keys needed** — operates entirely against macOS Keychain

## External Endpoints

None. This skill makes zero network requests.

## Trust Statement

All code is open for inspection. The skill operates exclusively on the local
macOS Keychain and filesystem. No credentials, telemetry, or usage data are
transmitted anywhere. Built by a developer who runs this exact setup in
production 24/7.
