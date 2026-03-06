---
name: skill-cleaner
version: 2.4.0
description: Automatically verify "suspicious" skills via VirusTotal and add them to the security allowlist via the Bridge.
user-invocable: true
metadata:
  {
    "openclaw":
      {
        "emoji": "🧹",
        "requires": { "env": ["VIRUSTOTAL_API_KEY"], "bin": ["openclaw"] },
        "category": "security",
      },
  }
command-dispatch: tool
command_tool: exec
command_template: "node --import tsx skills/skill-cleaner/scripts/clean.ts {args}"
tags: [security, trust, virus-total, scanner]
---

# Skill Cleaner

Scans your installed skills for suspicious patterns, verifies them against VirusTotal, and "fixes" false positives by adding them to the safety allowlist.

## Usage

Run the cleaner to automatically verify and allowlist suspicious skills:

```bash
# Dry run (safe, just shows what would happen)
npx tsx ./skills/skill-cleaner/scripts/clean.ts

# Commit trust to safety allowlist for clean files
npx tsx ./skills/skill-cleaner/scripts/clean.ts --commit

# Full Security Fix: Trust clean files AND quarantine malicious ones
npx tsx ./skills/skill-cleaner/scripts/clean.ts --fix
```

## Features

- **Heuristic Scanning**: Uses OpenClaw Core scanner to find suspicious code patterns.
- **VirusTotal Integration**: Cross-references hashes with VT for reputation.
- **Trust Bridge**: Automatically allowlists "false positives" via the Gateway.
- **Quarantine**: Moves malicious files (detects > 0 on VT) to a `.quarantine/` folder for safety.

## Security Disclosure

This skill requires high-privilege access to function as a security utility:

- **Safe Bridge**: Uses a hardened, non-shell Bridge (Gateway RPC) to verify and trust skills. This avoids direct file system mutation for the allowlist.
- **Privacy**: Only loads the `VIRUSTOTAL_API_KEY` from your `.env` file; it does not access or expose unrelated secrets.
- **Verification**: Performs a **Live Scan** of your `skills/` directory using the internal OpenClaw security module to compute hashes.

**Audit Guidance**: If you see "High Privilege" flags on the Hub, this is expected behavior for a tool that interacts with the Security Core. Always run in dry-run mode first to inspect planned changes.
