---
name: skillgate-gov
description: "Supply-chain governance for OpenClaw skills: scan, assess, quarantine/restore."
metadata: { "openclaw": { "emoji": "🛡️", "requires": { "bins": ["node", "npm"] }, "homepage": "https://github.com/skillgatesecurity/openclaw-skillgate" } }
---

# SkillGate (Governance)

This skill teaches OpenClaw how to run SkillGate against a skills directory, generate evidence, and quarantine risky skills.

## Quick Start (recommended)

> We intentionally avoid global installs (`npm i -g`) to reduce supply-chain risk.
> Use a pinned version via `npx` for deterministic behavior.

```bash
# Scan current workspace (read-only by default)
npx --yes @skillgate/openclaw-skillgate@0.1.3 gov_scan .

# Show a human-readable explanation for a finding
npx --yes @skillgate/openclaw-skillgate@0.1.3 gov_explain <EVIDENCE_JSON_PATH>
```

## Provenance / How to verify what you run

```bash
# Verify package metadata
npm view @skillgate/openclaw-skillgate@0.1.3 name version license repository
npm view @skillgate/openclaw-skillgate@0.1.3 dist.tarball dist.integrity

# Optional: verify GitHub release & source
# Repo: https://github.com/skillgatesecurity/openclaw-skillgate
```

This package is published under the official `@skillgate` scope and built/released via GitHub Actions.

## Permissions & Filesystem scope

- **Network**: not required for scanning local files (except fetching the npm package on first run).
- **Default mode**: read-only scan of the given directory.
- **Writes** (only when you explicitly run quarantine/restore commands):
  - creates/updates evidence outputs under a local folder (e.g. `.skillgate/` or the specified output path)
  - may quarantine a skill by moving/marking files within the target directory you pass in

It does not require secrets (no tokens/keys) and does not modify system-wide settings.

## OpenClaw Plugin Commands

Once loaded as an OpenClaw plugin, these slash commands become available:

```bash
# scan all skills for risks (default: HIGH+)
/gov scan

# scan with all findings including LOW/INFO
/gov scan --all

# quarantine a specific skill
/gov quarantine <skillKey>

# restore a quarantined skill
/gov restore <skillKey>

# explain why a skill was flagged
/gov explain <skillKey>

# show governance status
/gov status
```

## Risk Levels

| Level | Auto Action | Description |
|-------|-------------|-------------|
| CRITICAL | Quarantine | Shell injection, supply-chain attacks |
| HIGH | Disable | Dangerous patterns, external downloads |
| MEDIUM | Warn | Risky but not immediately dangerous |
| LOW/INFO | Log | Informational only |

## Local Development (optional)

If you prefer a local dependency instead of `npx`:

```bash
npm i -D @skillgate/openclaw-skillgate@0.1.3
npx gov_scan .
```

## Notes

Use this as the standard operating procedure for Skill supply-chain reviews.
