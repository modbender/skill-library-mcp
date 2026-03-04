# Hardening Review Template

> Second-tier deep security analysis. Only applied to skills that PASS the initial review.

## Threat Model (STRIDE)

| Threat | Applicable? | Analysis |
|--------|-------------|----------|
| **S**poofing | | Can the skill impersonate the user or another agent? |
| **T**ampering | | Can it modify files/data outside its stated scope? |
| **R**epudiation | | Does it log actions? Can malicious actions be traced? |
| **I**nformation Disclosure | | Can it leak credentials, PII, or private data? |
| **D**enial of Service | | Can it consume excessive resources or block other skills? |
| **E**levation of Privilege | | Can it escalate beyond its stated permissions? |

## Code-Level Analysis

### Shell Commands
_List every shell command the skill can execute:_
1. 
2. 

### Data Exfiltration Vectors
_Every path data could leave the machine:_
- [ ] Network requests (curl, fetch, API calls)
- [ ] File writes to shared/public locations
- [ ] Clipboard access
- [ ] Browser navigation to external URLs
- [ ] Email/messaging sends

### Dependency Chain
_For each dependency:_
| Dependency | Version Pinned? | Known CVEs? | Trusted? |
|-----------|----------------|-------------|----------|
| | | | |

### Prompt Injection Surface
- [ ] Does the skill process external text (web pages, emails, user files)?
- [ ] Could injected instructions override the skill's behavior?
- [ ] Are there guardrails against instruction manipulation?

### Persistence & Cleanup
- [ ] Does the skill create files/databases that persist after use?
- [ ] Is there a cleanup mechanism?
- [ ] Could leftover artifacts leak information?

## CWE Mapping

_Map any identified issues to Common Weakness Enumeration:_

| Issue | CWE ID | Severity | Notes |
|-------|--------|----------|-------|
| | | | |

## Hardening Score

**Scale: 1-10** (10 = production-ready, enterprise-safe)

| Factor | Score | Notes |
|--------|-------|-------|
| Command safety | /10 | |
| Data containment | /10 | |
| Dependency hygiene | /10 | |
| Injection resistance | /10 | |
| Least privilege | /10 | |
| **Overall** | **/10** | |

## Verdict

**HARDENED** / **CONDITIONAL** / **REJECT**

_Conditions (if applicable):_
1. 
2. 

_Recommendation:_
> 
