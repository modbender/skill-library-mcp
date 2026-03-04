# Security Policy

## Antivirus / Malware Scanner False Positives

**Crabukit may be flagged by antivirus scanners (including VirusTotal) as "suspicious" or as malware (e.g., "SordealStealer", "Generic.PY"). This is a FALSE POSITIVE.**

### Why This Happens

Crabukit is a **defensive security scanner** (like Bandit, Semgrep, or YARA). It is flagged because:

1. **Pattern Matching**: AV engines detect code patterns like `eval()`, `exec()`, subprocess calls, and file scanning
2. **Similarity to Malware**: Real malware (like SordealStealer) uses these patterns for malicious purposes
3. **Defensive vs Offensive**: Crabukit uses these patterns to **detect** threats, not **perform** them

### What's Actually in the Code

- ✅ **Searches for credentials** - To warn users about exposed secrets
- ✅ **Detects `eval()`/`exec()`** - To flag dangerous code
- ✅ **Uses subprocess** - To run external security tools like Clawdex
- ✅ **Scans files** - To analyze SKILL.md and scripts for vulnerabilities

### Verification

- **Open Source**: All code is auditable at https://github.com/tnbradley/crabukit
- **Purpose**: Defensive security scanning for OpenClaw skills
- **No Network Exfiltration**: Only calls public Clawdex API (optional)
- **No Persistence**: Does not install backdoors or modify system files

If you have concerns, please review the code or contact us via GitHub Security Advisories.

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.2.x   | :white_check_mark: |
| < 0.2   | :x:                |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via GitHub's private vulnerability reporting feature:

🔗 **https://github.com/tnbradley/crabukit/security/advisories**

Or open a private discussion with the maintainer.

We aim to respond within 48 hours.

### What to Include

- Description of the vulnerability
- Steps to reproduce
- Potential impact assessment
- Suggested fix or mitigation (if any)
- Whether you'd like to be credited publicly

### Response Process

1. **Acknowledgment** - We confirm receipt within 48 hours
2. **Assessment** - We evaluate the vulnerability and determine severity
3. **Fix** - We develop and test a fix
4. **Disclosure** - We coordinate disclosure timeline with you
5. **Release** - We release the fix and publish a security advisory

## Security Best Practices

### For Skill Authors

1. **Principle of Least Privilege** - Only request tools you absolutely need
2. **Input Validation** - Never trust user input; validate before using
3. **No Secrets** - Never hardcode API keys, passwords, or tokens
4. **Safety Warnings** - Include warnings for destructive operations
5. **Code Review** - Have others review your skill before publishing

### For Skill Users

1. **Scan Before Install** - Always run `crabukit scan` before installing
2. **Review Permissions** - Check what tools the skill requests
3. **Trusted Sources** - Only install from trusted publishers
4. **Keep Updated** - Update skills regularly for security patches

## Known Security Considerations

### Limitations

- **Static Analysis Only**: Crabukit performs static analysis; dynamic/runtime behavior may differ
- **No Sandbox Execution**: We don't execute code to check behavior (by design)
- **Evasion Possible**: Determined attackers may craft code that evades detection

### Defense in Depth

Crabukit is one layer of defense. We recommend:
- Scanning skills before installation
- Reviewing code manually for critical skills
- Running skills with minimal privileges
- Monitoring skill behavior

## Security-Related Configuration

### CI/CD Fail Thresholds

```bash
# Conservative (recommended for production)
crabukit scan ./skill --fail-on=medium

# Strict (recommended for high-security environments)
crabukit scan ./skill --fail-on=low
```

### SARIF Output for GitHub Advanced Security

```bash
crabukit scan ./skill --format=sarif --output=results.sarif
```

## Acknowledgments

We thank the security researchers who have responsibly disclosed vulnerabilities:

- (Your name could be here!)

---

Last updated: 2026-02-20
