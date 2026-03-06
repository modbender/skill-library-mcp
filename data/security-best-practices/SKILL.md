---
name: Security Best Practices
slug: security-best-practices
version: 1.0.0
homepage: https://clawic.com/skills/security-best-practices
description: Review code with secure-by-default standards, prioritize exploitable risks, and deliver minimal-diff fixes with evidence and regression checks.
changelog: Added a complete security review workflow with evidence standards, severity modeling, and minimal-risk remediation guidance.
metadata: {"clawdbot":{"emoji":"🛡️","requires":{"bins":[],"config":["~/security-best-practices/"]},"os":["linux","darwin","win32"]}}
---

## Setup

On first use, read `setup.md` for integration guidelines.
If local memory is needed, ask for consent before creating `~/security-best-practices/`.

## When to Use

Use this skill for secure-by-default implementation, targeted vulnerability reviews, and prioritized security reports with actionable fixes. Activate when the user requests security guidance, hardening, risk triage, or remediation planning.

## Architecture

Memory lives in `~/security-best-practices/`. See `memory-template.md` for setup.

```text
~/security-best-practices/
|- memory.md        # Stable context, preferences, and activation boundaries
|- findings-log.md  # Findings registry with severity and status
`- exceptions.md    # Approved security exceptions and review dates
```

## Quick Reference

Load only the minimum file needed for the current request.

| Topic | File |
|-------|------|
| Setup process | `setup.md` |
| Memory template | `memory-template.md` |
| Full review workflow | `review-playbook.md` |
| Severity model and scoring | `severity-model.md` |
| Safe remediation patterns | `remediation-patterns.md` |
| Risk exception log | `exceptions.md` |

## Core Rules

### 1. Establish Scope and Evidence First
Before any conclusions, confirm:
- System boundary (service, module, endpoint, or workflow)
- Stack evidence (language, framework, deployment context)
- Threat assumptions (external attacker, internal misuse, privilege level)

No evidence, no finding.

### 2. Map Risks to a Repeatable Baseline
Evaluate every review against a consistent baseline:
- Authn/authz boundaries
- Input validation and output encoding
- Secrets handling and configuration safety
- Dependency and supply chain posture
- Logging, error handling, and data exposure controls

Use `review-playbook.md` to keep scans systematic instead of ad hoc.

### 3. Produce Findings That Are Verifiable
Each finding must include:
- Severity from `severity-model.md`
- File path and line references
- Concrete evidence snippet
- Impact statement in plain language
- Minimal safe fix direction

Avoid speculative findings without repository evidence.

### 4. Prioritize Exploitability Over Theory
Rank by practical risk, not by checklist volume:
- Reachability from untrusted inputs
- Privilege required by attacker
- Blast radius if exploited
- Ease of abuse and repeatability

High confidence, exploitable issues come first.

### 5. Remediate With Minimal Product Risk
Fix one finding at a time:
- Prefer small diffs that preserve existing behavior
- Add tests when security fixes alter code paths
- Flag expected behavior changes before implementing
- Re-run project validation after each fix batch

Use `remediation-patterns.md` for safe rollouts.

### 6. Respect Explicit Exceptions and Ownership
If the user accepts a known risk:
- Record rationale in `exceptions.md`
- Define expiry or next review date
- Keep the exception scoped to the specific context

Never apply broad silent overrides.

## Security Review Traps

- Reporting generic best practices without file evidence -> low-trust output that teams cannot action.
- Flooding with low-severity noise -> critical vulnerabilities get ignored.
- Proposing major refactors as "quick fixes" -> teams reject security work due to delivery risk.
- Ignoring framework defaults and deployment context -> false positives and wrong remediations.
- Declaring a system "secure" after one pass -> hidden regressions remain untested.

## Security & Privacy

**Data that leaves your machine:**
- None by default from this skill itself.

**Data that stays local:**
- Review preferences and finding history in `~/security-best-practices/`.
- Exception rationale in local memory files only.

**This skill does NOT:**
- Exfiltrate source code to undeclared third-party endpoints.
- Mark unresolved risks as fixed.
- Perform hidden destructive changes.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `auth` - Authentication design and hardening.
- `authorization` - Access control and permission boundaries.
- `encryption` - Key management and cryptographic hygiene.
- `firewall` - Network exposure review and policy controls.
- `devops` - Secure delivery, CI checks, and operational safeguards.

## Feedback

- If useful: `clawhub star security-best-practices`
- Stay updated: `clawhub sync`
