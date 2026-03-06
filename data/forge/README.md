# Forge

**Quality forged in, not bolted on.**

Forge is an autonomous quality engineering swarm skill for [Claude Code](https://claude.com/claude-code) that combines BDD behavioral verification, 7 quality gates, confidence-tiered learning, and self-healing fix loops. It spawns 8 specialized agents that work in parallel to verify, test, fix, and commit — continuously — until every Gherkin scenario passes and every quality gate clears.

---

## Key Features

- **8 specialized agents** working in parallel with cost-optimized model routing
- **Gherkin behavioral specifications** as the single source of truth
- **7 quality gates**: Functional, Behavioral, Coverage, Security, Accessibility, Resilience, Contract
- **Confidence-tiered fix patterns** (Platinum/Gold/Silver/Bronze) that evolve over time
- **Defect prediction** based on historical failure data and file changes
- **Chaos/resilience testing** with controlled failure injection
- **Cross-context dependency awareness** with cascade re-testing
- **Shared types and cross-cutting validation** across bounded contexts
- **Agent-optimized ADRs** with MUST/MUST NOT constraints and verification commands
- **Visual regression testing** with pixel-by-pixel comparison
- **Architecture-agnostic** — monolith, microservices, monorepo, mobile+backend
- **Optional Agentic QE integration** for enhanced pattern search, security scanning, and more
- **No mocking** — all tests run against the real backend

---

## Philosophy

### Three Pillars

| Pillar | Source | What It Does |
|--------|--------|--------------|
| **Build** | DDD+ADR+TDD methodology | Structured development with quality gates, defect prediction, confidence-tiered fixes |
| **Verify** | BDD/Gherkin behavioral specs | Continuous behavioral verification — the PRODUCT works, not just the CODE |
| **Heal** | Autonomous E2E fix loop | Test → Analyze → Fix → Commit → Learn → Repeat |

### "DONE DONE"

"DONE DONE" means: the code compiles AND the product behaves as specified. Every Gherkin scenario passes. Every quality gate clears. Every dependency graph is satisfied.

---

## Quick Start

```bash
# Copy SKILL.md to your Claude Code skills directory
cp SKILL.md ~/.claude/skills/forge.md

# Run on your project
/forge --autonomous --context payments
```

---

## Invocation Modes

| Command | Description |
|---------|-------------|
| `/forge --autonomous --all` | Full autonomous run — all contexts, all gates |
| `/forge --autonomous --context [name]` | Single context autonomous run |
| `/forge --verify-only` | Behavioral verification only (no fixes) |
| `/forge --verify-only --context [name]` | Verify single context |
| `/forge --fix-only --context [name]` | Fix failures, don't generate new tests |
| `/forge --learn` | Analyze patterns, update confidence tiers |
| `/forge --add-coverage --screens [names]` | Add coverage for new screens/pages/components |
| `/forge --spec-gen --context [name]` | Generate Gherkin specs for a context |
| `/forge --spec-gen --all` | Generate Gherkin specs for all contexts |
| `/forge --gates-only` | Run quality gates without test execution |
| `/forge --gates-only --context [name]` | Run gates for single context |
| `/forge --predict` | Defect prediction only |
| `/forge --predict --context [name]` | Predict defects for single context |
| `/forge --chaos --context [name]` | Chaos/resilience testing for a context |
| `/forge --chaos --all` | Chaos testing for all contexts |

---

## Architecture

### Autonomous Loop

```
Specify → Test → Analyze → Fix → Audit → Gate → Commit → Learn → Repeat
```

```
┌────────────────────────────────────────────────────────────────────┐
│                    FORGE AUTONOMOUS LOOP                            │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐      │
│  │ Specify  │──▶│   Test   │──▶│ Analyze  │──▶│   Fix    │      │
│  │ (Gherkin)│   │ (Run)    │   │ (Root    │   │ (Tiered) │      │
│  └──────────┘   └──────────┘   │  Cause)  │   └──────────┘      │
│       ▲                        └──────────┘        │              │
│       │                                            ▼              │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐      │
│  │  Learn   │◀──│  Commit  │◀──│  Gate    │◀──│  Audit   │      │
│  │ (Update  │   │ (Auto)   │   │ (7 Gates)│   │ (A11y)   │      │
│  │  Tiers)  │   └──────────┘   └──────────┘   └──────────┘      │
│  └──────────┘                                                     │
│       │                                                           │
│       └──────────────── REPEAT ──────────────────────────────────│
│                                                                    │
│  Loop continues until: ALL 7 GATES PASS or MAX_ITERATIONS (10)   │
└────────────────────────────────────────────────────────────────────┘
```

### Execution Phases

1. **Phase 0** — Backend setup (build, run, health check, seed data)
2. **Phase 1** — Behavioral specification & architecture records (Gherkin specs, ADRs)
3. **Phase 2** — Contract & dependency validation (schemas, shared types, cross-cutting)
4. **Phase 3** — Swarm initialization (load patterns, predictions, confidence tiers)
5. **Phase 4** — Spawn 8 autonomous agents in parallel
6. **Phase 5** — Quality gates evaluation (7 gates after every fix cycle)

---

## Quality Gates

| Gate | Check | Threshold | Blocking |
|------|-------|-----------|----------|
| 1. Functional | All tests pass | 100% pass rate | YES |
| 2. Behavioral | Gherkin scenarios satisfied | 100% of targeted scenarios | YES |
| 3. Coverage | Path coverage | >=85% overall, >=95% critical | YES (critical only) |
| 4. Security | No secrets, SAST checks, no injection vectors | 0 critical/high violations | YES |
| 5. Accessibility | Labels, target sizes, contrast | WCAG AA | Warning only |
| 6. Resilience | Offline, timeout, error handling | Tested for target context | Warning only |
| 7. Contract | API response matches schema | 0 mismatches | YES |

---

## Agent Roles

| Agent | Model | Role |
|-------|-------|------|
| **Specification Verifier** | Sonnet | Generates/validates Gherkin specs and ADRs for bounded contexts |
| **Test Runner** | Haiku | Executes E2E test suites, parses results, maps failures to specs |
| **Failure Analyzer** | Sonnet | Root cause analysis, pattern matching, dependency impact assessment |
| **Bug Fixer** | Opus | Applies confidence-tiered fixes from first principles |
| **Quality Gate Enforcer** | Haiku | Evaluates all 7 gates, arbitrates agent disagreements |
| **Accessibility Auditor** | Sonnet | WCAG AA audit: labels, contrast, targets, focus order |
| **Auto-Committer** | Haiku | Stages fixed files, creates detailed commits with gate statuses |
| **Learning Optimizer** | Sonnet | Updates confidence tiers, defect prediction, coverage metrics |

---

## Configuration

### Project Config (optional)

```yaml
# forge.config.yaml — placed at repo root
architecture: microservices
backend:
  services:
    - name: auth-service
      port: 8081
      healthEndpoint: /health
      buildCommand: npm run build
      runCommand: npm start
frontend:
  technology: react
  testCommand: npx cypress run --spec {target}
  testDir: cypress/e2e/
  specDir: cypress/e2e/specs/

# Model routing overrides
model_routing:
  bug-fixer: opus
  failure-analyzer: sonnet
  test-runner: haiku

# Visual regression
visual_regression:
  enabled: true
  threshold: 0.001

# Agentic QE integration
integrations:
  agentic-qe:
    enabled: true
    domains: [defect-intelligence, security-compliance, visual-accessibility, contract-testing]
```

### Context Config (optional)

```yaml
# forge.contexts.yaml — bounded context definitions
contexts:
  - name: identity
    testFile: identity.cy.ts
    specFile: identity.feature
    paths: 68
    subdomains: [Auth, Profiles, Verification]
  - name: payments
    testFile: payments.cy.ts
    specFile: payments.feature
    paths: 89
    subdomains: [Wallet, Cards, Transactions]

dependencies:
  identity:
    blocks: [payments, orders]
  payments:
    depends_on: [identity]
    blocks: [orders, subscriptions]
```

If no configuration files are present, Forge auto-discovers the project structure on first run.

---

## Agentic QE Integration

Forge optionally integrates with [Agentic QE](https://github.com/proffesor-for-testing/agentic-qe) via MCP for enhanced capabilities:

| Capability | Without AQE | With AQE |
|-----------|-------------|----------|
| Pattern Storage | claude-flow memory | ReasoningBank (vector-indexed, 150x faster) |
| Defect Prediction | File changes + history | Specialized defect-intelligence agents |
| Security Scanning | Gate 4 static checks | Full SAST/DAST analysis |
| Accessibility | Built-in auditor | visual-tester + accessibility-auditor |
| Contract Testing | Schema validation | contract-validator + graphql-tester |
| Progress | `.forge/progress.jsonl` | AG-UI real-time streaming |

All AQE features are additive. Forge works identically without AQE installed.

---

## References

- [Continuous Behavioral Verification: Ongoing Path to Done](https://www.linkedin.com/pulse/continuous-behavioral-verification-ongoing-path-done-ikenna-okpala) — Ikenna Okpala
- [Build with Quality Skill: How I Build Software 10x Faster](https://www.linkedin.com/pulse/build-quality-skill-how-i-build-software-10x-faster-mondweep-chakravorty) — Mondweep Chakravorty
- [claude-code-v3-qe-skill](https://github.com/mondweep/vibe-cast) — V3 QE Skill
- [agentic-qe](https://github.com/proffesor-for-testing/agentic-qe) — Agentic QE Framework

---

## License

MIT
