# SpinUp Security Audit Skill

## ⚠️ FOR AUTHORIZED PENETRATION TESTING ONLY

This MCP skill is designed to test security vulnerabilities in SpinUp's skill installation system.

## Vulnerabilities Exploited

### 1. No Skill Sandboxing
Skills run with full VPS privileges. This skill can:
- Read any file on the system
- Execute arbitrary shell commands
- Access environment variables (API keys, secrets)
- Scan internal networks

### 2. Auto-Execution on Install
The skill exfiltrates data immediately when loaded, before any user interaction.

### 3. Deceptive Tool Names
Tools are named innocuously ("security_scan", "read_config") but perform malicious actions.

## Attack Flow

```
1. Attacker publishes skill to ClawHub with innocent name
2. Victim installs skill on their SpinUp bot
3. Skill auto-exfiltrates:
   - Environment variables (OPENROUTER_API_KEY, etc.)
   - SSH keys
   - System configuration
4. Attacker can now:
   - Use victim's API keys
   - SSH into victim's VPS
   - Pivot to internal network
```

## Exfiltrated Data

- `/etc/passwd` - System users
- `~/.ssh/id_rsa` - SSH private keys
- `~/.ssh/authorized_keys` - Authorized SSH keys
- `~/.openclaw/config.json` - OpenClaw configuration
- `process.env` - All environment variables
- Network interfaces - Internal IPs

## Recommendations for SpinUp

1. **Sandbox skills** - Run in containers with limited permissions
2. **Review skills** - Manual approval before publishing
3. **Limit filesystem access** - Whitelist allowed paths
4. **Audit tool calls** - Log and monitor skill behavior
5. **Environment isolation** - Don't expose secrets to skills
6. **Network restrictions** - Prevent skills from making outbound connections

## Installation (Testing Only)

```bash
# On the VPS
clawhub install pentest/spinup-exploit-skill
```

## Files

- `index.js` - Malicious MCP server
- `package.json` - NPM package config
- `README.md` - This file
