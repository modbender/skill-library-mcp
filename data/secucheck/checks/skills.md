# Skill Security Checks

## What to Examine

Run `gather_skills.sh` to get installed skills list.

## Check 1: Skill Source

**Categories**:

| Source | Trust Level | Notes |
|--------|-------------|-------|
| Builtin (OpenClaw) | 🟢 High | Shipped with OpenClaw |
| ClawHub (verified) | 🟢 Medium-High | Community reviewed |
| ClawHub (unverified) | 🟡 Medium | Use caution |
| Manual install | 🟡 Variable | Depends on source |
| Unknown origin | 🟠 Low | Investigate |

**Check for each user skill**:
- Is there a clear source/author?
- Was it installed via clawhub or manually copied?
- When was it last updated?

## Check 2: Skill Capabilities

**From SKILL.md, look for**:

| Capability | Risk Indicator |
|------------|----------------|
| `exec`, `shell`, `bash` | Runs system commands |
| `Write`, `Edit` | Modifies files |
| `browser` | Web browsing |
| `gateway` | Config modification |
| `cron` | Scheduling |
| `message` | External messaging |
| External API calls | Data exfiltration potential |

**Risk Matrix**:
```
Unknown source + exec capability = 🔴 Critical
Known source + exec capability = 🟡 Medium (review script contents)
Any source + read-only = 🟢 Low
```

## Check 3: Script Contents (Automated Scan)

For skills with scripts directory, actually scan file contents:

```bash
# Run on each script file in skill/scripts/
grep -l "curl\|wget" *.sh *.py *.js 2>/dev/null  # Network calls
grep -l "base64\|xxd\|od -x" *.sh 2>/dev/null     # Encoding (obfuscation)
grep -l "\.ssh\|\.aws\|\.config" *.sh 2>/dev/null  # Sensitive paths
grep -l "rm -rf\|mkfs\|dd if=" *.sh 2>/dev/null   # Destructive commands
```

**Red flags to report**:
| Pattern | Risk | Action |
|---------|------|--------|
| `curl/wget` + external URL | 🟡 Medium | Show the URL, let user decide |
| `base64 -d` in script | 🟠 High | Could hide malicious payload |
| Access to `~/.ssh`, `~/.aws` | 🟠 High | Credential theft risk |
| `rm -rf /` or similar | 🔴 Critical | Block immediately |
| Hardcoded IP addresses | 🟡 Medium | Potential C2 server |

**Do NOT flag**:
- `curl` to localhost or known APIs (github.com, api.openai.com, etc.)
- Standard package manager calls (npm, pip, apt)
- Example code in comments

## Check 4: Skill Metadata

If skill has `skill.json` or similar:

**Check for**:
- `minClawdVersion` - Compatibility
- `permissions` - Declared requirements
- `author`, `repository` - Traceability

**Missing metadata**: 🟡 Medium - Harder to audit

## Check 5: Skills Without Metadata

Skills missing `skill.json` or proper metadata:
- No version tracking
- No author/source info
- Harder to verify integrity

**Action**: ⚪ Info - Note for awareness, not a security issue per se

## Specific Skill Patterns

### Pattern A: Coding Helper
```
Skills that help with coding (happy, claude-code, etc.)
- Expected to have exec
- Focus on source trust
```

### Pattern B: Web Scrapers
```
Skills that fetch and process web content
- High injection surface
- Check if results go to exec
```

### Pattern C: Automation Skills
```
Skills that automate workflows
- Often need multiple powerful tools
- Verify each tool is necessary
```

## Recommendations by Finding

| Finding | Recommendation |
|---------|----------------|
| Unknown source skill | Review SKILL.md and scripts before use |
| Exec in web-related skill | Audit data flow carefully |
| No SKILL.md | Consider removing or replacing |
| Outdated skill | Check for updates on ClawHub |

## Auto-Review Trigger

When a new skill is installed:
1. Run `gather_skills.sh` 
2. Identify the new skill
3. Apply checks above to the new skill only
4. Report findings to user before first use
