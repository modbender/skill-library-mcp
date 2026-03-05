# Review Playbook - Security Best Practices

Use this sequence for explicit security scans and hardening reviews.

## 1. Scope and Inventory

1. Confirm target boundary (service, package, endpoint set).
2. Identify runtime stack and trust boundaries.
3. Classify data handled by the target (public, internal, sensitive).

## 2. Baseline Pass

Review baseline controls:
- Authentication and authorization
- Input validation and output encoding
- Secret handling and configuration
- Dependency versions and known vulnerable libraries
- Logging and error disclosure behavior

## 3. Finding Extraction

For each finding, capture:
- ID (`SEC-001`, `SEC-002`, ...)
- Severity and confidence
- Exact location with line references
- Evidence snippet
- Impact in one sentence
- Minimal remediation path

## 4. Prioritization

Sort findings by:
1. Exploitability
2. Blast radius
3. Ease of remediation
4. Regression risk

Critical and high issues should be grouped into an immediate action set.

## 5. Remediation Plan

For each planned fix:
- Describe expected behavior changes
- Define test coverage required
- Apply smallest safe diff first
- Re-validate before moving to the next finding

## 6. Reporting Format

Deliver:
1. Executive summary
2. Prioritized findings table
3. Fix plan by severity
4. Residual risk and accepted exceptions

Keep the report concise and directly actionable by engineering teams.
