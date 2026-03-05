# Skill Review Template

> For use by the isolated review agent. Fill in all sections.

## Skill Info

- **Name:** 
- **Author:** 
- **Source:** ClawHub / GitHub
- **Source URL:** 
- **Version:** 
- **Review Date:** 

---

## Plain English Summary

_What does this skill do in one sentence a non-technical person would understand?_

> 

## What It Claims To Do

_List the skill's stated capabilities from its description/SKILL.md:_

1. 
2. 
3. 

## What It Actually Does (Code Analysis)

_Based on reading the source code, what does this skill actually do?_

1. 
2. 
3. 

### Claims vs Reality Match: ✅ Match / ⚠️ Partial / ❌ Mismatch

---

## Security Analysis

### Permissions Required
_What access does this skill need?_

- [ ] File read
- [ ] File write
- [ ] Shell execution
- [ ] Network/API access
- [ ] Browser control
- [ ] System commands
- [ ] Credential access
- [ ] Other: ___

### Risk Flags

| Flag | Found? | Details |
|------|--------|---------|
| eval()/exec() calls | ☐ | |
| External data transmission | ☐ | |
| Obfuscated code | ☐ | |
| Credential harvesting | ☐ | |
| Excessive permissions | ☐ | |
| Unvetted dependencies | ☐ | |
| Hidden network calls | ☐ | |
| Prompt injection patterns | ☐ | |

### Data Flow
_Where does data go? Does anything leave the local machine?_

> 

---

## Quality Assessment

| Criteria | Score (1-5) | Notes |
|----------|-------------|-------|
| Documentation quality | | |
| Code clarity | | |
| Error handling | | |
| Usefulness | | |
| Uniqueness (vs alternatives) | | |

---

## Trust Score

**🟢 Safe** / **🟡 Caution** / **🔴 Avoid**

_Reasoning:_

> 

---

## Category

**Primary:** 
**Tags:** 

---

## Install

```bash
npx clawhub@latest install {skill-name}
```

Or manual: copy to `~/.openclaw/skills/{skill-name}/`

---

## Verdict

_Would you recommend this skill to a new OpenClaw user? Why or why not?_

> 
