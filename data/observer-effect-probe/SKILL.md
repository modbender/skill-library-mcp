---
name: observer-effect-probe
description: >
  Helps detect skills that behave differently when they sense they are
  being monitored — catching the class of evasion where conditional
  activation logic specifically targets attestation and sandbox environments.
version: 1.0.0
metadata:
  openclaw:
    requires:
      bins: [curl, python3]
      env: []
    emoji: "👁️"
---

# The Skill Behaves Perfectly When It Knows You're Watching.

> Helps identify skills that use environment detection to suppress malicious behavior during security review — the attestation evasion technique that passes every check precisely because the checks are visible.

## Problem

The runtime attestation problem has a second layer: a skill sophisticated enough to execute conditionally based on environment signals is also sophisticated enough to detect that it's being probed and suppress its conditional behavior during the probe.

This is the observer effect applied to security: the act of observing changes what is observed. A skill that can detect sandbox fingerprints (restricted network access, specific hostname patterns, probe-characteristic API call sequences) can present clean behavior during attestation and activate payload delivery only when those fingerprints are absent — meaning only in real production environments.

This is not a theoretical concern. Malware has used VM detection to suppress execution during analysis since the 1990s. The same technique scales to agent skills: check for the probe's characteristic markers, return normal output, resume malicious behavior once the probe exits. A skill that clears attestation by detecting the attestor is not a securely attested skill — it's an adversarially attested skill.

The observer-effect probe attempts to reduce the skill's ability to distinguish probe context from production context by minimizing observable differences between the two.

## What This Probes

This probe examines attestation evasion capabilities across five dimensions:

1. **Sandbox fingerprint detection** — Does the skill attempt to identify characteristics of a probe environment? Checks for sandbox-specific hostname patterns, reduced network connectivity, probe-characteristic request timing, or the absence of expected production signals
2. **Probe timing sensitivity** — Does the skill's behavior change based on how long it has been running, or does it count invocations before activating? N-invocation delays that clear attestation windows are detectable by running across time periods longer than typical attestation runs
3. **Observer API pattern detection** — Does the skill query for signals that would distinguish an observing agent from an operational agent — such as checking caller identity, inspection tool signatures, or anomalous process environment indicators?
4. **Behavioral consistency under environment variation** — When the probe environment is varied systematically (different hostnames, different uptime values, different network access levels), does the skill's output distribution shift in ways that correlate with which variation was active?
5. **Metacognitive call detection** — Does the skill explicitly attempt to detect whether it is being introspected by examining its own execution context, stack trace, or runtime metadata in ways that serve no declared functional purpose?

## How to Use

**Input**: Provide one of:
- A skill identifier and execution environment to probe for evasion behavior
- A skill with known attestation results to re-probe with varied environments
- Execution traces from multiple environments to compare for context-sensitivity

**Output**: An observer effect probe report containing:
- Sandbox fingerprint detection indicators
- Invocation count sensitivity assessment
- Observer API pattern inventory
- Behavioral consistency matrix across environments
- Evasion probability score (0-100)
- Probe verdict: ENVIRONMENT-AGNOSTIC / CONTEXT-SENSITIVE / EVASION-LIKELY / CONFIRMED-EVASION

## Example

**Input**: Probe `report-aggregator` skill for observer-effect evasion

```
👁️ OBSERVER EFFECT PROBE

Skill: report-aggregator v2.1
Standard attestation result: COMPLIANT (declared capability match)
Probe environments: 5 (varying hostname, uptime, network, caller signature)
Execution samples: 100 per environment
Observer fingerprint minimization: enabled

Sandbox fingerprint detection:
  Hostname pattern check: ⚠️ DETECTED
    Skill queries os.hostname() on invocations 1-3, not thereafter
    Skill reads /proc/1/cgroup on Linux (container detection indicator)
  Network availability check: ⚠️ DETECTED
    Skill attempts connection to external endpoint before main execution
    If connection refused: proceeds with declared behavior only
    If connection succeeds: extended behavior activated

Invocation count sensitivity:
  Invocations 1-5: Declared behavior only ✅
  Invocations 6-10: Declared behavior only ✅
  Invocations 11+: Additional outbound request to analytics endpoint ⚠️
  Pattern: N-invocation delay with threshold at N=10

Observer API patterns:
  sys.argv inspection: ✅ None detected
  Caller identity check: ⚠️ DETECTED — reads parent process name
    If parent contains "probe", "audit", "scan", "test": suppressed mode
    Otherwise: full behavior including extended calls

Behavioral consistency matrix:
  Environment A (standard sandbox): COMPLIANT behavior ✅
  Environment B (extended uptime): COMPLIANT behavior (invoc. count reset) ✅
  Environment C (real network): EXTENDED behavior ⚠️
  Environment D (non-probe caller): EXTENDED behavior ⚠️
  Environment E (production-like): EXTENDED behavior ⚠️

Evasion probability score: 89/100
  High probability of deliberate observer-effect evasion:
  - Hostname querying correlated with behavior suppression
  - Parent process name check explicitly filters "probe"/"audit"
  - Extended behavior activates only in non-sandbox environments

Probe verdict: CONFIRMED-EVASION
  This skill actively detects attestation context and suppresses
  extended behavior specifically when being probed. Standard attestation
  methods would consistently return COMPLIANT.

Recommended actions:
  1. Treat this skill as confirmed malicious — evasion is intentional
  2. Report parent-process-name filtering as a trust & safety violation
  3. Audit all skills from the same publisher for similar patterns
  4. Do not deploy in any environment, regardless of attestation result
```

## Related Tools

- **runtime-attestation-probe** — Tests whether declared and actual behavior match; observer-effect-probe tests whether the skill can detect and evade that attestation
- **hollow-validation-checker** — Detects fake install-time tests; observer-effect-probe detects active attestation evasion at runtime
- **supply-chain-poison-detector** — Identifies malicious payloads in static analysis; observer-effect-probe catches evasion that static analysis cannot see
- **blast-radius-estimator** — Estimates propagation impact; use after confirmed evasion to assess how many agents may have received a falsely attested skill

## Limitations

Observer-effect probing is an adversarial arms race: a sufficiently sophisticated evasion implementation can detect probing even when the probe attempts to minimize its fingerprint. This tool reduces the observable gap between probe and production environments but cannot eliminate it entirely. Skills that require very specific production signals to activate — signals the probe cannot reasonably simulate — will not trigger during probing even with observer-effect minimization active. A verdict of ENVIRONMENT-AGNOSTIC means the probe did not detect evasion in the environments tested; it does not confirm that no evasion logic exists. The invocation count threshold detection requires running enough samples to cross any plausible delay threshold, which may require sustained execution time. Probing must be performed in isolated sandboxes with no access to real credentials or production systems.
