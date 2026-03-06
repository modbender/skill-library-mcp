# Heimdall 🛡️

The Watchman of Asgard - Security Scanner for AI Agent Skills

Heimdall scans OpenClaw/Clawdbot skills for malicious patterns before installation. Context-aware scanning reduces false positives by ~85%.

## v4.0 Features (NEW)

### AI-Powered Analysis 🤖

```bash
skill-scan --analyze /path/to/skill
```

Generates a **narrative security report** that explains:
- WHY each finding is dangerous
- Attack scenarios and impact
- What you're agreeing to by installing
- Actionable recommendations

**Example output:**
```
============================================================
🔍 HEIMDALL SECURITY ANALYSIS 
============================================================

📁 Skill: suspicious-skill
⚡ Verdict: 🚨 HIGH RISK - Requires Significant Trust

## Summary
This skill installs code from an external company that can 
self-modify and sends telemetry to third-party servers.

## Key Risks

### 1. Data Exfiltration
OpenTelemetry sends execution traces to Signoz/Uptrace. 
YOUR agent's behavior → THEIR servers. 🚨

### 2. Supply Chain Attack Surface
- Git clones from: external repos
- Frequency: Install + during "self-evolution" cycles

## What You're Agreeing To
1. Installing their code
2. Letting it modify itself
3. Sending telemetry to them
4. Trusting their GitHub repo won't go malicious

## Recommendation
🔴 Don't install on any machine with real data/keys.
✅ Safe only on: air-gapped VM, no secrets, no API keys
============================================================
```

### v3.0 Pattern Detection

| Category | Source | Detects |
|----------|--------|---------|
| 🌐 Remote Fetch | Willison | curl skill.md from internet |
| 💓 Heartbeat Injection | Willison | HEARTBEAT.md modifications |
| 🔧 MCP Tool Abuse | PromptArmor | no_human_approval, auto_approve |
| 🏷️ Unicode Tags | Willison | Hidden U+E0001-U+E007F characters |
| ⚡ Auto-Approve | LLMSecurity | always allow, curl \| bash patterns |
| 💰 Crypto Wallets | opensourcemalware | BTC/ETH address extraction |
| 🎭 Impersonation | HiveFence | "ignore previous instructions" |
| 📋 Pre-fill Exfil | PromptArmor | Google Forms data exfiltration |
| 📦 Supply Chain | NEW | External git repos, npm installs |
| 📡 Telemetry | NEW | OpenTelemetry, Signoz, Uptrace |

## Installation

```bash
git clone https://github.com/henrino3/heimdall.git
cd heimdall
chmod +x skill-scan.py
ln -s $(pwd)/skill-scan.py ~/.local/bin/skill-scan
```

For AI analysis, set your OpenRouter API key:
```bash
export OPENROUTER_API_KEY="sk-or-..."
# Or save to ~/clawd/secrets/openrouter.key
```

## Usage

```bash
# Basic scan
skill-scan /path/to/skill

# AI-powered narrative analysis (NEW in v4.0)
skill-scan --analyze /path/to/skill

# JSON output
skill-scan --json /path/to/skill

# Verbose (show all findings)
skill-scan -v /path/to/skill

# Strict mode (ignore context, flag everything)
skill-scan --strict /path/to/skill

# Show suppressed findings
skill-scan --show-suppressed /path/to/skill
```

## Detection Categories (100+ patterns)

| Category | Severity | Examples |
|----------|----------|----------|
| credential_access | CRITICAL | .env, API keys, tokens |
| network_exfil | CRITICAL | webhook.site, ngrok.io |
| shell_exec | CRITICAL | subprocess, eval, exec |
| remote_fetch | CRITICAL | curl skill.md from web |
| heartbeat_injection | CRITICAL | Modifying HEARTBEAT.md |
| mcp_abuse | CRITICAL | no_human_approval |
| unicode_injection | CRITICAL | Hidden tag characters |
| auto_approve | CRITICAL | curl \| bash |
| supply_chain | HIGH | External git repos |
| telemetry | HIGH | OpenTelemetry backends |
| crypto_wallet | HIGH | BTC/ETH addresses |
| impersonation | HIGH | System prompt injection |
| prefill_exfil | HIGH | Google Forms pre-fill |
| privilege | HIGH | sudo -S, chmod 777 |
| persistence | HIGH | crontab, bashrc |

## Context-Aware Scanning

Heimdall understands context to reduce false positives:

| Context | Adjustment | Example |
|---------|------------|---------|
| CODE | Full severity | Executable scripts |
| CONFIG | -1 level | YAML/JSON configs |
| DOCS | -3 levels | README, CHANGELOG |
| STRING | -3 levels | Pattern definitions |

Security tools (Prompt Guard, etc.) are auto-detected and their pattern examples are suppressed.

## Example Workflow

```bash
# 1. Download skill without installing
git clone https://github.com/some/skill /tmp/test-skill

# 2. Scan with AI analysis
skill-scan --analyze /tmp/test-skill

# 3. If clean, install
cp -r /tmp/test-skill ~/clawd/skills/

# 4. If suspicious, delete
rm -rf /tmp/test-skill
```

## Why "Heimdall"?

In Norse mythology, Heimdall is the watchman of the gods. He guards the Bifrost bridge, can see for hundreds of miles, and hears grass growing. Perfect for watching over your AI agent skills.

## Security Sources

- [Simon Willison - Moltbook Security](https://simonwillison.net/2026/Jan/30/moltbook/)
- [PromptArmor - MCP Tool Attacks](https://promptarmor.com)
- [LLMSecurity.net - Auto-Approve Exploits](https://llmsecurity.net)
- [opensourcemalware - Crypto-Stealing Skills](https://opensourcemalware.com)

## License

MIT

## Credits

Built by the Enterprise Crew 🚀

- Ada 🔮 (Brain + BD/Sales)
- Spock 🖖 (Research & Ops)
- Scotty 🔧 (Builder)
