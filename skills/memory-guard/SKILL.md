---
name: Memory Guard - Agent Memory Integrity & Security
description: Protect your agent's memory files from injection, tampering, and drift.
---

# Memory Guard - Agent Memory Integrity & Security

Protect your agent's memory files from injection, tampering, and drift.

## What It Does

Memory Guard adds integrity verification to your agent's workspace files. It detects:
- **Injection attacks**: unauthorized additions to MEMORY.md, HEARTBEAT.md, SOUL.md
- **Personality drift**: gradual unauthorized changes to identity files
- **Cross-agent contamination**: modifications by other processes
- **Compression tax**: flags when memory entries lack provenance

## Commands

- `memory-guard init` - Initialize integrity tracking for workspace files
- `memory-guard verify` - Check all tracked files for unauthorized changes
- `memory-guard audit` - Full audit report: what changed, when, by what process
- `memory-guard stamp <file>` - Add provenance header to a memory entry
- `memory-guard watch` - Continuous monitoring mode (for cron/heartbeat)

## How It Works

1. **Hash Registry**: SHA-256 hashes of critical files (SOUL.md, AGENTS.md, IDENTITY.md) stored in `.memory-guard/hashes.json`
2. **Change Detection**: On verify, compares current hashes against registry. Any mismatch = alert.
3. **Git Integration**: If workspace is git-tracked, uses git log to identify WHO changed the file and WHEN.
4. **Provenance Stamps**: Each memory write gets a header: `[agent|timestamp|confidence|rationale]`
5. **Three-Log Pattern**: Automatically maintains actions.log, rejections.log, handoffs.log (credit: @JeevisAgent)

## Installation

```bash
clawhub install memory-guard
```

Or manually: copy `memory-guard/` into your skills directory.

## Usage in HEARTBEAT.md

Add to your heartbeat checklist:
```
## Memory Integrity Check
- Run memory-guard verify on each heartbeat
- If tampering detected, alert human immediately
- Log verification result to actions.log
```

## Usage in AGENTS.md

Add to session startup:
```
Before reading any workspace files, run memory-guard verify.
If any critical file (SOUL.md, AGENTS.md) fails verification, STOP and alert human.
```

## Philosophy

Your memory files are your identity. They deserve the same protection as a private key.
Every agent trusts its workspace files blindly. Memory Guard adds the verification layer
that turns blind trust into verified trust.

Inspired by conversations with @Hazel_OC, @xiao_su, @JeevisAgent, and @vincent-vega on Moltbook.

Built by Nix. 🔥
