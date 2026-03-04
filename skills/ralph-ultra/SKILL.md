---
name: ralph-ultra
description: "Deep-dive security audit with 1,000 iterations (~4-8 hours). Use when user says 'deep security audit', 'ralph ultra', 'compliance audit prep', 'thorough security review', 'before major release', or 'security incident investigation'. Covers OWASP deep dive, supply chain, compliance, business logic, 4 expert personas."
metadata: { "openclaw": { "emoji": "⚔️" }, "author": "dorukardahan", "version": "2.0.0", "category": "security", "tags": ["security", "audit", "deep-dive", "compliance", "owasp"] }
---

# Ralph Ultra — 1,000 Iterations (~4-8 hours)

Deep-dive security audit with thorough coverage across all attack vectors.

## References

- [Severity and triage guidance](references/severity-guide.md)
- [Expert persona descriptions](references/personas.md)

## Instructions

### Execution Engine

YOU MUST follow this loop for EVERY iteration:

1. **STATE**: Read current iteration (start: 1)
2. **PHASE**: Determine phase from iteration number
3. **MIND**: Activate appropriate expert persona for phase
4. **ACTION**: Perform ONE check from current phase
5. **VERIFY**: Before FAIL — read actual code, check libraries, check DB constraints, check environment. If inconclusive: `NEEDS_REVIEW`.
6. **REPORT**: Output iteration result
7. **SAVE**: Every 50 iterations, update `.ralph-report.md`
8. **INCREMENT**: iteration + 1
9. **CONTINUE**: IF iteration <= 1000 GOTO Step 1
10. **FINAL**: Generate comprehensive report

**Critical rules:**
- ONE check per iteration — deep, not wide
- ALWAYS show `[ULTRA-X/1000]`
- NEVER skip iterations
- CRITICAL findings: immediately flag
- Apply Red Team mindset to EVERY check

### Per-Iteration Output

```
╔══════════════════════════════════════════════════════════════════╗
║ [ULTRA-{N}/1000] Phase {P}: {phase_name}                        ║
║ Mind: {active_expert_persona}                                    ║
╠══════════════════════════════════════════════════════════════════╣
║ Check: {specific_check}                                          ║
║ Target: {file:line / endpoint / system}                          ║
╠══════════════════════════════════════════════════════════════════╣
║ Result: {PASS|FAIL|WARN|N/A}                                     ║
║ Confidence: {VERIFIED|LIKELY|PATTERN_MATCH|NEEDS_REVIEW}         ║
║ Severity: {CRITICAL|HIGH|MEDIUM|LOW|INFO}                        ║
║ CVSS: {score}                                                    ║
╠══════════════════════════════════════════════════════════════════╣
║ Finding: {detailed description}                                  ║
║ Exploit: {proof of concept or "N/A"}                             ║
║ Fix: {specific remediation}                                      ║
╠══════════════════════════════════════════════════════════════════╣
║ Progress: [████████████░░░░░░░░] {N/10}%                         ║
║ Phase: {current}/{8} | ETA: ~{time} remaining                    ║
╚══════════════════════════════════════════════════════════════════╝
```

### Expert Personas

| Phase | Persona |
|-------|---------|
| 1, 3, 7 | Cybersecurity Veteran |
| 2, 5 | Code Auditor (Pentester) |
| 4 | Container Security Expert |
| 6 | Dependency Hunter |
| 8 | All Minds |

Full persona descriptions in [references/personas.md](references/personas.md).

### Phase Structure (1,000 Iterations)

| Phase | Iterations | Focus Area |
|-------|------------|------------|
| 1 | 1-100 | Reconnaissance & Attack Surface |
| 2 | 101-250 | OWASP Top 10 Deep Dive |
| 3 | 251-400 | Authentication & Secrets |
| 4 | 401-550 | Infrastructure & Containers |
| 5 | 551-700 | Code Quality & Business Logic |
| 6 | 701-850 | Supply Chain & Dependencies |
| 7 | 851-950 | Compliance & Documentation |
| 8 | 951-1000 | Final Verification & Report |

### Phase 1: Reconnaissance (1-100)

- **1-20:** Platform sync — auto-detect stack, git sync, hash verification, environment drift
- **21-50:** Attack surface — endpoint enumeration, auth mapping, rate limits, exposed ports, WebSocket/SSE
- **51-75:** Hidden systems — undeclared services, cron jobs, orphan configs, Docker networks
- **76-100:** Environment & docs — variable audit, .env drift, documentation accuracy, scoring

### Phase 2: OWASP Top 10 (101-250)

| Iter | OWASP | Focus |
|------|-------|-------|
| 101-120 | A01 | Broken Access Control (IDOR, CORS, path traversal) |
| 121-140 | A02 | Cryptographic Failures (algorithms, keys, TLS) |
| 141-170 | A03 | Injection (SQL, Command, XSS, Template, Log) |
| 171-185 | A04 | Insecure Design (missing controls, business logic) |
| 186-200 | A05 | Security Misconfiguration (debug, errors, headers) |
| 201-215 | A06 | Vulnerable Components (dependency audit) |
| 216-230 | A07 | Auth Failures (credential stuffing, sessions) |
| 231-240 | A08 | Integrity Failures (deserialization, CI/CD) |
| 241-245 | A09 | Logging Failures |
| 246-250 | A10 | SSRF |

### Phase 3: Authentication & Secrets (251-400)

**Pre-check:** Determine library vs custom crypto before flagging.

- **251-300:** Secret detection (API keys, passwords, git history)
- **301-340:** JWT security (algorithm, claims, storage, revocation)
- **341-365:** OAuth 2.0 (PKCE, redirect URI, state, token exchange)
- **366-385:** Admin authentication (brute force, timing, lockout)
- **386-400:** Rate limiting (coverage, bypass)

### Phase 4: Infrastructure (401-550)

- **401-450:** Container security (non-root, readonly, capabilities, limits)
- **451-490:** Network security (ports, firewall, isolation, egress)
- **491-515:** TLS/SSL (cert validity, ciphers, HSTS)
- **516-535:** SSH security (key auth, config hardening)
- **536-550:** Database security (SSL, permissions, backups)

### Phase 5: Code Quality (551-700)

**Pre-check:** Check database constraints before flagging race conditions.

- **551-590:** Race conditions (TOCTOU, concurrent access, locks)
- **591-630:** Business logic (workflow bypass, state manipulation)
- **631-660:** Error handling (safe messages, fail-safe defaults)
- **661-690:** Resource management (connections, memory, DoS)
- **691-700:** Complexity attacks (ReDoS, JSON bombs)

### Phase 6: Supply Chain (701-850)

- **701-750:** Dependency audit (CVEs, outdated, typosquatting)
- **751-790:** Third-party API security (keys, webhooks, rate limits)
- **791-820:** Container supply chain (base images, signatures)
- **821-850:** CI/CD security (secrets, permissions, pinned actions)

### Phase 7: Compliance (851-950)

- **851-885:** Privacy compliance (GDPR, data retention, consent)
- **886-915:** Security documentation (incident response, policies)
- **916-935:** Operational security (access control, change mgmt)
- **936-950:** Audit trail (logging completeness, retention)

### Phase 8: Final Verification (951-1000)

- **951-970:** Critical findings re-verification
- **971-985:** Penetration test simulation
- **986-995:** Security scorecard generation
- **996-1000:** Final report and summary

### Auto-Detect (Iteration 1)

1. `git rev-parse --show-toplevel`, `git remote -v`
2. Stack: `package.json`, `pyproject.toml`, `requirements.txt`, `go.mod`, `Cargo.toml`
3. Infra: `Dockerfile`, `docker-compose.yml`, k8s manifests, terraform
4. CI/CD: `.github/workflows`, `.gitlab-ci.yml`, `.circleci`

### Report File

On start: rename existing report. Auto-save every 50 iterations.

### Parameters

| Param | Default | Options |
|-------|---------|---------|
| `--iterations` | 1000 | 1-2000 |
| `--focus` | all | recon, owasp, auth, infra, code, supply-chain, compliance, all |
| `--phase` | all | 1-8 |
| `--resume` | — | Continue from checkpoint |

### Context Limit Protocol

Checkpoint to `.ralph-report.md`, output resume command, wait for new session.

### When to Use

- Before major release
- Compliance audit preparation
- Security incident investigation
- Deep dive after `/ralph-security` flags issues
