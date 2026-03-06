# Security Notice - OpenClaw Shield

## Purpose

OpenClaw Shield is a **SECURITY SCANNER** designed to DETECT threats in AI agent code. It is NOT malicious software.

## Why This Tool Contains Security-Related Patterns

This repository contains:
- ✅ **Pattern definitions** for detecting credential theft, data exfiltration, and malicious code
- ✅ **Example threat signatures** used to identify dangerous operations
- ✅ **Detection logic** that scans OTHER code for security issues

**This is equivalent to antivirus signature databases** - they contain descriptions of threats to DETECT them, not to execute them.

## What This Tool Does NOT Do

❌ **Does NOT contain exploits** - No actual malicious code  
❌ **Does NOT steal credentials** - Detects when OTHER code tries to  
❌ **Does NOT exfiltrate data** - Detects when OTHER code tries to  
❌ **Does NOT run malicious operations** - Scans for them in target code

## What This Tool DOES Do

✅ **Scans Python code** for security threats using pattern matching  
✅ **Identifies suspicious operations** like credential access + network calls  
✅ **Generates security reports** in JSON format  
✅ **Prevents execution** of flagged code through allowlist enforcement  
✅ **Logs audit trails** with tamper-evident hashing

## Safe Usage

```bash
# Scan a directory for threats
python3 src/scanner.py /path/to/scan --output report.json

# Review the report
cat report.json

# Take action based on findings
```

## False Positive Explanation

Automated security tools may flag this repository because:

1. **Pattern definitions look like threats** - We define patterns like `ANTHROPIC_API_KEY` to DETECT when other code accesses them
2. **References to sensitive paths** - We check if code accesses `~/.ssh/`, `~/.aws/` to FLAG suspicious behavior
3. **Network + credential correlation** - We detect when code reads secrets AND makes network calls

**This is detection logic, not attack logic.**

## Comparison

| Tool | Contains Threat Patterns? | Malicious? |
|------|---------------------------|------------|
| ClamAV virus database | ✅ Yes (millions) | ❌ No - it's antivirus |
| Snort IDS signatures | ✅ Yes (thousands) | ❌ No - it's intrusion detection |
| **OpenClaw Shield** | ✅ Yes (dozens) | ❌ No - it's a code scanner |

## Responsible Disclosure

If you find an actual security vulnerability (not a false positive from our detection patterns):
- Report via GitHub Issues: https://github.com/pfaria32/OpenClaw-Shield-Security/issues
- Or email: security@openclaw.com (if configured)

## Verification

To verify this tool's safety:
1. ✅ Read the source code: `src/scanner.py` (Python stdlib only, no external dependencies)
2. ✅ Review pattern definitions: Lines contain regex patterns for DETECTION
3. ✅ Check for network calls: None in scanner code itself
4. ✅ Inspect git history: No hidden exploits or obfuscated code

## License & Disclaimer

MIT License - Provided "AS IS" with NO WARRANTIES.

**Use responsibly:** This is a security tool. Audit code before deploying. The scanner can only detect known patterns - it's not a substitute for human security review.

---

**TL;DR:** This is a security scanner that contains threat DETECTION patterns, not threat EXECUTION code. Like antivirus software, it describes threats to identify them.
