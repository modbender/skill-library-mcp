# Security Scanner - Detection Rules Reference

Complete reference for all detection rules and their patterns.

## Rule Categories

### EXEC - Code Execution

Rules detecting dynamic code execution capabilities.

| ID | Name | Pattern | Severity |
|----|------|---------|----------|
| EXEC001 | Code Execution Functions | `\b(eval\|exec\|compile\|__import__\|execfile)\s*\(` | Critical |
| EXEC002 | System Command Execution | `\b(os\.system\|subprocess\.(call\|run\|Popen\|check_output)\|popen\|spawn\|shell=True)\s*\(` | High |

**Why it matters**: These functions can execute arbitrary code, bypassing normal security controls.

**Common legitimate uses**:
- Running external tools (ffmpeg, git, etc.)
- Dynamic configuration loading
- Plugin systems

**Red flags**:
- User input passed directly to these functions
- Obfuscated code using these functions
- Network data fed into eval/exec

### NET - Network Operations

Rules detecting network communication capabilities.

| ID | Name | Pattern | Severity |
|----|------|---------|----------|
| NET001 | HTTP Requests | `\b(requests\.(get\|post)\|urllib\|http\.client\|fetch\|axios\.)` | Medium |
| NET002 | Raw Sockets | `\b(socket\.(socket\|connect)\|\.connect\s*\(\|socket\.AF_INET)` | High |
| NET003 | Hardcoded IPs | `https?://\d+\.\d+\.\d+\.\d+` | Medium |
| NET004 | Short URLs | `bit\.ly\|tinyurl\|t\.co\|goo\.gl` | High |

**Why it matters**: Network access enables data exfiltration, command & control, and payload downloading.

**Common legitimate uses**:
- API integrations (weather, finance, etc.)
- Data fetching from public sources
- Webhook notifications

**Red flags**:
- Communication with unknown/external servers
- Sending local file data over network
- Using IP addresses instead of domains
- Short URLs hiding destinations
- No documentation of network usage

### FILE - File System Operations

Rules detecting file system modifications.

| ID | Name | Pattern | Severity |
|----|------|---------|----------|
| FILE001 | File Deletion | `\b(os\.remove\|os\.rmdir\|shutil\.rmtree\|os\.unlink)` | Medium |
| FILE002 | File Writing | `\b(open\s*\(\s*[^,\)]*,\s*['"]w\|fs\.writeFile)` | Low |

**Why it matters**: File operations can destroy data, plant malware, or modify system files.

**Common legitimate uses**:
- Creating output files
- Temporary file cleanup
- Cache management

**Red flags**:
- Deleting files outside skill directory
- Modifying system files
- Overwriting user documents
- No backup before destructive operations

### ENV - Environment Access

Rules detecting access to system environment.

| ID | Name | Pattern | Severity |
|----|------|---------|----------|
| ENV001 | Sensitive Variables | `\b(os\.environ\|process\.env)\s*\[?\s*['"](PASSWORD\|SECRET\|KEY\|TOKEN)` | High |
| ENV002 | Variable Enumeration | `\b(os\.environ\|process\.env)\.(items\|keys\|values)` | Medium |

**Why it matters**: Environment variables often contain credentials and sensitive configuration.

**Common legitimate uses**:
- Reading API keys for configured services
- Checking PATH or HOME
- Configuration via environment

**Red flags**:
- Accessing password/secret variables
- Bulk collection of all environment data
- Sending environment data over network
- No explanation in documentation

### CRYPTO - Cryptographic Operations

Rules detecting encryption/encoding operations.

| ID | Name | Pattern | Severity |
|----|------|---------|----------|
| CRYPTO001 | Crypto Operations | `\b(hashlib\|cryptography\|Crypto\.Cipher\|bcrypt)` | Low |

**Why it matters**: Encryption can be used for both legitimate security and malicious obfuscation.

**Common legitimate uses**:
- Password hashing
- Data integrity verification
- Secure communication

**Red flags**:
- Obfuscating code with encryption
- Custom crypto implementations
- No clear purpose in documentation

### OBF - Obfuscation

Rules detecting code hiding techniques.

| ID | Name | Pattern | Severity |
|----|------|---------|----------|
| OBF001 | Code Obfuscation | Long repetitive patterns, hex/unicode escapes | High |
| OBF002 | Base64 Blocks | Large base64 strings | Medium |

**Why it matters**: Obfuscation hides what code actually does, making auditing impossible.

**Red flags**:
- Large blocks of encoded data
- Multiple layers of encoding
- No source code provided
- Minified code without original source

### SUSPICIOUS - Malware Indicators

Rules detecting known malicious behavior patterns.

| ID | Name | Pattern | Severity |
|----|------|---------|----------|
| SUSPICIOUS001 | Keylogging | `\b(keyboard\|pynput\|hook\|GetAsyncKeyState\|keylogger)` | Critical |
| SUSPICIOUS002 | Screen Capture | `\b(pyautogui\.screenshot\|PIL\.ImageGrab\|mss\|screenshot)` | High |
| SUSPICIOUS003 | Cryptomining | `\b(mining\|miner\|bitcoin\|monero\|stratum\+tcp)` | Critical |

**Why it matters**: These are clear indicators of malicious intent.

**Never legitimate**:
- Keyloggers in OpenClaw skills
- Unauthorized screen recording
- Cryptocurrency mining

### DATA - Data Handling

Rules detecting unsafe data processing.

| ID | Name | Pattern | Severity |
|----|------|---------|----------|
| DATA001 | Unsafe Deserialization | `\b(pickle\.(loads\|load)\|yaml\.load\|marshal\.loads)` | Medium |

**Why it matters**: Deserialization can lead to code execution vulnerabilities.

**Common legitimate uses**:
- Loading cached data
- Configuration files
- Internal data formats

**Red flags**:
- Deserializing untrusted network data
- Using pickle for user input
- No input validation

### PERM - Permission Operations

Rules detecting permission changes.

| ID | Name | Pattern | Severity |
|----|------|---------|----------|
| PERM001 | Privilege Escalation | `\b(setuid\|setgid\|os\.chmod.*0o[0-7]{3,4}\|777\|sudo)` | High |

**Why it matters**: Permission changes can enable further compromise.

**Red flags**:
- Setting 777 permissions
- Requesting sudo/admin
- Changing file ownership

### DOC - Documentation

Rules checking skill documentation quality.

| ID | Name | Check | Severity |
|----|------|-------|----------|
| DOC001 | Short Documentation | SKILL.md < 500 chars | Low |
| DOC002 | Missing Security Info | No security/privacy section | Low |

**Why it matters**: Good documentation indicates transparency and trustworthiness.

## Risk Scoring Algorithm

```
Base Score: 100
- Critical finding: -30 points
- High finding: -15 points  
- Medium finding: -5 points
- Low finding: -2 points

Minimum Score: 0
```

### Verdict Determination

| Condition | Verdict |
|-----------|---------|
| Any Critical | REJECT |
| Any High | WARNING |
| >2 Medium OR Score < 90 | REVIEW |
| Score >= 90 | PASS |

## Whitelisting Guidelines

When reviewing findings, consider:

1. **Is the behavior documented?**
   - Skill description explains the functionality
   - Users are informed what will happen

2. **Is it proportional to the skill's purpose?**
   - Weather skill making API calls: ✅ Expected
   - Calculator skill making network requests: 🚩 Suspicious

3. **Is user data protected?**
   - No unexpected data transmission
   - Sensitive data stays local

4. **Can the user control it?**
   - Clear opt-in/opt-out
   - Configurable behavior

## Advanced Usage

### Custom Rule Sets

You can extend the scanner with custom rules:

```python
from security_scanner import SecurityScanner

class CustomScanner(SecurityScanner):
    CUSTOM_PATTERNS = {
        "CUSTOM001": {
            "name": "Your Custom Rule",
            "pattern": r'your_regex_pattern',
            "description": "What this detects",
            "risk": RiskLevel.MEDIUM,
            "recommendation": "What to do about it"
        }
    }
```

### Integration with CI/CD

```yaml
# .github/workflows/security-scan.yml
name: Skill Security Scan
on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Security Scanner
        run: |
          python scripts/security_scanner.py . --format json -o report.json
      - name: Check Results
        run: |
          if grep -q '"verdict": "REJECT"' report.json; then
            echo "Security check failed!"
            exit 1
          fi
```

## Threat Model

This scanner addresses:

1. **Supply Chain Attacks**: Malicious skills distributed through repositories
2. **Data Exfiltration**: Skills stealing user data
3. **System Compromise**: Skills modifying system settings/files
4. **Credential Theft**: Skills harvesting passwords/keys
5. **Resource Abuse**: Cryptominers, botnet participants
6. **Surveillance**: Keyloggers, screen recorders

## Limitations

The scanner cannot detect:

- **Zero-day vulnerabilities**: Unknown attack patterns
- **Logic bombs**: Time/delayed triggers
- **Polymorphic code**: Self-modifying malware
- **External payloads**: Code downloaded at runtime
- **Social engineering**: Tricking users into actions

**Always combine with**:
- Source code review
- Reputation checking
- Sandboxed testing
- Network monitoring
