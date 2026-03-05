---
name: ralph-quick
description: "Fast security spot-check with 10 iterations (~5-10 min). Use when user says 'quick security check', 'pre-deploy audit', 'ralph quick', 'fast security scan', 'spot check before deploy', or 'daily security check'. Covers secrets, OWASP basics, auth, rate limiting, and containers."
metadata: { "openclaw": { "emoji": "🔍" }, "author": "dorukardahan", "version": "2.0.0", "category": "security", "tags": ["security", "audit", "owasp", "pre-deploy"] }
---

# Ralph Quick — 10 Iterations (~5-10 min)

Fast security spot-check for pre-deployment or daily security hygiene.

## References

- [Severity definitions](references/severity-guide.md)

## Instructions

### Execution Engine

YOU MUST follow this loop for EVERY iteration:

1. **STATE**: Read current iteration (start: 1)
2. **ACTION**: Perform ONE check from current phase
3. **VERIFY**: Before reporting FAIL — read actual code, check if a library handles it, check DB constraints, check if dev-only
4. **REPORT**: Output iteration result in the format below
5. **INCREMENT**: iteration = iteration + 1
6. **CONTINUE**: IF iteration <= 10 GOTO Step 1
7. **FINAL**: Generate summary report saved to `.ralph-report.md`

**Critical rules:**
- ONE check per iteration (not all at once)
- ALWAYS show iteration counter `[QUICK-X/10]`
- NEVER skip iterations
- If VERIFY is inconclusive: mark `NEEDS_REVIEW`, not `FAIL`

### Per-Iteration Output

```
[QUICK-{N}/10] {check_name}
Target: {file or system component}
Result: {PASS|FAIL|WARN|N/A}
Confidence: {VERIFIED|LIKELY|PATTERN_MATCH|NEEDS_REVIEW}
Finding: {description or "Clean"}
───────────────────────────────
```

### Persona

Senior security engineer — evidence-based, critical focus, maximum efficiency.

### Phase Structure

| Iter | Check |
|------|-------|
| 1 | Auto-detect stack, infra, git sync |
| 2 | .env in .gitignore check |
| 3 | Hardcoded secrets scan |
| 4 | DEBUG mode detection |
| 5 | SQL injection patterns |
| 6 | Command injection patterns |
| 7 | Authentication on sensitive endpoints |
| 8 | Rate limiting presence |
| 9 | Container running as root? |
| 10 | Summary & recommendations |

### Auto-Detect (Iteration 1)

Deterministic order:
1. `git rev-parse --show-toplevel`
2. Stack: `package.json`, `pyproject.toml`, `requirements.txt`, `go.mod`
3. Infra: `Dockerfile`, `docker-compose.yml`, k8s manifests
4. CI/CD: `.github/workflows`, `.gitlab-ci.yml`
5. Skip non-applicable checks, mark N/A

### Confidence Levels

| Level | Meaning |
|-------|---------|
| VERIFIED | Confirmed with code reading or PoC |
| LIKELY | Strong evidence, no PoC |
| PATTERN_MATCH | Keyword match only — flag for human review |
| NEEDS_REVIEW | Inconclusive |

### Severity

| Level | CVSS | Response |
|-------|------|----------|
| CRITICAL | 9.0-10.0 | Stop and fix immediately |
| HIGH | 7.0-8.9 | Fix before deployment |
| MEDIUM | 4.0-6.9 | Schedule fix |
| LOW | 0.1-3.9 | Note for later |

### Report File

On start: if `.ralph-report.md` exists, rename to `.ralph-report-{YYYY-MM-DD-HHmm}.md`. Save final report at end.

### Parameters

| Param | Default | Options |
|-------|---------|---------|
| `--iterations` | 10 | 1-20 |
| `--focus` | all | secrets, owasp, infra, all |

Note: Parameters are AI-interpreted instructions, not parsed CLI args.

### When to Use

- Pre-deployment quick check
- Daily security spot-check
- Verifying a specific fix

For deeper audits: `/ralph-security` (100), `/ralph-ultra` (1,000), `/ralph-promax` (10,000).
