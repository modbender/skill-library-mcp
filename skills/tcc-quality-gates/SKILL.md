# openClaw Skill: Quality Gateways (Generic Web + API Applications)

## Purpose
This skill defines and applies **6 universal quality gateways** for typical application projects that include:
- Backend API services (any stack)
- Web frontends (any stack)
- CI/CD pipelines (any provider)

The gateways are written in **LLM-friendly operational language**: how to **check**, **calculate**, **evaluate**, and **document** results consistently.

This skill is **language-agnostic** and can be used on any repository. It relies on a central configuration file:
- `.defs/quality-gateway-definition.json` (MUST be stored in the repository, not the workspace)

## Non-Negotiable Storage Rules (openClaw)
- The gateway definition file MUST be placed in: `REPO_ROOT/.defs/quality-gateway-definition.json`
- Temporary files MUST go to: `REPO_ROOT/.tmp/quality-gates/` (do not create or delete other workspace directories)
- Reports MUST be written to repository paths defined in the JSON config (default suggested below)

## Inputs
- Repository root path (REPO_ROOT)
- Optional CI artifacts path (if provided by the runtime)
- Optional commit range (for PR-focused evaluation)
- Optional environment notes (target load, environments, risk level)

## Outputs
1. A human-readable report (Markdown)
2. A machine-readable report (JSON) containing raw metrics + per-check scores
3. Evidence references (paths, snippets, CI links if available)

Recommended default output paths (override via JSON config):
- `docs/quality/quality-gate-report.md`
- `docs/quality/quality-gate-report.json`
- Evidence directory: `docs/quality/evidence/`

---

# The 6 Quality Gateways

Each gateway produces:
- **Score**: 0–100
- **Status**: PASS / WARN / FAIL
- **Blocking behavior**: some gateways are “blocking” (FAIL blocks release)

All gateway thresholds and weights come from:
- `.defs/quality-gateway-definition.json`

---

## Gateway 1 — Build & Dependency Health
### Goal
Ensure the system can be built and packaged reliably, and dependencies are manageable and safe to ship.

### What to Check (typical checks)
- CI pipeline status (green on default branch / PR)
- Reproducible build or deterministic packaging indicators
- Dependency freshness (stale/outdated dependencies)
- License policy compliance (allowlist/denylist)
- SBOM presence (if required)

### How to Measure / Calculate
- Boolean checks: PASS=100, FAIL=0
- Ratio checks (e.g., “outdated deps %”): scale 0–100 using thresholds
- Policy checks: hard FAIL if a forbidden license is detected (if enabled)

### Evidence to Collect
- CI job summary (or local build logs)
- Dependency list report output (tool-specific, but keep the report file)
- SBOM artifact path (if present)
- License scan output (if used)

### How to Document
In the report, include:
- Build command/pipeline name
- Artifact identifiers / versions
- Summary of dependency deltas and policy results

---

## Gateway 2 — Automated Testing & Coverage
### Goal
Prove correctness through automated tests and prevent regression.

### What to Check
- Unit tests pass
- Integration/API tests pass (or contract tests)
- E2E/smoke tests pass (for web apps)
- Code coverage meets thresholds (overall + critical components)
- Flaky test rate is controlled (if CI provides retries/flakes)

### How to Measure / Calculate
- Test pass: boolean
- Coverage: numeric percentage
  - Score mapping example:
    - >= target: 100
    - between warn and target: linear 70–99
    - below warn: linear 0–69
- Optional “critical path coverage” gets extra weight

### Evidence to Collect
- Test run outputs (JUnit/TRX/etc.)
- Coverage summary files
- List of failed tests (if any) + links

### How to Document
- Test suites executed
- Coverage numbers (overall + key areas)
- Notes on skipped tests (if allowed) and rationale

---

## Gateway 3 — Security & Supply-Chain
### Goal
Prevent known vulnerabilities, secrets leakage, insecure configs, and supply-chain risks.

### What to Check
- Dependency vulnerabilities (Critical/High/Medium counts)
- Secret scanning results (must be zero leaked secrets)
- Basic secure configuration checks (CSP, TLS, auth boundaries) where applicable
- SAST findings severity counts (if tooling exists)
- Container image scan (if containers exist)

### How to Measure / Calculate
- Vulnerability gating (typical):
  - Critical = 0 required (FAIL otherwise)
  - High = 0 required (or <= allowedHigh)
  - Medium allowed up to a budget (WARN if above warn)
- Secrets: any secret finding => FAIL (blocking)
- Score: start at 100 and subtract penalties by severity and count (config-driven)

### Evidence to Collect
- Vulnerability scan report files
- Secret scan output (including file paths and fingerprint IDs, not actual secrets)
- SAST report snippet/summary

### How to Document
- Severity counts and whether exceptions exist
- Any exception MUST include: reason, owner, expiry date (if your org uses waivers)

---

## Gateway 4 — Performance & Efficiency (API + Web)
### Goal
Ensure the system meets baseline performance and user experience targets.

### What to Check
API (typical):
- p95 latency under target
- Error rate under target
- Throughput meets expected load (if known)

Web (typical):
- Core Web Vitals (LCP, CLS, INP) on a reference device/profile
- Bundle size / asset weight thresholds (optional)

### How to Measure / Calculate
- Latency score:
  - p95 <= target: 100
  - between target and warn: linear 70–99
  - > warn: 0–69 (linear), with hard FAIL if beyond “max”
- Error rate:
  - <= target: 100
  - <= warn: 70–99
  - > warn: 0–69, FAIL if beyond max
- Web vitals:
  - Each metric scored independently; weighted into a single web score

### Evidence to Collect
- Load test or benchmark outputs (k6/JMeter/etc.)
- APM snapshots (if available)
- Lighthouse or Web Vitals report exports

### How to Document
- Test conditions: environment, dataset size, concurrency, device profile
- Key p95 / error rate / vitals values
- Notable regressions vs baseline

---

## Gateway 5 — Maintainability & Code Health
### Goal
Keep the codebase understandable, changeable, and reviewable over time.

### What to Check
- Static analysis quality (lint errors, rule violations)
- Complexity thresholds (cyclomatic complexity, large functions/classes)
- Duplication rate
- “Change risk” signals (hotspots: frequent churn + complexity)
- Documentation coverage for public APIs (e.g., endpoint docs, component docs)

### How to Measure / Calculate
- Issue density: findings per KLOC (or per file for smaller repos)
- Complexity score: percentage of units exceeding complexity threshold
- Duplication: % duplicated lines
- Score: weighted average of normalized sub-scores (config-driven)

### Evidence to Collect
- Static analysis summaries
- Complexity and duplication reports (any tool is fine; store outputs)
- List of top hotspots and why (files + metrics)

### How to Document
- Top 10 problems by impact
- Concrete refactoring suggestions only if asked; otherwise just findings

---

## Gateway 6 — Release Readiness & Operability (Observability + Runbooks)
### Goal
Make sure the system can be operated safely in production.

### What to Check
- Health endpoints exist and are meaningful
- Logging is structured and includes correlation IDs
- Metrics and dashboards exist for key signals (latency, error rate, saturation)
- Alerts configured for SLO breaches / error budget burn (if applicable)
- Runbooks for major failure modes exist (deploy rollback, incident triage)
- Versioning and changelog/release notes exist

### How to Measure / Calculate
Mostly “presence + completeness” scoring:
- Each required artifact is a boolean check
- Optional maturity rubric: 0 (missing), 50 (partial), 100 (complete)
- Blocking if “minimum operability” is not met (config-driven)

### Evidence to Collect
- Paths to runbooks, dashboards-as-code, alert configs
- Sample log/metric/tracing docs
- On-call/ops notes (if present)

### How to Document
- List missing operational artifacts
- Minimum go-live checklist status

---

# Standard Evaluation Algorithm (LLM-Executable)

## Step 1: Load configuration
- Read `REPO_ROOT/.defs/quality-gateway-definition.json`
- Validate it against the schema description (see below)
- If fields are missing, use documented defaults from the JSON

## Step 2: Collect metrics per check
For each gate:
- For each check:
  - Identify data source:
    - Prefer CI artifacts if provided
    - Otherwise use repository files and local commands (if allowed by runtime)
  - Produce a metric value (number/boolean/string) and evidence references

## Step 3: Score each check (0–100)
Use the scoring method defined per check:
- `boolean`: pass => 100, fail => 0
- `threshold_range`: linear scoring between warn and target
- `penalty_by_count`: start at 100 and subtract per issue
- `rubric`: map {missing/partial/complete} to {0/50/100}

## Step 4: Score each gateway
- Compute weighted average of its checks
- Determine gateway status using configured thresholds:
  - Score >= passScore => PASS
  - Score >= warnScore => WARN
  - else => FAIL
- If gateway is marked `blockingOnFail=true`, any FAIL blocks release

## Step 5: Produce reports
Write:
1) Markdown report (human)
2) JSON report (machine)
Include:
- per-gateway score/status
- per-check metrics + evidence paths
- overall score and overall status
- explicit “BLOCKERS” list if any

---

# Report Template (Markdown)
Use this outline in `docs/quality/quality-gate-report.md` unless JSON overrides paths:

## Summary
- Overall Score:
- Overall Status:
- Blocking Failures:
- Date/Commit:

## Gateway Results
| Gateway | Score | Status | Key Metrics | Evidence |
|---|---:|---|---|---|

## Details (per Gateway)
### <Gateway Name>
- Score/Status
- Checks:
  - <Check>: metric=..., score=..., evidence=...
- Notes / Exceptions

---

# quality-gateway-definition.json — JSON Schema Description

The configuration file is a normal JSON document with:

## Root
- `schemaVersion` (string) — version of this config layout
- `projectProfile` (object) — context used for defaults
- `scoring` (object) — global pass/warn thresholds and aggregation rules
- `reporting` (object) — output paths and evidence folder
- `gates` (array) — list of gateway definitions (exactly 6 for this skill)

## projectProfile (object)
- `applicationType` (string) — e.g. `"web_api_and_web"`
- `riskLevel` (string) — `"low"|"medium"|"high"`
- `releaseCadence` (string) — e.g. `"daily"|"weekly"|"monthly"`
- `expectedLoad` (object, optional)
  - `apiRps` (number)
  - `concurrency` (number)

## scoring (object)
- `passScore` (number 0–100)
- `warnScore` (number 0–100)
- `overallAggregation` (string) — `"weighted_average"`
- `blockIfAnyBlockingGateFails` (boolean)

## reporting (object)
- `markdownReportPath` (string, repo-relative)
- `jsonReportPath` (string, repo-relative)
- `evidenceDir` (string, repo-relative)
- `tempDir` (string, repo-relative; MUST be inside `.tmp/quality-gates/`)

## gates (array of objects)
Each gate:
- `id` (string) — stable identifier
- `name` (string)
- `description` (string)
- `weight` (number) — relative importance in overall score
- `blockingOnFail` (boolean)
- `checks` (array)

## checks (array of objects)
Each check:
- `id` (string)
- `name` (string)
- `description` (string)
- `weight` (number)
- `metricType` (string) — `"boolean"|"percentage"|"count"|"duration_ms"|"rubric"`
- `scoringMethod` (string) — `"boolean"|"threshold_range"|"penalty_by_count"|"rubric"`
- `thresholds` (object) — depends on scoringMethod:
  - for `threshold_range`:
    - `target` (number)
    - `warn` (number)
    - `max` (number, optional hard-fail)
    - `direction` (string) — `"higher_is_better"|"lower_is_better"`
  - for `penalty_by_count`:
    - `allowed` (number)
    - `warnAbove` (number)
    - `failAbove` (number)
    - `penaltyPerUnit` (number)
- `evidenceHints` (array of strings) — where to find evidence in a generic repo/CI
- `notes` (string, optional)

---

# Operational Notes
- If a metric cannot be measured, do NOT invent numbers.
  - Mark the check as `"unknown"` in the JSON report and score it using the config’s fallback rule (recommended: treat unknown as WARN with score 70 unless the check is security/secrets, where unknown should be FAIL).
- Always include evidence references (paths or CI artifact names).
- Keep all temp work inside `.tmp/quality-gates/`.

# JSON references
- `templ/quality-gateway-definition-template.json` (template settings file. Can be copied to `REPO_ROOT/.defs/quality-gateway-definition.json` if missing)
