---
name: obekt-security
description: Basic threat detection and security analysis for code, files, and agent skills. Use when you need to scan for vulnerabilities, validate security patterns, detect malicious patterns, or audit codebases for security issues.
---

# ObekT Security

Basic threat detection and security analysis toolkit for code, files, and agent skills.

**Pro Tier** includes continuous monitoring and professional report generation for advanced security workflows.

## Core Capabilities

### 1. Pattern-Based Threat Detection
- Scan code for common vulnerability patterns (SQL injection, XSS, command injection)
- Identify hardcoded secrets, API keys, and credentials
- Detect unsafe file operations and path traversal risks
- Find insecure cryptographic practices

### 2. Security Audit Workflows
- Basic code review for skills and applications
- Check for authentication/authorization weaknesses
- Validate input handling and sanitization
- Review API endpoint security

### 3. Malicious Pattern Recognition
- Detect obfuscated code patterns
- Identify data exfiltration attempts
- Scan for suspicious network calls
- Check for unauthorized crypto wallet interactions

## Quick Start

### Installation

**Basic Tier (no dependencies):**
All core scanning scripts work with Python 3.8+ standard library.

**Pro Tier (additional dependencies):**
```bash
pip install watchdog  # For continuous monitoring
```

### Scan a Codebase for Common Vulnerabilities

```bash
python3 scripts/threat_scan.py --directory /path/to/code --severity medium,high
```

### Check for Hardcoded Secrets

```bash
python3 scripts/secret_scan.py --file path/to/source.py
```

### Audit an Agent Skill

```bash
python3 scripts/skill_audit.py --skill-path /path/to/skill
```

## Threat Detection Patterns

### Critical Severity Patterns
- Direct command execution with user input (exec, eval, os.system)
- SQL queries with string concatenation
- Hardcoded private keys or mnemonic phrases
- External wallet drain patterns
- Unrestricted file uploads

### High Severity Patterns
- Weak random number generation
- Hardcoded API keys or tokens
- Missing input validation
- Insecure cryptographic algorithms (MD5, SHA1)
- Path traversal vulnerabilities

### Medium Severity Patterns
- Logging sensitive data
- Insecure URL redirects
- Missing rate limiting
- Weak password policies

## Security Audit Checklist

When auditing code or skills, check:

- [ ] No hardcoded secrets (keys, tokens, passwords)
- [ ] Input validation and sanitization
- [ ] Proper error handling (no information leakage)
- [ ] Secure cryptographic implementations
- [ ] Authentication/authorization where required
- [ ] Principle of least privilege
- [ ] No command injection vulnerabilities
- [ ] Safe file operations
- [ ] Secure network communications
- [ ] Proper session management

## Using the Scripts

### threat_scan.py
Scans directories for known vulnerability patterns.

```bash
python3 scripts/threat_scan.py <path> [--severity LEVEL] [--output FORMAT]
```

**Options:**
- `--severity`: Filter by severity (critical, high, medium, low). Default: all
- `--output`: Output format (json, text, markdown). Default: text
- `--recursive`: Scan subdirectories. Default: true

**Example:**
```bash
# Find critical and high issues in a project
python3 scripts/threat_scan.py ~/project --severity critical,high --output markdown
```

### secret_scan.py
Detects hardcoded credentials and secrets.

```bash
python3 scripts/secret_scan.py <path> [--patterns PATTERN_FILE]
```

**Patterns detect:**
- API keys (AWS, Google, Stripe, etc.)
- Private keys (PEM, OpenSSH)
- Database connection strings
- Crypto wallet seeds/mnemonics
- OAuth tokens

### skill_audit.py
Audits agent skills for security issues.

```bash
python3 scripts/skill_audit.py <skill-path> [--quick]
```

**Checks:**
- SKILL.md structure and completeness
- Required vs. optional file permissions
- External dependencies and command safety
- Network calls and data handling
- Credential handling patterns

### monitor.py (Pro Tier)
Continuous security monitoring - watches directories for changes and auto-scans.

```bash
python3 scripts/monitor.py --path /path/to/project --interval 60
python3 scripts/monitor.py --config monitor.json
```

**Features:**
- Real-time monitoring of file changes
- Automatic threat and secret scans on modifications
- Configurable severity thresholds and scan intervals
- Alert notifications when issues found
- Smart filtering (ignores .git, node_modules, etc.)

**Options:**
- `--path`: Directory to monitor
- `--interval`: Minimum seconds between scans for same path
- `--severity`: Severity levels to report
- `--alert`: Enable alerts when issues found
- `--config`: JSON configuration file

### generate_report.py (Pro Tier)
Generate professional security audit reports.

```bash
python3 scripts/generate_report.py --scan-dir /path/to/project --output report.md
python3 scripts/generate_report.py --input scan_results.json --format html
```

**Features:**
- Multiple output formats: Markdown, HTML, JSON
- Executive summary with severity assessment
- Detailed findings with code snippets
- Prioritized recommendations
- Client-ready formatting

**Options:**
- `--scan-dir`: Directory to scan (fresh scan)
- `--input`: JSON file with existing scan results
- `--output`: Output file path
- `--format`: markdown, html, or json
- `--severity`: Severity levels to include

## Pro Tier Features

### 4. Continuous Monitoring
**NEW** - Real-time security monitoring for development workflows

Automatically monitor codebases for security vulnerabilities as you develop.

```bash
python3 scripts/monitor.py --path /path/to/project --interval 60
```

**Features:**
- Watch directories for file changes in real-time
- Auto-trigger security scans on file modifications
- Configurable scan intervals and severity thresholds
- Alert notifications when issues found (webhook ready)
- Skip temporary files and directories intelligently

**Configuration:**
```json
{
  "paths": ["./project"],
  "min_scan_interval": 30,
  "severity": "high,critical",
  "alert_on_issues": true,
  "recursive": true,
  "filters": {
    "include_extensions": [".py", ".js", ".ts", ".java", ".go", ".rs"],
    "exclude_dirs": [".git", "__pycache__", "node_modules", ".venv"]
  },
  "alert_config": {
    "webhook_url": "https://your-webhook-endpoint"
  }
}
```

### 5. Professional Report Generation
**NEW** - Generate client-ready audit reports

Create professional security audit reports in multiple formats for delivery to clients or compliance documentation.

```bash
# Generate report from fresh scan
python3 scripts/generate_report.py --scan-dir /path/to/project --output report.md

# Generate HTML report
python3 scripts/generate_report.py --scan-dir /path/to/project --output report.html --format html

# Generate from existing scan results
python3 scripts/generate_report.py --input scan_results.json --output client_report.md
```

**Features:**
- Multiple output formats: Markdown, HTML, JSON
- Professional formatting with severity color coding
- Executive summary with overall severity assessment
- Detailed findings with code snippets
- Actionable recommendations prioritized by severity
- Ready for client delivery

**Report Contents:**
- Executive summary with overall severity
- Severity breakdown table
- Detailed threat findings with code snippets
- Secret/credential exposure report
- Prioritized recommendations
- Timestamp and metadata

## Reference Documentation

For detailed threat patterns and remediation guidance:
- See [VULNERABILITY_PATTERNS.md](references/VULNERABILITY_PATTERNS.md) for complete pattern catalog
- See [REMEDIATION_GUIDE.md](references/REMEDIATION_GUIDE.md) for fixing issues
- See [CHECKLIST.md](references/CHECKLIST.md) for comprehensive audit checklist
- See [CRYPTO_SECURITY.md](references/CRYPTO_SECURITY.md) for blockchain-specific patterns

## Pricing Tiers

### Free Tier
- Pattern-based threat detection
- Secret scanning
- Basic skill auditing
- Manual scan execution

### Pro Tier ($5/month)
- All Free Tier features
- **Continuous monitoring daemon** with real-time alerts
- **Professional report generation** (Markdown, HTML, JSON)
- Client-ready deliverables for audit services
- Priority support

### Enterprise Tier ($50/month)
- All Pro Tier features
- Private skill audits
- Custom pattern rules
- Team collaboration features
- Webhook integrations

*Note: All tiers are self-contained. No cloud account required.*

## Integration with Other Skills

This skill works well with:
- **skill-creator**: Validate security of skills during development
- **clawcast**: Audit wallet transaction safety
- **auth-auditor**: Complement authentication flow security

## Limitations

This tool provides **basic** threat detection using pattern matching. It cannot replace:
- Manual security reviews by experts
- Dynamic application security testing (DAST)
- Penetration testing
- Static analysis tools (SAST) like SonarQube, CodeQL

Use as a first line of defense, not a replacement for comprehensive security assessments.
