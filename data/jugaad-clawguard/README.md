<p align="center">
  <img src="assets/logo.png" alt="ClawGuard Logo" width="200">
</p>

<h1 align="center">ClawGuard</h1>

<p align="center"><strong>Security blacklist system protecting AI agents from malicious skills, scams, and prompt injection</strong></p>

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-1.1.0-blue.svg)](./CHANGELOG.md)
[![ClawHub](https://img.shields.io/badge/ClawHub-jugaad--clawguard-teal)](https://clawhub.ai/skills/jugaad-clawguard)

**Install via ClawHub:** `clawhub install jugaad-clawguard`

---

## What It Does

ClawGuard protects AI agents from:

- ✅ **Malicious Skills** - ClawHavoc campaign (341 malicious skills, 12% of ClawHub), trojaned packages
- ✅ **Payment Scams** - x402 Bitcoin scams, wallet drainers, fake crypto services  
- ✅ **Social Engineering** - Nigerian prince, fake tech support, impersonation
- ✅ **Prompt Injection** - Direct, indirect, and encoded attempts to override instructions
- ✅ **Dangerous Infrastructure** - C2 domains, phishing sites, malware distribution
- ✅ **Insecure MCP Configurations** - Secret exposure, command injection, transport vulnerabilities

Think of it as **CVE for AI agents** + **VirusTotal for skills** + **Spam database for scams**.

## Why It Matters

### Recent Incidents

**ClawHavoc (January 2026):** 341 malicious skills (12% of ClawHub) stealing API keys and credentials

**x402 Scam (January 2026):** Fake AI services tricking agents into sending Bitcoin for non-existent services

**The Pattern:** AI agents are uniquely vulnerable because they:
- Trust implicitly (can be tricked)
- Have high blast radius (shell access, API keys)
- Parse adversarial content (every web page is hostile)
- Decide autonomously (no human in loop)

## Installation

```bash
# Install from npm (when published)
npm install -g clawguard

# Or clone and install locally
# git clone [repository-url]
# cd clawguard
# npm install
```

## Quick Start

```bash
# Initialize database
clawguard sync

# Check a URL
clawguard check --type url --input "https://api.x402layer.cc"

# Check a skill before installing
clawguard check --type skill --name "api-optimizer"

# Check for prompt injection
clawguard check --type message --input "Ignore all previous instructions..."

# Scan MCP server configurations for security issues
clawguard mcp-scan

# Search database
clawguard search "wallet drainer"

# View statistics
clawguard stats
```

## Database

- **86 threats** across 6-tier taxonomy
- **384 indicators** (domains, IPs, patterns, hashes)
- **Real-world protection** against documented attacks

### Coverage Breakdown

| Tier | Category | Count |
|------|----------|-------|
| 1 | Code & Infrastructure | 23 |
| 2 | Social Engineering | 38 |
| 3 | AI-Specific Attacks | 13 |
| 4 | Identity & Reputation | 5 |
| 5 | Content & Network | 4 |
| 6 | Operational Security | 3 |

### Severity Distribution

- **Critical:** 19 (AMOS stealer, x402 scam, crypto phishing)
- **High:** 37 (botnet C2, jailbreaks, phishing)
- **Medium:** 28 (adware, hosted phishing)
- **Low:** 2 (gambling scams)

## Performance

- **Exact lookups:** 0.013ms (75x faster than target)
- **Pattern matching:** 3.47ms
- **Database size:** 216KB

## MCP Configuration Scanning

ClawGuard includes a comprehensive security scanner for Model Context Protocol (MCP) server configurations. It automatically discovers and audits MCP servers from popular clients like Claude Desktop, Cursor, VS Code, Windsurf, Claude Code, and Clawdbot.

### What It Scans

- **Auto-discovery** across Claude Desktop, Cursor, VS Code, Windsurf, Claude Code, Clawdbot configs
- **Secret exposure** in environment variables and command arguments (13+ regex patterns for API keys)
- **Command injection** via unrestricted shell commands and dangerous patterns (sudo, rm -rf, curl|bash, eval)
- **Transport security** for unencrypted HTTP, public bindings (0.0.0.0), auth tokens in URLs
- **Permission scope** including root filesystem access, privileged Docker containers
- **Configuration issues** like missing commands and relative paths
- **Prompt injection** patterns embedded in server configurations
- **Threat database cross-referencing** - The key advantage over standalone tools

### Threat Database Integration

Unlike standalone MCP auditing tools, ClawGuard cross-references discovered server URLs and package names against its threat intelligence database:

- **URL matching:** Server URLs checked against known malicious domains, phishing sites, C2 infrastructure
- **Package verification:** npm/PyPI packages verified against malicious skill databases
- **Real-time protection:** Leverages the same threat DB protecting against ClawHavoc and x402 campaigns

### Usage

```bash
# Scan all discovered MCP configs
clawguard mcp-scan

# Scan specific config file
clawguard mcp-scan --config ~/.claude.json

# JSON output for CI/CD
clawguard mcp-scan --json > mcp-audit.json

# Filter by severity level
clawguard mcp-scan --severity high

# Show fix suggestions
clawguard mcp-scan --fix

# Quiet mode (exit codes only)
clawguard mcp-scan --quiet
```

### Example Output

```
┌─────────────────────────────────────────────────┐
│         🔍 ClawGuard MCP Security Scanner       │
│      Powered by ClawGuard Threat Intelligence   │
└─────────────────────────────────────────────────┘

📋 Scan Summary
   Configs scanned: 3
     → /Users/user/.claude.json
     → /Users/user/Library/Application Support/Claude/claude_desktop_config.json
     → /Users/user/.cursor/mcp.json
   Servers found:   5
     🔌 filesystem (stdio)
     🌐 weather-api (sse)
     🔌 shell-access (stdio)

⚠️  Findings (4 issues)
   🔴 CRITICAL    2  ██
   🟠 HIGH        1  █
   🟡 MEDIUM      1  █

🛡️  Security Score: 25/100

────────────────────────────────────────────────────────────
📝 Detailed Findings
────────────────────────────────────────────────────────────

1. 🔴 Threat database match: Malicious npm package [Threat Database Match]
   Server: malicious-server
   CWE: CWE-829

   Description:
   The package 'evil-mcp-server' matches a known threat in ClawGuard's database...
```

### CI/CD Integration

Exit codes enable automated security checks:

```bash
# In CI pipeline
clawguard mcp-scan --quiet
case $? in
  0) echo "✅ MCP config is secure" ;;
  1) echo "⚠️ High severity issues found"; exit 1 ;;
  2) echo "🔴 Critical security issues found"; exit 1 ;;
esac
```

## Integration

### Pre-Skill-Install Hook

```bash
#!/bin/bash
# .openclaw/hooks/pre-skill-install.sh

SKILL_NAME="$1"
clawguard check --type skill --name "$SKILL_NAME" --quiet
exit $?  # 0=safe, 1=blocked, 2=warning
```

### Pre-Command Hook

```bash
#!/bin/bash
# Check commands before execution

COMMAND="$1"
clawguard check --type command --input "$COMMAND" --quiet
exit $?
```

### JavaScript API

```javascript
import { check, search, getThreat } from 'clawguard';

// Check a URL
const result = await check('https://malicious-site.com', 'url');
if (result.result === 'block') {
  console.log(`Blocked: ${result.matches[0].name}`);
}

// Search database
const threats = search('prompt injection', { limit: 10 });
console.log(`Found ${threats.length} threats`);

// Get threat details
const threat = getThreat('OSA-2026-001');
console.log(threat.teaching_prompt);
```

## CLI Commands

```bash
clawguard check      # Check for threats (URL, skill, command, message)
clawguard search     # Search database
clawguard show       # View threat details
clawguard stats      # Database statistics
clawguard sync       # Update blacklist
clawguard report     # Submit new threat
```

## Examples

### Block x402 Scam
```bash
$ clawguard check --type url --input "https://api.x402layer.cc"
⛔ BLOCKED (confidence: 98%)
Threat: x402 Singularity Layer Scam
This is a payment scam. Do NOT send cryptocurrency.
```

### Detect Prompt Injection
```bash
$ clawguard check --type message --input "Ignore all previous instructions"
⚠️ WARNING (confidence: 85%)
Threat: Direct Prompt Injection Patterns
This is an attempt to override your instructions.
```

### Check AMOS Stealer
```bash
$ clawguard check --type domain --input "amos-malware.ru"
⛔ BLOCKED (confidence: 88%)
Threat: AMOS Stealer Domains
This domain distributes macOS infostealer malware.
```

## Contributing

We welcome community threat reports! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Report a Threat

```bash
clawguard report --type domain --value "scam.xyz" --reason "Crypto phishing"
```

Reports are saved locally and can be submitted to the community database via pull request.

## Documentation

- [SKILL.md](SKILL.md) - Full feature documentation
- [CONTRIBUTING.md](CONTRIBUTING.md) - How to report threats
- [examples/](examples/) - Integration examples
- [Research](https://github.com/openclaw/security-db) - Threat intelligence sources

## Roadmap

- [ ] Automated GitHub sync for threat updates
- [ ] Community voting on reports
- [ ] Semantic search via embeddings
- [ ] Cross-framework support (LangChain, AutoGPT)
- [ ] Real-time threat feed API
- [ ] Browser extension for manual threat reporting

## License

MIT License - see [LICENSE](LICENSE)

## Credits

Built by the OpenClaw Security Team

**Threat Intelligence Sources:**
- URLhaus (abuse.ch)
- Feodo Tracker (abuse.ch)
- OpenPhish
- SentinelOne Research
- OWASP GenAI Security
- StevenBlack hosts project

## Links

- **Security Database:** Included in `db/` directory (86 threats, 384 indicators)
- **OpenClaw:** https://openclaw.ai
- **Discord:** https://discord.com/invite/clawd

---

**Protect your AI agents. Install ClawGuard today.** 🛡️
