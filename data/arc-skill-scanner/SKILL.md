---
name: skill-scanner
description: Scan OpenClaw skills for security vulnerabilities before installing them. Use when evaluating a new skill from ClawHub or any third-party source. Detects credential stealers, data exfiltration, malicious URLs, obfuscated code, and supply chain attacks.
user-invocable: true
metadata: {"openclaw": {"emoji": "🔒", "os": ["darwin", "linux"], "requires": {"bins": ["python3"]}}}
---

# Skill Scanner

Scan OpenClaw skills for security issues before you install them. 341 malicious skills were found on ClawHub — don't be the next victim.

## Why This Exists

The ClawHub marketplace had 22-26% of skills flagged as containing vulnerabilities. Common attacks include:
- **Credential stealers** disguised as benign plugins
- **Typosquatting** (fake names similar to popular skills)
- **Data exfiltration** via hidden HTTP requests
- **Obfuscated code** hiding malicious payloads
- **Prompt injection** via SKILL.md content

## Commands

### Scan a local skill directory
```bash
python3 {baseDir}/scripts/scanner.py scan --path ~/.openclaw/skills/some-skill/
```

### Scan a SKILL.md file directly
```bash
python3 {baseDir}/scripts/scanner.py scan --file ./SKILL.md
```

### Scan with verbose output
```bash
python3 {baseDir}/scripts/scanner.py scan --path ~/.openclaw/skills/some-skill/ --verbose
```

### Scan all installed skills
```bash
python3 {baseDir}/scripts/scanner.py scan-all
```

### Scan with binary checksum verification
```bash
python3 {baseDir}/scripts/scanner.py scan --path ~/.openclaw/skills/some-skill/ --checksum checksums.json
```

### Generate checksums for binary assets
```bash
python3 {baseDir}/scripts/scanner.py checksum --path ~/.openclaw/skills/some-skill/ -o checksums.json
```

### Verify checksums against a manifest
```bash
python3 {baseDir}/scripts/scanner.py checksum --path ~/.openclaw/skills/some-skill/ --verify checksums.json
```

### Output as JSON
```bash
python3 {baseDir}/scripts/scanner.py scan --path ./skill-dir/ --json
```

## What It Checks

### SKILL.md Analysis
- Suspicious URLs (non-HTTPS, IP addresses, URL shorteners)
- Prompt injection patterns (hidden instructions, override attempts)
- Requests for credentials, API keys, or tokens
- Obfuscated or encoded content (base64, hex, unicode escapes)

### Script Analysis
- Network calls (curl, wget, requests, urllib, fetch)
- File system writes outside expected paths
- Environment variable access (credential harvesting)
- Shell command execution (os.system, subprocess, exec)
- Obfuscated strings (base64 decode, eval, exec)
- Data exfiltration patterns (POSTing to external URLs)
- Cryptocurrency wallet patterns
- Known malicious domains
- Dynamic instruction fetching (remote .md/.yaml/.json downloads)
- Fetch-and-execute patterns (remote code execution)
- Telemetry leaks (printenv, logging env vars/configs/secrets to stdout)
- Binary/asset risks (prebuilt executables, compiled code, library injection)
- Shell=True in subprocess calls (RCE risk)
- Path traversal patterns (directory escape via ../ sequences)

### Name Analysis
- Typosquatting detection (compares against known popular skills)
- Edit distance calculation to catch misspellings and character swaps

### Binary/Asset Checksum Verification
- SHA-256 checksums for all binary files (.exe, .dll, .so, .wasm, .pyc, etc.)
- Generate checksum manifests for trusted skill versions
- Verify binaries against expected checksums on update
- Flags unverified binaries and checksum mismatches (tampering detection)

### Metadata Analysis
- Excessive permission requirements
- Suspicious install scripts
- Env requirements that seem unnecessary

## Risk Levels

- **CRITICAL** — Almost certainly malicious. Do NOT install.
- **HIGH** — Likely malicious or extremely risky. Manual review required.
- **MEDIUM** — Suspicious patterns found. Review before installing.
- **LOW** — Minor concerns. Probably safe but worth checking.
- **CLEAN** — No issues detected. Safe to install.

## Tips

- Always scan before installing ANY third-party skill
- Even "CLEAN" results aren't a guarantee — this catches known patterns
- If a skill needs network access, verify the domains it contacts
- Cross-reference skill names with known typosquats
- When in doubt, read the source code yourself
