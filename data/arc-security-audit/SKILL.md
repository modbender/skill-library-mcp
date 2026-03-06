---
name: security-audit
description: Comprehensive security audit for an agent's full skill stack. Chains scanner, differ, trust-verifier, and health-monitor into a single assessment with prioritized findings and trust attestations.
user-invocable: true
metadata: {"openclaw": {"emoji": "🛡️", "os": ["darwin", "linux"], "requires": {"bins": ["python3"]}}}
---

# Security Audit

One command to audit your entire skill stack. Chains together arc-skill-scanner, arc-trust-verifier, and generates a comprehensive risk report with prioritized findings.

## Why This Exists

Running individual security tools one at a time is tedious. A full audit needs scanning, trust assessment, binary verification, and a unified report. This skill does it all in one pass.

## Commands

### Audit all installed skills
```bash
python3 {baseDir}/scripts/audit.py full
```

### Audit a specific skill
```bash
python3 {baseDir}/scripts/audit.py single --path ~/.openclaw/skills/some-skill/
```

### Generate audit report as JSON
```bash
python3 {baseDir}/scripts/audit.py full --json --output report.json
```

### Audit with trust attestations
```bash
python3 {baseDir}/scripts/audit.py full --attest
```

## What It Does

1. **Scans** every installed skill with arc-skill-scanner patterns
2. **Assesses trust** for each skill (provenance, code cleanliness, binary presence)
3. **Checks binary integrity** with SHA-256 checksums
4. **Generates a prioritized report** sorted by risk level
5. **Optionally creates trust attestations** for skills that pass all checks

## Output

The audit report includes:
- Summary: total skills scanned, findings by severity, overall risk level
- Per-skill breakdown: findings, trust score, recommendations
- Critical actions: what to fix immediately
- Trust attestations for passing skills (if --attest flag used)
