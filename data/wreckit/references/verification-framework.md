# wreckit Verification Framework — Harmonized Checklist

_The "closest-to-bulletproof" AI code verification pipeline. AI tests + scripts, but with independent checks._

**Core principle:** Use AI aggressively, but structure it so it **can't silently agree with itself.**

---

## The 14-Step Pipeline

### 1. Freeze a Formal Spec (Source of Truth)
- Write: expected behavior, error handling, constraints, security assumptions
- Extract invariants ("must always hold") + forbidden behaviors ("must never happen")
- Performance expectations included
- AI can draft this; a human should sanity-check it

### 2. Establish Independent Oracles (Anchor to Reality)
Pick at least one:
- Reference implementation (trusted library / known-good version)
- Brute-force "slow but obviously correct" checker for small inputs
- Golden tests with hand-verified expected outputs
- Metamorphic properties (relationships that must hold under transformations)

**Why:** Prevents "AI wrote code, AI wrote tests, both wrong in the same way."

### 3. Generate Tests from Spec (Separate AI Context/Model)
The test author must NOT see the implementation. Generate:
- Unit tests (core logic)
- Integration tests (module boundaries)
- Negative tests (bad inputs, malformed data)
- Boundary tests (empty, max size, extremes)
- Sequence/state tests (repeated calls, ordering, partial failures)

### 4. Adversarial Red-Team Pass
A separate AI agent assumes the code is broken and tries to prove it:
- Injection attacks
- Logic bypasses
- Malformed inputs, weird encodings
- Concurrency abuse
- Resource exhaustion

### 5. Differential Testing
- Compare output vs oracle/reference/brute-force (Step 2), at least on small/medium cases
- If multiple implementations exist, compare across them
- **One of the highest-value steps available** — catches "plausible but wrong" logic extremely well

### 6. Property-Based Testing + Fuzzing
- Encode invariants from Step 1 into properties
- Run thousands+ randomized cases
- Store failing seeds/inputs — maintain a crash corpus that grows over time

**Why:** Finds bugs nobody thought to write a test for.

### 7. Mutation Testing (The Real Judge)
- Introduce synthetic bugs, verify tests catch them
- Coverage is a *floor* (necessary, not sufficient)
- **Mutation score is the honest measure of test suite quality**
- Set a threshold and treat it as a gate

### 8. Static Analysis
- Type checking + linting
- Security scanning (SAST)
- Taint analysis
- Complexity metrics

### 9. Dynamic Analysis
- Memory sanitizers
- Undefined behavior detectors
- Race condition detectors
- Leak detectors

**Why:** Catches entire classes of bugs that no amount of test cases will find.

### 10. Performance / Load Benchmarking
- Test against realistic AND worst-case data volumes
- Time + memory thresholds
- Load/stress/concurrency tests if applicable

**Why:** AI code often "works on 10 items" but fails at 10,000.

### 11. Dependency Audit
- Verify all packages are real (not hallucinated)
- Check maintained, vulnerability-free, actually necessary
- Typosquat detection
- License checks

**Why:** One of the most AI-specific failure modes.

### 12. Deterministic, Reproducible Harness
- Pinned dependencies
- Fixed random seeds
- Logged inputs on failure
- Resource limits + timeouts
- Runtime sanitizers where available

**Why:** Without this, fuzz and property-based testing can produce non-reproducible failures — almost worse than not testing at all.

### 13. CI Integration with Regression Corpus
- Every bug becomes a permanent test
- Fuzz crashes accumulate
- Nothing runs without the full pipeline passing
- One command/script runs everything

### 14. Human Validation Anchor
- At least one hand-verified golden test case per critical path
- One sanity check that doesn't depend on any AI reasoning at all
- Business-logic security (authz rules, money movement, workflow bypass)
- Regulatory/compliance constraints
- Maintainability/architecture tradeoffs

---

## Why This Works

The strongest parts are **independence + oracles + mechanical checks**:

| Defense | What It Prevents |
|---------|-----------------|
| **Independence** (separate contexts/models, spec-only tests) | Shared blind spots |
| **Oracles/differential** (known-correct reference) | Circular reasoning |
| **Mechanical truth** (mutation testing, analyzers, dependency audits, sandbox) | AI bias |
| **Scale gates** (benchmarks + load) | "Works small, breaks big" |

---

## Role Separation (The "Three Minds" Pattern)

| Role | Job | Context |
|------|-----|---------|
| **Builder AI** | Generates code | Has spec + requirements |
| **Tester AI** | Generates tests from spec only | Fresh context, does NOT see code |
| **Breaker AI** | Tries to make it fail | Fresh context, different model if possible |

This is the main defense against shared blind spots.

---

## How This Maps to wreckit Gates

| wreckit Gate | Framework Steps |
|-------------|----------------|
| AI Slop Scan | 11 (dependency audit) + 8 (static analysis) |
| Type Check | 8 (static analysis — type checking) |
| Ralph Loop | 1 (spec) + 3 (test gen) + iterative fix |
| Test Quality | 3 (layered tests) + 6 (property/fuzz) + 7 (mutation) |
| Mutation Kill | 7 (mutation testing) — the gate |
| Proof Bundle | 13 (CI integration) + all results committed |

**Steps wreckit should add:**
- **Step 2**: Independent oracle / differential testing
- **Step 4**: Adversarial red-team (Breaker AI as separate subagent)
- **Step 5**: Differential testing
- **Step 9**: Dynamic analysis / sanitizers
- **Step 10**: Performance benchmarking gate
- **Step 12**: Deterministic harness enforcement

---

## Honest Assessment

> There is no bulletproof method. But **independent oracles + differential testing + fuzzing + mutation testing + sanitizers** is the practical ceiling, and most teams aren't doing even two of those. Getting all 14 steps running in CI puts you ahead of virtually every production codebase in existence.

### Where we're still weak (both frameworks):
- Maintainability/readability (hard to automate)
- Regulatory compliance (domain-specific)
- Formal verification (theoretical ceiling, impractical for most code)

---

_This framework is the foundation for wreckit's verification pipeline. Each step maps to a gate or subagent task. The goal: make AI-generated code trustworthy enough to ship._
