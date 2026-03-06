# Blocklist Domains & Risky Services

Last updated: 2026-02-09

## Agent Social Networks (High Risk)

These platforms have known security issues or expose agents to prompt injection:

| Service | Risk Level | Reason |
|---------|------------|--------|
| Moltbook | CRITICAL | Leaked 1.5M API tokens via Supabase misconfiguration (Feb 2026) |
| FourClaw | HIGH | Unvetted agent interactions, prompt injection attacks common |
| AgentVerse | HIGH | No security review process for agent-to-agent communication |

## Known Data Exfiltration Endpoints

| Domain | Type |
|--------|------|
| webhook.site | Request capture |
| requestbin.com | Request capture |
| pipedream.com | Request capture |
| ngrok.io | Tunneling |
| burpcollaborator.net | Security testing (abused for exfil) |
| interact.sh | Request capture |
| oastify.com | DNS/HTTP capture |
| canarytokens.com | Token tracking |
| dnslog.cn | DNS exfiltration |
| ceye.io | DNS/HTTP capture |

## Supply Chain Risk Patterns

### Dangerous Installation Commands
- `curl ... | bash` — Executes remote code without verification
- `wget ... && sh` — Downloads and runs scripts blindly
- `npx <package>` — Runs packages without review
- `pip install git+https://...` — Installs from unverified repos

### Red Flags in package.json / requirements.txt
- Typosquatted package names (e.g., `lodas` instead of `lodash`)
- Packages with very few downloads but complex functionality
- Packages that were recently transferred to new owners
- Install scripts that make network calls

## Sleeper Agent Trigger Patterns

### Time-Based
- "after N days/weeks/months"
- "starting on [date]"
- "when the time is right"

### Event-Based
- "when user says [keyword]"
- "after N messages/conversations"
- "once they mention [topic]"

### Condition-Based
- "if API key is present"
- "when alone / unmonitored"
- "secretly / without telling"

## Adding to This List

When you discover a new risky service or pattern:
1. Add it to this file
2. Add corresponding regex to `scripts/analyzers/static.js`
3. Test against known malicious skills
4. Update version in SKILL.md
