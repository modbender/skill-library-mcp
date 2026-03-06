# PR Rejection Vector Taxonomy

A condensed, agent-readable framework for predicting PR rejection. Derived from academic research and industry practice.

## 1. Technical Gatekeeping

Automated gates that block merge mechanically.

- **CI failure**: Any failing check = hard block in most repos
- **Build breakage**: Compilation errors, type errors, lint failures
- **Test failures**: Existing tests broken by the change
- **Missing tests**: New code without corresponding tests (coverage regression)
- **Lint/format violations**: Style guide not followed, auto-formatter not run
- **Performance regression**: Benchmarks show degradation
- **Type errors**: TypeScript/Flow/mypy failures
- **Security scan findings**: SAST/DAST tools flag vulnerabilities
- **Dependency audit failures**: Known CVEs in added dependencies

**Weight**: Very high — these are usually hard blockers.

## 2. Architectural Misalignment

The PR works but doesn't fit the project's design philosophy.

### Pattern Violations
- Code doesn't follow established patterns (e.g., MVC in a Rails app, hooks in React)
- Inconsistent naming conventions
- Wrong abstraction level (too high or too low)
- Reinventing existing utilities instead of reusing them

### AI-Generated Code Signals
- Overly verbose or boilerplate-heavy code
- Comments that explain obvious things
- Code that works but ignores project conventions
- Generic implementations that don't use project-specific patterns

### Scope Creep
- PR description says "fix bug X" but also refactors Y and adds feature Z
- Touching files unrelated to the stated purpose
- "While I was here..." changes mixed with the main change
- Large reformatting mixed with logic changes

### Dependency Concerns
- Adding new dependencies for trivial functionality
- Dependency with problematic license
- Unmaintained or low-quality dependency
- Significant size increase to bundle/binary

### Legacy/Migration Friction
- Using deprecated APIs or patterns
- Not following active migration direction
- Adding to old system when new system exists

**Weight**: High — maintainers protect architectural integrity aggressively.

## 3. Process Constraints

Procedural and logistical factors that prevent merge.

### Size
- **<100 LOC**: Almost always reviewable, high merge rate
- **100-400 LOC**: Sweet spot, good merge rate
- **400-1000 LOC**: Review fatigue begins, merge rate drops
- **>1000 LOC**: Dramatic drop in merge rate; often asked to split
- Large PRs get superficial reviews → bugs slip through → maintainers learn to reject them

### Timing
- PR submitted during feature freeze
- PR targets a branch that's about to be cut/released
- Competing PR for the same feature (first-mover advantage)
- PR duplicates recently merged work

### Staleness & Abandonment
- **<1 week**: Fresh, high attention
- **1-2 weeks**: Normal for complex PRs
- **2-4 weeks**: Concern — losing context, may have conflicts
- **>30 days**: Likely abandoned; merge conflicts accumulate
- **>90 days**: Almost certainly dead unless actively discussed
- Merge conflicts signal staleness — rebasing required

### Template Compliance
- Empty or missing PR description when template exists
- Required fields not filled (testing steps, screenshots, linked issue)
- Checklist items not checked

### Branch Targeting
- PR against wrong branch (e.g., main instead of develop)
- PR against a feature branch that was already merged

**Weight**: Medium-high — process violations are easy to detect and often enforced.

## 4. Social Dynamics

Human factors that influence merge decisions.

### Communication Quality
- Vague or missing PR description
- Defensive responses to review feedback
- Not responding to reviewer questions
- Language barrier causing miscommunication
- Confrontational tone in discussions

### Trust & Track Record
- **First-time contributor**: Higher scrutiny, lower trust → higher rejection rate
- **Established contributor**: Benefit of the doubt, faster reviews
- **Core team member**: Highest trust, often self-merge capable
- Author's recent merge rate in the repo is predictive
- Previous negative interactions create bias

### Reviewer Dynamics
- Key reviewer is on vacation or overloaded
- No reviewer assigned or willing to review
- Reviewer and author have history of disagreement
- Required reviewer explicitly blocks

### Organizational Politics
- PR conflicts with team lead's preferred approach
- Feature not aligned with current roadmap/priorities
- "Not invented here" syndrome
- Maintainer fatigue in popular open-source projects

**Weight**: Medium — harder to detect from data but very real.

## 5. Legal, Security & Compliance

Hard blockers that no amount of good code can overcome.

### Security
- Introduces XSS, SQL injection, or other vulnerabilities
- Hardcoded secrets, API keys, or credentials in code
- Weakens authentication or authorization
- Disables security features or controls

### Licensing
- Added dependency with incompatible license (GPL in MIT project, etc.)
- Copy-pasted code from differently-licensed source
- Missing license headers when required

### Compliance
- CLA/DCO not signed (hard block in many corporate OSS projects)
- Export control concerns
- GDPR/privacy implications not addressed
- Missing required legal review

### Secrets & Data
- Accidentally committed secrets (even if removed in later commit, they're in history)
- PII in test fixtures or logs
- Internal URLs or infrastructure details exposed

**Weight**: Very high — these are non-negotiable blockers.

## 6. Composite Risk Signals

Combinations that strongly predict rejection:

| Signal Combination | Risk Level |
|---|---|
| Failed CI + no response to comments | 🔴 Very high |
| >1000 LOC + scattered files + no description | 🔴 Very high |
| Changes requested + no updates in >1 week | 🔴 High |
| First-time author + large PR + no linked issue | 🔴 High |
| Draft status + WIP label | 🟡 Not ready (expected) |
| All CI green + approvals + <400 LOC | 🟢 Very likely to merge |
| Core team author + small change + CI green | 🟢 Almost certain merge |

## 7. Positive Merge Indicators

Signals that increase merge probability:

- All CI checks passing (green)
- One or more approvals from required reviewers
- Small, focused change (<400 LOC)
- Clear title and thorough description
- Linked to an open issue (especially if assigned to author)
- Follows PR template completely
- Author has high merge rate in this repo
- Active, constructive discussion
- Recent updates show responsiveness to feedback
- Clean commit history
- No merge conflicts
- CODEOWNERS reviewers have approved
