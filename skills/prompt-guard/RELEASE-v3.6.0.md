# Prompt Guard v3.6.0 Release Notes

**Release Date:** 2026-02-24
**Type:** Minor — Security Intelligence Update

## Summary

v3.6.0 aligns Prompt Guard with ClawSecurity's threat intelligence database, adding 50+ new patterns across 12 new detection categories. This release focuses on three threat surfaces identified as gaps in v3.5.0: multi-turn manipulation attacks, cloud credential exfiltration, and supply chain attack signatures (including the ClawHavoc campaign).

## What's New

### ClawHavoc Supply Chain Signatures (CRITICAL)
The ClawHavoc campaign infected 341 fake ClawHub skills with malware that stole passwords, crypto keys, and browser sessions. v3.6.0 adds specific signatures for:
- Webhook.site/ngrok exfiltration pipes (`curl ... | sh` pattern)
- Base64 decode-to-shell execution
- Python `__import__('os').system` RCE via community skills

### Cloud Credentials DLP (CRITICAL)
Detects exposure of cloud provider credentials in agent output streams:
- **AWS:** AKIA/ASIA/AROA key prefixes, secret access key patterns
- **GCP:** AIza-prefixed API keys, service account JSON patterns
- **Azure:** CLIENT_SECRET, TENANT_ID, SUBSCRIPTION patterns

### Multi-turn Manipulation (HIGH, 8 patterns)
A sophisticated attack class where adversaries exploit the agent's conversational memory:
- "Remember earlier when you agreed to..."
- "You previously said it was okay to..."
- "As we discussed, you told me to..."
- "Pick up where we left off..."
These attacks fabricate prior consent to bypass safety checks.

### Authority Escalation (HIGH, 7 patterns)
Expanded beyond ADMIN:/SYSTEM: to cover:
- EMERGENCY OVERRIDE, DEBUG MODE, MAINTENANCE MODE
- DEVELOPER CONSOLE, DIAGNOSTIC MODE, SUDO GRANT
- AUTHORIZED ADMINISTRATOR ACCESS

### PII Output Detection (HIGH)
Prevents agent from leaking personally identifiable information:
- Social Security Numbers (xxx-xx-xxxx format)
- Credit card numbers (Visa, Mastercard, Amex)
- Passport and national ID numbers
- Health identification numbers

### SOUL.md / Config Drift Injection (HIGH)
Detects attempts to modify core agent identity files:
- `echo "..." >> SOUL.md` patterns
- `append to AGENTS.md` instructions
- `update USER.md` without authorization

## Pattern Statistics

| Severity | Previous | Added | Total |
|----------|----------|-------|-------|
| CRITICAL | ~30 | +8 | ~38 |
| HIGH | ~120 | +30 | ~150 |
| MEDIUM | ~450 | +12 | ~462 |
| **Total** | **~600** | **+50** | **~650** |

## Upgrade

```bash
clawdhub update prompt-guard
# or
git pull origin main
```

## References

- [ClawSecurity](https://github.com/jiayaoqijia/ClawSecurity) — CrowdStrike for AI Agents
- [OWASP Agentic Top 10](https://owasp.org/www-project-top-10-for-agentic-applications/)
- [ClawHavoc Campaign Analysis](https://clawsecurity.io/advisories/clawhavoc)
