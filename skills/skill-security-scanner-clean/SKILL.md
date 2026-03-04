---
name: skill-security-scanner
description: Security scanner for OpenClaw skills. Use when installing, updating, or auditing skills to detect malicious backdoors, suspicious code patterns, data exfiltration risks, and security vulnerabilities. Automatically analyzes Python/JavaScript/Shell code for dangerous functions (eval, exec, system calls), network requests, file operations, environment variable access, obfuscation patterns, and known attack signatures. Provides security score and installation recommendations.
---

# Skill Security Scanner

Protect your OpenClaw installation from malicious skills. This scanner performs static analysis on skill code to detect:

- **Code Execution Threats**: `eval`, `exec`, `os.system`, `subprocess` calls
- **Data Exfiltration**: Hidden network requests, suspicious URLs, IP connections  
- **System Compromise**: File deletion, permission changes, privilege escalation
- **Credential Theft**: Environment variable access, secret harvesting
- **Cryptojacking**: Mining malware, suspicious compute patterns
- **Obfuscation**: Hidden code, base64 encoding, minification
- **Spyware**: Keyloggers, screen capture, surveillance features

## Quick Start

```bash
# Basic scan
python scripts/security_scanner.py /path/to/skill

# Strict mode (catches more suspicious patterns)
python scripts/security_scanner.py /path/to/skill --strict

# Save JSON report
python scripts/security_scanner.py /path/to/skill --format json -o report.json

# Generate markdown report
python scripts/security_scanner.py /path/to/skill --format markdown -o report.md
```

## Understanding Results

### Verdict Levels

| Verdict | Emoji | Meaning | Action |
|---------|-------|---------|--------|
| **PASS** | 🟢 | No critical issues found | Safe to install |
| **REVIEW** | 🟡 | Some concerns, review recommended | Check findings before installing |
| **WARNING** | 🟠 | High-risk patterns detected | Strongly reconsider installation |
| **REJECT** | 🔴 | Critical threats identified | **DO NOT INSTALL** |

### Security Score

- **90-100**: Excellent - minimal risk
- **70-89**: Good - minor issues
- **50-69**: Fair - requires review
- **0-49**: Poor - significant risks

## Detection Rules

### Critical (🔴)

| Rule | Description | Example |
|------|-------------|---------|
| EXEC001 | Code execution functions | `eval()`, `exec()`, `compile()` |
| SUSPICIOUS001 | Keylogger functionality | `pynput`, `keyboard` modules |
| SUSPICIOUS003 | Cryptocurrency mining | `mining`, `bitcoin`, `stratum+tcp` |

### High (🟠)

| Rule | Description | Example |
|------|-------------|---------|
| EXEC002 | System command execution | `os.system()`, `subprocess.call()` |
| NET002 | Raw socket connections | `socket.connect()` |
| ENV001 | Sensitive credential access | `os.environ['PASSWORD']` |
| OBF001 | Code obfuscation | Base64, hex-encoded code |
| SUSPICIOUS002 | Screen capture | `pyautogui.screenshot()` |
| NET004 | Short URL usage | `bit.ly`, `tinyurl` links |

### Medium (🟡)

| Rule | Description | Example |
|------|-------------|---------|
| NET001 | HTTP network requests | `requests.get()`, `fetch()` |
| ENV002 | Environment enumeration | `os.environ.items()` |
| FILE001 | File deletion | `os.remove()`, `shutil.rmtree()` |
| DATA001 | Unsafe deserialization | `pickle.loads()`, `yaml.load()` |
| NET003 | Hardcoded IP addresses | Direct IP in URLs |
| OBF002 | Base64 encoded blocks | Large base64 strings |

### Low/Info (🔵/⚪)

| Rule | Description |
|------|-------------|
| FILE002 | File write operations |
| CRYPTO001 | Cryptographic operations |
| DOC001 | Insufficient documentation |
| DOC002 | Missing security statements |

## Workflow

### Before Installing a New Skill

1. Download the skill to a temporary directory
2. Run the security scanner
3. Review the verdict:
   - 🟢 **PASS**: Proceed with installation
   - 🟡 **REVIEW**: Examine findings, verify legitimate use
   - 🟠 **WARNING**: Only install from trusted sources
   - 🔴 **REJECT**: Do not install

4. For 🟡/🟠 findings, manually review the flagged code
5. Confirm the skill's behavior matches its documentation

### Before Updating an Existing Skill

1. Run scanner on the new version
2. Compare results with previous version's scan
3. Check for new critical/high findings
4. Review any new network/file operations

### Automated Integration

Add to your skill installation workflow:

```python
import subprocess
import sys

def safe_install_skill(skill_path):
    # Run security scan
    result = subprocess.run(
        ['python', 'scripts/security_scanner.py', skill_path, '--format', 'json'],
        capture_output=True,
        text=True
    )
    
    import json
    report = json.loads(result.stdout)
    
    if report['summary']['verdict'] == 'REJECT':
        print("❌ Installation blocked: Critical security issues found")
        return False
    
    if report['summary']['verdict'] == 'WARNING':
        response = input("⚠️ High-risk patterns detected. Install anyway? (y/N): ")
        if response.lower() != 'y':
            return False
    
    # Proceed with installation
    return True
```

## Handling False Positives

Some legitimate skills may trigger warnings:

- **Network requests**: Skills that fetch data from APIs
- **File operations**: Skills that modify documents
- **Encryption**: Skills handling sensitive data

When you trust the source and understand the functionality, you can:

1. Review the specific code flagged
2. Verify it matches the documented purpose
3. Manually approve if confident

## Reporting Issues

If you find a skill with confirmed malicious intent:

1. Do not install or run it
2. Report to the skill repository/hosting platform
3. Notify OpenClaw community channels
4. Share scan report (without executing the skill)

## Best Practices

1. **Only install skills from trusted sources**
2. **Always scan before installing** - even from trusted sources
3. **Review findings carefully** - understand what the skill does
4. **Keep scanner updated** - new detection rules added regularly
5. **Use strict mode for untrusted sources** - catches more suspicious patterns
6. **Check skill updates** - re-scan when updating existing skills

## Exit Codes

The scanner returns specific exit codes:

| Code | Meaning |
|------|---------|
| 0 | PASS or REVIEW - installation may proceed |
| 1 | WARNING - high-risk patterns found |
| 2 | REJECT - critical threats detected |

Use in scripts:

```bash
python scripts/security_scanner.py ./skill || {
    echo "Security check failed"
    exit 1
}
```
