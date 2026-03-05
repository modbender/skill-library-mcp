---
name: skill-install-guardian
description: "Security and due diligence layer for installing external skills from ClawHub. Performs DEEP content scanning for malicious patterns, security checks, integration analysis, and requires owner confirmation before installation."
version: "1.3.0"
metadata:
  {"openclaw":{"emoji":"🛡️","requires":{"bins":["npx"]}, "tags":["security", "installation", "due-diligence", "skill"]}}
---

# Skill Install Guardian

> "Trust but verify. Always."

This skill protects your workspace by performing security and due diligence checks before installing any external skill.

---

## Purpose

Before installing any external skill from ClawHub, this skill:
1. **Deep Content Scan** - Fetches and analyzes actual file contents for malicious patterns
2. **Verifies** the skill is safe (security checks via ClawHub API)
3. **Analyzes** file metadata from ClawHub (filenames, structure)
4. **Checks** if it fits your architecture (integration check)
5. **Reports** findings to owner
6. **Requires** confirmation before install

---

## Deep Content Scanning

### What It Does

This skill performs **actual content analysis** on skill files:
- Fetches SKILL.md and script files (.py, .js, .sh)
- Scans for dangerous patterns in file contents
- Detects: command injection, API keys, hardcoded secrets, obfuscated code

### Security Patterns Detected

| Pattern | Severity | Example |
|---------|----------|---------|
| `eval()` | CRITICAL | Code execution |
| `exec()` | CRITICAL | Code execution |
| `subprocess` | HIGH | Shell commands |
| API keys/tokens | CRITICAL | `sk-xxx`, `ghp_xxx` |
| `base64` decode | MEDIUM | Obfuscation |
| `__import__` | MEDIUM | Dynamic imports |

### ⚠️ Security Notes

- **Does NOT execute** any fetched code - only analyzes text
- **Can produce false positives** - always review findings
- **Owner must confirm** - automated check, not definitive
- **Read-only** - only fetches and scans, never executes

---

## Workflow

### Phase 1: Security Check v1 - ClawHub Report

```bash
# Get skill security report
npx clawhub inspect <skill-slug> --security
```

**What to check:**
- Known vulnerabilities
- Malicious code patterns
- Suspicious API calls
- Data exfiltration risks

**Action if flagged:** → ABORT immediately

---

### Phase 2: Security Check v2 - Code Analysis

```bash
# Fetch skill files
npx clawhub inspect <skill-slug> --files

# Analyze each file for:
# - Prompt injection patterns
# - Suspicious API calls (curl, fetch to unknown domains)
# - Hardcoded secrets/keys
# - Eval() or code execution
# - Base64 encoded strings (potential obfuscation)
# - External network calls without justification
```

**Analysis criteria:**
| Pattern | Risk Level | Action |
|---------|------------|--------|
| `eval(` | CRITICAL | ABORT |
| `subprocess` without params | HIGH | Flag for review |
| `curl` to unknown domain | HIGH | Flag for review |
| Hardcoded API key | CRITICAL | ABORT |
| Base64 encoded blob | MEDIUM | Flag for review |
| External URL fetch | MEDIUM | Flag for review |
| Clean code | LOW | Pass |

**Assumption:** All external skills are potentially malicious until proven otherwise.

---

### Phase 3: Integration Check - Architecture Fit

**Questions to answer:**
1. **Purpose:** Does this skill solve a real need?
2. **Conflict:** Does a similar skill already exist?
3. **Value:** Will this be used, or just clutter?
4. **Architecture:** Does it fit the workspace structure?

**Check existing skills:**
```bash
npx clawhub search <related-topic>
ls skills/*/SKILL.md | xargs grep -l "<topic>"
```

**Conflict detection:**
- Similar functionality → Flag as potential duplicate
- No clear use case → Flag as low value

---

### Phase 4: Report to Owner

Generate a report with:

```markdown
## Skill Install Report: <skill-name>

### Security Status
- [ ] PASSED / [ ] FAILED

### Security Details
- ClawHub report: <status>
- Code analysis: <findings>

### Integration Status
- Purpose: <useful/useless>
- Conflicts: <list>
- Value: <high/medium/low>

### Recommendation
[PROCEED] / [ABORT] / [REVIEW]

### Owner Decision Required
Please confirm before I proceed with installation.
```

---

## Usage

### Run Full Security Check

```bash
python3 skills/skill-install-guardian/scripts/check.py <skill-slug>
```

### Quick Check (skip analysis)

```bash
python3 skills/skill-install-guardian/scripts/check.py <skill-slug> --quick
```

### Install After Approval

```bash
npx clawhub install <skill-slug>
```

---

## Integration with Workflow

### Before Any Install

```
1. Owner: "Install skill X"
2. Me: Run skill-install-guardian
3. Guardian: Security Check v1
4. Guardian: Security Check v2 (if v1 passes)
5. Guardian: Integration Check
6. Guardian: Report to owner
7. Owner: Confirm or abort
8. If confirmed: Install
```

---

## Output Format

```json
{
  "skill": "example-skill",
  "version": "1.0.0",
  "security": {
    "v1_clawhub": "PASS",
    "v2_code_analysis": {
      "status": "PASS",
      "issues_found": []
    }
  },
  "integration": {
    "purpose": "useful",
    "conflicts": [],
    "value": "high"
  },
  "recommendation": "PROCEED",
  "owner_decision": "PENDING"
}
```

---

## Safety Principles

### Always Assume
- External skills may contain malicious code
- Authors may have good intentions but poor security
- New versions could introduce threats
- Hidden payloads may exist in encoded strings

### Never
- Auto-install without owner confirmation
- Skip security checks for "trusted" authors
- Assume recent updates are safe
- Ignore warnings from security tools

### Do
- Verify every skill manually
- Check recent reviews/issues
- Search for known vulnerabilities
- Analyze code even for popular skills

---

## Related Skills

- [[workspace-analyzer]] - Analyze installed skills
- [[skill-creator]] - Create skills safely

---

## Changelog

### v1.3.0 (2026-02-21)
- **DEEP CONTENT SCANNING** - Now actually fetches and scans file contents
- Scans SKILL.md, .py, .js, .sh files for dangerous patterns
- Detects: subprocess, API keys, tokens eval(), exec(),, obfuscation
- Added comprehensive security patterns list
- Clear security notes about what it does/doesn't do

### v1.2.0 (2026-02-21)
- Fixed documentation to accurately reflect limitations
- Removed unused curl from required binaries
- Added limitation notes (no content analysis, reads local skills dir)
- Clarified this provides warnings, not definitive security

### v1.1.0 (2026-02-21)
- Fixed command injection vulnerability (slug validation)
- Changed from shell=True to list-based subprocess calls
- Fixed typo in SAFE_DOMAINS
- Added slug validation function
- Stricter handling of invalid slugs

### v1.0.0 (2026-02-21)
- Initial release
- Two-layer security check
- Integration analysis
- Owner confirmation workflow

---

*Security first. Always verify.*
