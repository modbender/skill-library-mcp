---
name: bounty-hunter
description: Automated smart contract bug bounty hunting. Scans Immunefi/Code4rena targets with Slither static analysis, triages findings with local LLMs, and generates PoC templates. Zero API cost for scanning phase.
version: 1.0.0
---

# Bounty Hunter

Automated smart contract vulnerability scanner for bug bounty programs. Uses free tools (Slither + local LLMs) for the heavy lifting, saves expensive models for PoC writing.

## Requirements

- `slither-analyzer` (pip): Static analysis
- `solc-select` (pip): Solidity compiler management  
- Node.js: For script execution
- Optional: Ollama with any code model for local triage

## Quick Start

```bash
# Scan a repo
bash scripts/scan.sh <github-repo-url> [src-dir]

# Triage findings (uses local LLM if available, otherwise prints raw)
bash scripts/triage.sh <scan-output.json>

# Generate PoC template for a finding
bash scripts/poc-template.sh <finding-id> <contract-address>
```

## Workflow

1. **Target Selection** — Check Immunefi/Code4rena for active programs
2. **Clone & Scan** — `scan.sh` clones the repo, installs solc, runs Slither
3. **Triage** — `triage.sh` filters HIGH/MEDIUM findings, removes known false positives
4. **Deep Dive** — Only read code that Slither flagged (save your tokens)
5. **PoC** — Use `poc-template.sh` to generate Foundry test scaffolding
6. **Submit** — Write up finding on Immunefi/Code4rena

## Target Selection Criteria

Before scanning, check:
- Scope last updated within 30 days (fresh code = more bugs)
- Past payouts > $50K (they actually pay)
- GitHub repo in scope (not just deployed addresses)
- Solidity-based (Slither only works with Solidity)

## Anti-Patterns

- Don't read entire codebases manually — let Slither scan first
- Don't spend > 1 hour on a target without a concrete lead
- Don't submit known issues (check past reports first)
- Don't ignore test coverage — untested code is where bugs hide
