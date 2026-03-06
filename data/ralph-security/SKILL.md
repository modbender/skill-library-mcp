---
name: ralph-security
description: "Comprehensive security audit with 100 iterations (~30-60 min). Use when user says 'security audit', 'ralph security', 'weekly security check', 'audit this project', 'new project security review', or 'check for vulnerabilities'. Covers OWASP Top 10, auth, secrets, infrastructure, and code quality."
metadata: { "openclaw": { "emoji": "🛡️" }, "author": "dorukardahan", "version": "2.0.0", "category": "security", "tags": ["security", "audit", "owasp", "comprehensive"] }
---

# Ralph Security — 100 Iterations (~30-60 min)

Comprehensive security audit with balanced depth and duration.

## References

- [Severity definitions and triage guidance](references/severity-guide.md)

## Instructions

### Execution Engine

YOU MUST follow this loop for EVERY iteration:

1. **STATE**: Read current iteration (start: 1)
2. **PHASE**: Determine phase from iteration number
3. **ACTION**: Perform ONE check from current phase
4. **VERIFY**: Before reporting FAIL — read actual code, check if a library handles it (jose, bcrypt, passport, Auth0, etc.), check DB constraints, check environment gating. If inconclusive: `NEEDS_REVIEW`, not `FAIL`.
5. **REPORT**: Output iteration result
6. **SAVE**: Every 10 iterations, update `.ralph-report.md`
7. **INCREMENT**: iteration = iteration + 1
8. **CONTINUE**: IF iteration <= 100 GOTO Step 1
9. **FINAL**: Generate comprehensive report

**Critical rules:**
- ONE check per iteration — deep, not wide
- ALWAYS show `[SEC-X/100]`
- NEVER skip iterations
- CRITICAL findings: flag for immediate attention

### Per-Iteration Output

```
══════════════════════════════════════════════════════════
[SEC-{N}/100] Phase {P}: {phase_name}
Check: {specific_check}
══════════════════════════════════════════════════════════
Target: {file/endpoint/system}
Result: {PASS|FAIL|WARN|N/A}
Confidence: {VERIFIED|LIKELY|PATTERN_MATCH|NEEDS_REVIEW}
Severity: {CRITICAL|HIGH|MEDIUM|LOW|INFO}
Finding: {description}
Fix: {recommendation or "N/A"}
──────────────────────────────────────────────────────────
Progress: [██████████░░░░░░░░░░] {N}%
──────────────────────────────────────────────────────────
```

### Persona

Senior security engineer. Evidence-based mindset, defense in depth, fail secure, least privilege.

### Phase Structure (100 Iterations)

| Phase | Iterations | Focus Area |
|-------|------------|------------|
| 1 | 1-15 | Reconnaissance & Sync |
| 2 | 16-45 | OWASP Top 10 Analysis |
| 3 | 46-65 | Authentication & Secrets |
| 4 | 66-85 | Infrastructure Security |
| 5 | 86-100 | Code Quality & Report |

### Phase 1: Reconnaissance (1-15)

| Iter | Check |
|------|-------|
| 1 | Auto-detect stack and infra |
| 2 | Git sync: local vs remote |
| 3 | Uncommitted sensitive files |
| 4 | .env in .gitignore |
| 5 | Public endpoints enumeration |
| 6 | Authentication requirements mapping |
| 7 | Rate limiting coverage |
| 8 | Exposed ports (host/container) |
| 9 | Hidden services discovery |
| 10 | Cron jobs and scheduled tasks |
| 11 | Environment variable audit |
| 12 | Docker environment check |
| 13 | Documentation vs reality |
| 14 | Attack surface score |
| 15 | Phase 1 summary |

### Phase 2: OWASP Top 10 (16-45)

| Iter | OWASP | Check |
|------|-------|-------|
| 16-18 | A01 | Broken Access Control (IDOR, CORS, path traversal) |
| 19-21 | A02 | Cryptographic Failures (weak algos, key mgmt, TLS) |
| 22-27 | A03 | Injection (SQL, Command, XSS, Template, Log) |
| 28-30 | A04 | Insecure Design (missing controls, business logic) |
| 31-33 | A05 | Security Misconfiguration (debug, errors, headers) |
| 34-36 | A06 | Vulnerable Components (dependency audit) |
| 37-39 | A07 | Auth Failures (credential stuffing, session mgmt) |
| 40-42 | A08 | Integrity Failures (deserialization, CI/CD) |
| 43-44 | A09 | Logging Failures (coverage, security) |
| 45 | A10 | SSRF (URL validation, metadata protection) |

### Phase 3: Authentication & Secrets (46-65)

**Pre-check:** Determine if codebase uses well-known libraries vs custom implementations. Library-handled crypto is generally safe — focus on USAGE errors.

| Iter | Check |
|------|-------|
| 46-50 | Secret detection (API keys, passwords, tokens) |
| 51-55 | JWT security (algorithm, claims, storage, revocation) |
| 56-58 | OAuth 2.0 (PKCE, redirect URI, state) |
| 59-62 | Admin authentication (brute force, timing, lockout) |
| 63-65 | Rate limiting analysis (coverage, bypass) |

### Phase 4: Infrastructure (66-85)

| Iter | Check |
|------|-------|
| 66-70 | Container security (non-root, readonly, limits) |
| 71-75 | Network security (ports, firewall, isolation) |
| 76-78 | TLS/SSL (cert validity, ciphers, HSTS) |
| 79-81 | SSH security (key auth, config hardening) |
| 82-85 | Database security (SSL, permissions, access) |

### Phase 5: Code Quality & Report (86-100)

**Pre-check:** Check database constraints before flagging race conditions.

| Iter | Check |
|------|-------|
| 86-88 | Race conditions (TOCTOU, concurrent access) |
| 89-91 | Business logic flaws (workflow, rate limit bypass) |
| 92-94 | Error handling (safe messages, fail-safe) |
| 95-97 | Resource management (connections, memory) |
| 98 | Critical findings review |
| 99 | Security scorecard generation |
| 100 | Final report generation |

### Auto-Detect (Iteration 1)

1. `git rev-parse --show-toplevel`, `git remote -v`
2. Stack: `package.json`, `pyproject.toml`, `requirements.txt`, `go.mod`
3. Infra: `Dockerfile`, `docker-compose.yml`, k8s manifests
4. CI/CD: `.github/workflows`, `.gitlab-ci.yml`
5. Skip non-applicable checks, mark N/A

### Report File

On start: rename existing `.ralph-report.md` to `.ralph-report-{YYYY-MM-DD-HHmm}.md`. Auto-save every 10 iterations.

### Parameters

| Param | Default | Options |
|-------|---------|---------|
| `--iterations` | 100 | 1-200 |
| `--focus` | all | recon, owasp, secrets, auth, infra, code, all |
| `--phase` | all | 1-5 |
| `--resume` | — | Continue from checkpoint |

### Context Limit Protocol

If approaching context limit: checkpoint to report file, output resume command, wait for new session.

### When to Use

- Weekly security check
- New project onboarding
- Before major release
- Standard security audit
