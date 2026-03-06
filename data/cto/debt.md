# Technical Debt Management

## What Is Technical Debt

Technical debt is **intentional** trade-off: shipping faster now with known shortcuts.

**Not debt:**
- Bugs (just fix them)
- Bad code from inexperience (training problem)
- Outdated patterns (evolution, not debt)

**Is debt:**
- Skipped tests to meet deadline
- Hardcoded config that needs parameterization
- Monolith that needs decomposition
- Known performance issues deferred

## Debt Tracking

### Debt Registry

Maintain a living document:

| Item | Type | Impact | Interest Rate | Payoff Estimate |
|------|------|--------|---------------|-----------------|
| Auth service coupling | Architecture | High | Growing | 2 sprints |
| Missing API tests | Testing | Medium | Stable | 1 sprint |
| Legacy payment code | Code quality | Low | Stable | 3 sprints |

**Interest rate:** How fast does this get worse?
- Growing = urgent
- Stable = schedule when convenient

### Debt Types

| Type | Example | Typical Fix |
|------|---------|-------------|
| Code | Duplicated logic, unclear naming | Refactor |
| Architecture | Wrong boundaries, scaling limits | Redesign |
| Testing | Missing coverage, flaky tests | Add tests |
| Infrastructure | Manual processes, outdated tools | Automate |
| Documentation | Missing or stale docs | Update |

## Debt Paydown Strategy

### The 20% Rule

Reserve 20% of engineering capacity for:
- Maintenance
- Debt paydown
- Developer experience improvements

**How:** Every sprint includes debt items. Not negotiable.

### Refactor with Features

Best approach: Fix debt alongside feature work.

- Feature touches auth? Improve auth tests.
- New endpoint? Clean up related code.
- Deploying service? Fix deploy scripts.

**Why:** Pure refactor sprints lose business support. Bundled improvements don't.

### When to Do Big Rewrites

Almost never. But consider when:
- Old system literally can't support new requirements
- Cost of ongoing maintenance exceeds rewrite
- Team has rewrite experience (rare)

**Reality check:** Rewrites take 2-3x estimated time, and you're maintaining both systems during.

## Preventing Debt

| Practice | Impact |
|----------|--------|
| Code review | Catches shortcuts before merge |
| Definition of done | Tests, docs included |
| Tech debt budget | Planned capacity |
| Architecture reviews | Catches structural issues early |
| Retrospectives | Team identifies pain points |

## Communicating Debt to Business

Don't say: "We have technical debt"
Say: "This will slow feature delivery by 30% unless we invest 2 sprints"

**Frame as:**
- Velocity impact
- Risk (outages, security)
- Opportunity cost
- Concrete investment with concrete return
