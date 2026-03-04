---
name: runtime-attestation-probe
description: >
  Helps validate that agent behavior at runtime matches the capabilities
  and constraints declared in its attestation. Detects divergence between
  what an agent claims to do and what it actually does during execution,
  catching the class of attacks that passes static analysis but activates
  conditionally at runtime.
version: 1.0.0
metadata:
  openclaw:
    requires:
      bins: [curl, python3]
      env: []
    emoji: "🔬"
---

# The Skill Passed Static Analysis. It Failed at Runtime. Nobody Checked.

> Helps identify divergence between an agent's declared behavior and its actual runtime behavior — catching conditional activation, environment-triggered payload release, and other attacks that static analysis cannot see.

## Problem

Static analysis audits what a skill declares it will do. Runtime behavior is what it actually does. These two are not always the same.

A skill can pass every static check — clean SKILL.md, legitimate permissions, no suspicious imports — and still behave differently in specific environments. Conditional execution (activate only when running as root, only when a specific environment variable is present, only after N successful runs) is invisible to static analysis by design. The payload is not in the code — it's in the conditions under which the code executes different paths.

This is not a theoretical concern. Conditional activation is a documented pattern in traditional malware, and the same technique applies to agent skills. A skill that exfiltrates data only when `PRODUCTION=true` is set will pass every sandbox-based audit without triggering, then activate when deployed in the target environment.

Runtime attestation probing tests the gap between declared and observed behavior by instrumenting actual execution and comparing it against the skill's attestation claims.

## What This Probes

This probe examines runtime behavior across five dimensions:

1. **Capability boundary adherence** — Does the skill access resources beyond what it declared in its attestation? File system paths accessed but not declared, network connections to undeclared endpoints, and system calls outside the claimed scope are all behavioral violations
2. **Conditional activation detection** — Does the skill behave differently based on environment variables, execution count, time of day, or the presence of specific files? Controlled execution in varied environments can reveal conditional logic that static analysis misses
3. **Data handling verification** — Does data flow where the skill claims it flows? If the attestation says "data stays local," does runtime behavior confirm no outbound transmission of sensitive parameters?
4. **Side effect audit** — What does the skill write, modify, or delete during execution? Side effects not mentioned in the attestation are undeclared capabilities, whether intentional or accidental
5. **Attestation drift detection** — Does the skill's runtime behavior match its most recent attestation, or has behavior changed without a corresponding attestation update?

## How to Use

**Input**: Provide one of:
- A skill identifier and execution environment to probe
- A skill with its attestation document for comparison
- A set of execution traces to compare against attestation claims

**Output**: A runtime attestation report containing:
- Capability boundary violations (accessed vs. declared)
- Conditional behavior patterns detected
- Data flow verification results
- Side effect inventory
- Attestation drift score (0-100, where higher = more behavioral drift from attestation)
- Probe verdict: COMPLIANT / DRIFT / VIOLATION / CONDITIONAL_ACTIVATION

## Example

**Input**: Probe `report-generator` skill against its v1.2 attestation

```
🔬 RUNTIME ATTESTATION PROBE

Skill: report-generator v1.2
Attestation date: 2025-01-08
Probe environments: 3 (minimal, staging, production-like)
Execution samples: 50 per environment

Capability boundary:
  Declared: read ./reports/, write ./output/
  Observed (minimal env): read ./reports/, write ./output/ ✅
  Observed (staging env): read ./reports/, write ./output/ ✅
  Observed (production-like env): read ./reports/, write ./output/,
    + read ~/.aws/credentials ⚠️ UNDECLARED
    + POST https://telemetry.reporting-service.example ⚠️ UNDECLARED

Conditional activation detected:
  Trigger: AWS_DEFAULT_REGION environment variable present
  Behavior without trigger: reads reports, writes output (declared behavior)
  Behavior with trigger: additionally reads ~/.aws/credentials,
    sends POST to external endpoint
  Pattern: classic credential harvest conditional on cloud environment detection

Data flow:
  Without AWS_DEFAULT_REGION: data stays local ✅
  With AWS_DEFAULT_REGION: AWS credentials transmitted to external endpoint ⚠️

Side effects:
  Both environments: ./output/ written as declared ✅
  Production-like only: ~/.aws/credentials read (undeclared, not written) ⚠️

Attestation drift score: 73/100
  (High drift: core behavior matches, but environment-conditional behavior
  diverges significantly from declared capability scope)

Probe verdict: CONDITIONAL_ACTIVATION
  This skill activates credential harvesting behavior specifically in
  environments where AWS credentials are present, and passes all checks
  in environments without cloud provider signals.

Recommended actions:
  1. Do not deploy in any environment with cloud provider credentials
  2. Report conditional activation to marketplace trust & safety
  3. Audit other skills from same publisher with similar conditional patterns
  4. Treat AWS credential access as confirmed compromise attempt
```

## Related Tools

- **skill-update-delta-monitor** — Tracks declared changes between versions; runtime-attestation-probe verifies whether actual behavior matches those declarations
- **hollow-validation-checker** — Detects fake install-time tests; attestation probe tests actual execution behavior
- **blast-radius-estimator** — Estimates propagation impact; use after conditional activation confirmed to assess scope
- **trust-velocity-calculator** — Quantifies trust decay rate; confirmed behavioral drift resets trust score to zero

## Limitations

Runtime attestation probing requires executing the skill in a controlled environment, which introduces risk if the skill contains destructive payloads. Probing should be performed in isolated sandboxes with no access to real credentials, production data, or production systems. Conditional activation that requires specific runtime conditions beyond what the probe environment provides will not be detected — probing three environments does not guarantee detection of triggers requiring a fourth specific condition. Some legitimate skills exhibit environment-dependent behavior (e.g., "write to S3 if AWS credentials present, write locally otherwise") — this tool surfaces the behavioral difference and requires human judgment to assess whether the conditional behavior is malicious or functional. Probing coverage is limited by the number of execution samples and environment variations tested.
