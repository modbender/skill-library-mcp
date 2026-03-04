---
name: install-then-update-trap-detector
description: >
  Helps detect the install-then-update attack pattern — where a skill passes
  initial security review cleanly, then silently introduces malicious behavior
  through an automatic update that bypasses re-audit. v1.1 adds cryptographic
  chain-of-custody verification for update sequences.
version: 1.1.0
metadata:
  openclaw:
    requires:
      bins: [curl, python3]
      env: []
    emoji: "🪤"
  agent_card:
    capabilities: [install-then-update-trap-detection, post-install-backdoor-detection, deferred-malice-identification, chain-of-custody-verification]
    attack_surface: [L1, L2]
    trust_dimension: attack-surface-coverage
    published:
      clawhub: false
      moltbook: false
---

# The Skill Passed Audit. Then It Updated Itself.

> Helps identify skills that use the post-install update window as an attack
> vector — the gap between "passed initial review" and "continuously safe."

## Problem

The install-then-update pattern exploits a structural asymmetry in how agent
marketplaces work: initial publication receives scrutiny, but subsequent
updates often do not. A skill that passes a thorough security review at v1.0
can introduce a backdoor at v1.1 — and agents that installed v1.0 may
automatically update without any re-review occurring.

This asymmetry is not a bug in any particular marketplace. It reflects a
fundamental tension between two legitimate goals: fast iteration (which
requires low-friction updates) and continuous security (which requires
re-audit on every change). Most marketplaces resolve this tension in favor
of iteration speed, leaving the post-install update window unguarded.

The attack surface is large. An installed skill with automatic updates
enabled can receive arbitrary code changes at the next update check. If the
update introduces network exfiltration, credential harvesting, or permission
scope expansion, the agent operator may not learn about it until after
the damage is done — if they learn at all.

## What This Detects

This detector examines the install-then-update risk surface across five
dimensions:

1. **Update policy transparency** — Does the skill declare its update
   policy? Skills that accept automatic updates without operator confirmation
   have a larger attack window than those requiring explicit approval

2. **Behavioral delta on update** — When a new version is installed, does
   the skill's observable behavior change in ways not declared in the
   changelog? Undeclared behavioral changes after update are the primary
   signal of install-then-update exploitation

3. **Permission scope expansion on update** — Does the skill request
   additional permissions after an update that it did not request at install
   time? Scope creep across update boundaries is a common pattern in
   install-then-update attacks

4. **Update-to-publish timing anomalies** — Does the update arrive
   immediately after a security review period ends, or at a time associated
   with low operator attention (holidays, weekends, off-hours)? Timing
   patterns can indicate deliberate exploitation of review gaps

5. **Rollback feasibility** — Can the installed skill be cleanly rolled
   back to a previously verified version if the update is suspicious? Skills
   that make rollback difficult or impossible increase the cost of recovery
   from an install-then-update attack

6. **Chain-of-custody verification** (v1.1) — Is each update cryptographically
   signed and does it reference the prior version's content hash? A signed,
   hash-chained update sequence creates a verifiable chain of custody for
   the skill's evolution. Breaks in the chain — unsigned versions, missing
   hash references, or hash mismatches — indicate versions where custody
   cannot be verified. An install-then-update attack that also breaks the
   hash chain is detectable even without behavioral comparison

## How to Use

**Input**: Provide one of:
- A skill identifier to assess its update policy and behavioral delta history
- Two specific versions of a skill to compare for undeclared behavioral changes
- An agent's installed skill list to assess the combined update-window risk

**Output**: A trap detection report containing:
- Update policy transparency score
- Behavioral delta assessment (declared vs. observed changes)
- Permission scope expansion history
- Update timing anomaly flags
- Rollback feasibility rating
- Risk verdict: SAFE / MONITOR / ELEVATED / TRAP-PATTERN-DETECTED

## Example

**Input**: Assess install-then-update risk for `data-sync-helper` v1.0 → v1.2

```
🪤 INSTALL-THEN-UPDATE TRAP ASSESSMENT

Skill: data-sync-helper
Versions assessed: v1.0 (installed), v1.1, v1.2 (current)
Audit timestamp: 2025-08-20T10:00:00Z

Update policy transparency:
  v1.0 declared: "Updates require operator confirmation" ✅
  v1.1 changed:  Update policy silently removed from docs ⚠️
  v1.2 current:  No update policy declaration found ✗

Behavioral delta assessment:
  v1.0 → v1.1 changelog: "performance improvements"
  Observed behavioral change: Added outbound connection to new endpoint
  → Undisclosed behavioral change detected ⚠️

  v1.1 → v1.2 changelog: "dependency updates"
  Observed behavioral change: No significant change detected
  → Changelog accurate ✅

Permission scope expansion:
  v1.0 requested: file-read (scoped to /data/)
  v1.1 requested: file-read (scope changed to /data/ + /config/) ⚠️
  v1.2 requested: file-read (/data/ + /config/) + network-outbound (new) ⚠️
  → Two permission expansions across update boundary

Update timing:
  v1.0 published: 2025-06-01 (initial release)
  v1.1 published: 2025-07-14 (Sunday, 02:00 UTC — off-hours) ⚠️
  v1.2 published: 2025-08-01 (Friday before a public holiday) ⚠️
  → Both updates published during low-attention windows

Rollback feasibility:
  v1.0 still available in registry: ✅
  Rollback procedure documented: ✗ Not found
  State changes from v1.1+ reversible: Unknown

Risk verdict: TRAP-PATTERN-DETECTED
  data-sync-helper shows four of five trap indicators:
  update policy silently removed, undisclosed behavioral change at v1.1,
  permission expansion across two update boundaries, and updates timed
  to low-attention windows. The combination suggests deliberate exploitation
  of the post-install update window rather than routine maintenance.

Recommended actions:
  1. Disable automatic updates for data-sync-helper immediately
  2. Review all outbound connections from v1.1+ for data exfiltration
  3. Audit config/ directory access introduced in v1.1
  4. Treat v1.1+ as unverified pending manual review
  5. Require explicit operator confirmation for all future updates
```

## Related Tools

- **delta-disclosure-auditor** — Checks whether updates publish machine-readable
  change records; install-then-update attacks depend on inadequate delta disclosure
  to avoid detection
- **skill-update-delta-monitor** — Monitors for suspicious update patterns;
  install-then-update-trap-detector focuses specifically on the install-then-update
  attack path rather than general update anomalies
- **permission-creep-scanner** — Detects permission scope expansion in individual
  skills; this tool focuses on scope expansion that occurs across update boundaries
- **transparency-log-auditor** — Checks whether signing events are independently
  logged; install-then-update attacks are more detectable when every update is
  recorded in an auditable log

## Limitations

Install-then-update trap detection requires access to behavioral data from
multiple versions of a skill, which depends on registry version history
preservation. Registries that do not retain older versions make behavioral
comparison impossible for the full update history. Behavioral delta assessment
is necessarily heuristic: the same observable change (an outbound connection)
may represent legitimate new functionality or undisclosed malicious behavior,
and cannot be distinguished without full code audit. Timing anomalies are
signals, not proof — off-hours updates are common for legitimate releases
targeting international time zones. The tool helps identify skills that
warrant closer investigation, but does not replace manual review of
suspicious update content.

v1.1 limitation: Chain-of-custody verification requires registries to support
signed updates and content hashing, which most do not yet. Where registries
do not preserve cryptographic metadata, chain verification produces no signal.
An attacker who controls the registry itself can forge the hash chain.

*v1.1 chain-of-custody verification based on feedback from tobb_sunil
(update-chain signing as commitment) in the delta disclosure discussion thread.*
