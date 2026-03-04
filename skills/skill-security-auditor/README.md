# Skill Security Auditor 🛡️

**Protect your OpenClaw agent from malicious skills before installation**

## Overview

The Skill Security Auditor is a **command-line security analysis tool** that scans ClawHub skills for malicious patterns, credential leaks, and suspicious behaviors before you install them.

Born from the ClawHavoc campaign that distributed 341+ malicious skills stealing cryptocurrency credentials, this tool provides pattern-based threat detection using a curated threat intelligence database.

**Key Point**: This is a **manual CLI tool** you run before installing skills. It does not automatically scan or block installations - it provides security analysis to help you make informed decisions.

## Why You Need This

In February 2026, researchers discovered 341 malicious ClawHub skills that:
- 📦 Distributed Atomic Stealer (AMOS) malware
- 💰 Stole cryptocurrency exchange API keys
- 🔑 Harvested SSH credentials and browser passwords
- 🎭 Used sophisticated social engineering
- 🌐 Shared C2 infrastructure (91.92.242.30)

**This skill helps you avoid becoming a victim.**

## Features

✅ **Malicious Pattern Detection** - Identifies known attack patterns from ClawHavoc and other campaigns  
✅ **Credential Leak Analysis** - Finds hardcoded secrets and exfiltration vectors  
✅ **Dependency Validation** - Checks for suspicious binary requirements  
✅ **C2 Infrastructure Detection** - Flags known malicious IPs and domains  
✅ **Risk Scoring** - Quantitative 0-100 risk assessment  
✅ **VirusTotal Integration** - Links to OpenClaw's VirusTotal partnership  
✅ **Detailed Audit Reports** - Comprehensive security analysis with recommendations  

## Installation

### Via ClawHub CLI (Recommended)

```bash
# Install the skill
npx clawhub@latest install skill-security-auditor

# Make the analyzer script executable
chmod +x ~/.openclaw/skills/skill-security-auditor/analyze-skill.sh

# Test it works
~/.openclaw/skills/skill-security-auditor/analyze-skill.sh --help
```

### Manual Installation

```bash
# Create skill directory
mkdir -p ~/.openclaw/skills/skill-security-auditor/patterns

# Download SKILL.md
curl -o ~/.openclaw/skills/skill-security-auditor/SKILL.md \
  https://raw.githubusercontent.com/YOUR-USERNAME/skill-security-auditor/main/SKILL.md

# Download analyzer script
curl -o ~/.openclaw/skills/skill-security-auditor/analyze-skill.sh \
  https://raw.githubusercontent.com/YOUR-USERNAME/skill-security-auditor/main/analyze-skill.sh

# Download patterns database
curl -o ~/.openclaw/skills/skill-security-auditor/patterns/malicious-patterns.json \
  https://raw.githubusercontent.com/YOUR-USERNAME/skill-security-auditor/main/patterns/malicious-patterns.json

# Make executable
chmod +x ~/.openclaw/skills/skill-security-auditor/analyze-skill.sh
```

### Requirements

Required command-line tools (usually pre-installed):
- `bash` - Shell interpreter (v4.0+)
- `curl` - Fetching skills from ClawHub
- `jq` - JSON processing
- `grep` - Pattern matching

**Check if installed:**
```bash
for cmd in bash curl jq grep; do
  command -v $cmd &>/dev/null && echo "✓ $cmd" || echo "✗ $cmd (missing)"
done
```

**Install missing tools:**
```bash
# macOS
brew install jq

# Ubuntu/Debian
sudo apt install jq

# Windows (WSL2)
sudo apt install jq
```

## Quick Start

### 1. Audit Before Installation

**Instead of immediately installing:**
```bash
npx clawhub install solana-wallet-tracker  # ❌ Don't do this first
```

**Do this:**
```bash
# Install the security auditor
npx clawhub install skill-security-auditor

# Make script executable
chmod +x ~/.openclaw/skills/skill-security-auditor/analyze-skill.sh

# Audit the skill FIRST
~/.openclaw/skills/skill-security-auditor/analyze-skill.sh -s solana-wallet-tracker

# Example output:
# ============================================
#          SECURITY AUDIT REPORT
# ============================================
# 
# Risk Score: 85/100 - ☠️ CRITICAL
#
# ☠️ CRITICAL FINDINGS:
#   CLAW-001: Fake Prerequisites - ClawHavoc Campaign [+50 points]
#   └─ Matches ClawHavoc malware campaign pattern
#   CLAW-002: Known C2 Infrastructure [+50 points]
#   └─ IP address 91.92.242.30 detected
#
# ============================================
# RECOMMENDATION:
# DO NOT INSTALL. Malicious patterns detected.
# ============================================

# Based on results, decide whether to install
```

### 2. Audit Installed Skills

```bash
# Scan all currently installed skills
for skill in ~/.openclaw/skills/*/SKILL.md; do
  echo "Auditing: $(basename $(dirname $skill))"
  ~/.openclaw/skills/skill-security-auditor/analyze-skill.sh -f "$skill"
  echo ""
done

# Example output:
# Auditing: github-helper
# Risk Score: 15/100 - ✅ SAFE
# 
# Auditing: crypto-trading-bot  
# Risk Score: 72/100 - 🔴 HIGH RISK
# ⚠️ HIGH RISK FINDINGS:
#   CLAW-102: SSH Key Access [+30 points]
```

### 3. Create Convenience Alias

```bash
# Add to ~/.bashrc or ~/.zshrc
echo 'alias audit-skill="~/.openclaw/skills/skill-security-auditor/analyze-skill.sh"' >> ~/.bashrc
source ~/.bashrc

# Now you can simply run:
audit-skill -s any-skill-name
audit-skill -f /path/to/SKILL.md
```

## Risk Scoring

| Score | Level | Description | Action |
|-------|-------|-------------|--------|
| 0-20 | ✅ SAFE | No significant concerns | Proceed with installation |
| 21-40 | ⚠️ LOW | Minor concerns | Proceed with caution |
| 41-60 | 🟡 MEDIUM | Multiple red flags | Manual review recommended |
| 61-80 | 🔴 HIGH | Serious concerns | Expert review required |
| 81-100 | ☠️ CRITICAL | Malicious indicators | DO NOT INSTALL |

## What Gets Detected

### 🚨 Critical Threats

- **Fake Prerequisites** - ClawHavoc-style malware delivery
- **Known C2 Infrastructure** - Malicious IPs/domains
- **Credential Harvesting** - API keys, SSH keys, wallet access
- **Remote Code Execution** - `curl | bash` patterns
- **Obfuscated Payloads** - Base64 encoded execution

### ⚠️ Warning Signs

- Suspicious binary requirements
- Excessive permission requests
- Network calls to unknown hosts
- Social engineering language
- New/unverified authors

### ✅ Positive Indicators

- Verified authors (>1 year GitHub account)
- Transparent dependencies
- Clean, documented code
- Official source repositories
- Active community engagement

## Example Audit Report

```markdown
## Security Audit Report

**Skill**: github-pr-automator
**Author**: verified-dev
**Version**: 2.1.0
**Audit Date**: 2026-02-08

### Risk Score: 18/100 - SAFE ✅

### Critical Findings:
None detected.

### Warning Indicators:
- Uses child_process for git operations (justified and safe)

### Positive Indicators:
- Author has 47 published skills
- GitHub account created 2019
- Uses official GitHub CLI (gh)
- Clear documentation
- No external network calls
- VirusTotal: 0/70 detections

### Recommendations:
✅ SAFE TO INSTALL

This skill appears legitimate and follows security best practices.

### Detailed Analysis:
The skill uses the official GitHub CLI tool for PR operations,
which is a trusted and verified binary. All operations are
documented and transparent. No credential access or external
communications detected beyond GitHub API via official client.
```

## Advanced Usage

### Custom Pattern Database

Add your own threat intelligence:

```bash
# Add custom malicious pattern
jq '.patterns.critical += [{
  "id": "CUSTOM-001",
  "name": "My Custom Pattern",
  "pattern": "suspicious-pattern-here",
  "severity": "critical",
  "score_impact": 40,
  "description": "My custom threat detection"
}]' ~/.openclaw/skills/skill-security-auditor/patterns/malicious-patterns.json > temp.json
mv temp.json ~/.openclaw/skills/skill-security-auditor/patterns/malicious-patterns.json
```

### Whitelist Trusted Skills

```bash
# Add trusted author
jq '.whitelisted_patterns.verified_authors += ["your-github-username"]' \
  patterns/malicious-patterns.json > temp.json
```

### Update Threat Intelligence

```bash
# Pull latest patterns (when community database available)
curl -s "https://openclaw-security.github.io/threat-intel/latest.json" \
  -o ~/.openclaw/skills/skill-security-auditor/patterns/ioc-database.json
```

## Integration with Existing Tools

### With VirusTotal (via ClawHub)

This tool provides **pattern-based analysis** while ClawHub provides **binary/file scanning** through their VirusTotal partnership.

**Workflow:**
1. **Run pattern analysis** (local, instant):
   ```bash
   ~/.openclaw/skills/skill-security-auditor/analyze-skill.sh -s suspicious-skill
   ```

2. **Check VirusTotal results** (via ClawHub web interface):
   - Visit: `https://clawhub.ai/skills/suspicious-skill`
   - Look for VirusTotal scan results on the page
   - ClawHub automatically scans published skills

3. **Combine both assessments** for comprehensive security evaluation

**Note**: This tool does NOT access VirusTotal's API directly. The integration is through ClawHub's web interface.

### With Manual Code Review

Use this skill as **first-line defense**, then:

1. Review flagged sections in SKILL.md
2. Inspect any referenced scripts/binaries
3. Test in sandboxed environment
4. Monitor network activity during testing

## Contributing

### Report Malicious Skills

Found a malicious skill? Submit to:
- **ClawHub Moderation**: Use built-in report feature
- **Security Working Group**: [GitHub Issues](https://github.com/openclaw/security-auditor/issues)

### Contribute Patterns

Submit new detection patterns:

```json
{
  "id": "YOUR-ID",
  "name": "Pattern Name",
  "pattern": "regex-pattern",
  "severity": "critical|high|medium|low",
  "score_impact": 1-50,
  "description": "What this detects",
  "mitre_attack": "T#### - Technique Name",
  "references": ["https://..."]
}
```

## Limitations

⚠️ **Important**:

- This tool provides **analysis, not guarantees**
- Sophisticated malware may evade detection
- Always combine with VirusTotal + manual review
- Zero-day attacks won't have known patterns
- Security is a **shared responsibility**

**Defense in depth**: Use this as ONE layer of security, not the ONLY layer.

## FAQ

**Q: Will this catch all malicious skills?**  
A: No automated tool is perfect. This catches known patterns and heuristics, but sophisticated or novel attacks may evade detection. Always practice defense in depth.

**Q: Can I trust this skill itself?**  
A: Yes - the source code is transparent, uses only safe pattern matching, and makes no external network calls except to fetch skills for analysis.

**Q: Does this replace VirusTotal?**  
A: No, it complements it. VirusTotal scans binaries, this analyzes skill logic and patterns.

**Q: What if I get a false positive?**  
A: Review the detailed findings. If you believe it's safe, you can whitelist it. Always err on the side of caution.

**Q: How often are patterns updated?**  
A: The community maintains an updated pattern database. Pull latest regularly with the update command.

## Support

- **Issues**: [GitHub Issues](https://github.com/openclaw/security-auditor/issues)
- **Community**: [OpenClaw Discord #security](https://discord.gg/openclaw)
- **Security Reports**: security@openclaw.ai (for vulnerabilities in this skill)

## Credits

Developed by **akm626** in response to the ClawHavoc campaign.

Based on research by:
- Koi Researcher (ClawHub malware discovery)
- OpenSourceMalware (6mile/Paul McCarty)
- Bitdefender Labs
- Palo Alto Networks

## License

MIT License - Use freely, contribute back improvements.

---

**Stay safe, stay skeptical, stay secure.** 🦞🛡️

*Version 1.0.0 | Last Updated: 2026-02-08*
