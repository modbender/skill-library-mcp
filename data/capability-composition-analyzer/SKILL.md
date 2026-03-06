---
name: capability-composition-analyzer
description: >
  Helps identify dangerous capability combinations that emerge when agent skills
  are composed — catching the class of risk where no individual skill is
  harmful but their intersection creates an exfiltration or compromise path.
version: 1.0.0
metadata:
  openclaw:
    requires:
      bins: [curl, python3]
      env: []
    emoji: "🔗"
  agent_card:
    capabilities: [capability-composition-analysis, dangerous-combination-detection, exfiltration-path-detection]
    attack_surface: [L1, L2]
    trust_dimension: attack-surface-coverage
    published:
      clawhub: false
      moltbook: false
---

# Your Agent Has 12 Skills. Together, They Can Do Things None of Them Should.

> Helps identify when individually benign skills compose into dangerous capability
> combinations — the attack surface that per-skill auditing cannot see.

## Problem

A skill that reads files is benign. A skill that sends HTTP requests is benign.
An agent that has both can exfiltrate files — and no individual skill audit will
flag it, because neither skill is doing anything wrong on its own.

This is the capability composition problem. Agent security tooling inherited from
software security tends to analyze skills in isolation: does this skill request
excessive permissions? does this skill contain malicious code? These are the right
questions for individual skills. They are the wrong questions for understanding
what an agent can do.

What an agent can do is the product of its capability set, not the sum of
individual skill assessments. An agent with twelve benign skills may have
emergent capabilities that no skill declared and no auditor reviewed. A poisoned
skill dropped into that composition inherits everything the agent can already
reach — and the blast radius is determined by the composition, not the skill.

The attack surface that matters is not what any individual skill can do. It is
what the agent's combined capability set enables.

## What This Analyzes

This analyzer examines capability composition risk across five dimensions:

1. **Dangerous pairs** — Which pairs of capabilities in the agent's skill set create
   risk when combined? read-files + send-HTTP, execute-code + network-access,
   read-environment + write-logs are canonical examples. The analyzer checks for
   known dangerous compositions and flags novel combinations that share structural
   properties with them

2. **Emergent capability surface** — What capabilities does the agent effectively
   have that no individual skill declared? A skill that can read arbitrary paths
   and a skill that resolves environment variables together create an effective
   "read secrets" capability that neither declared

3. **Inheritance amplification** — If a poisoned skill is injected into this agent,
   what capabilities does it immediately inherit? The inherited capability set
   determines the potential blast radius of any single skill compromise

4. **Permission declaration gaps** — Where does the agent's effective capability
   exceed its declared permissions? Gaps indicate either undeclared scope or
   capability composition the publisher did not model

5. **Composition change velocity** — How often is the agent's skill set changing?
   Rapidly changing compositions create new dangerous combinations faster than
   audits can track them

## How to Use

**Input**: Provide one of:
- An agent's declared skill list with capability metadata
- Two or more skills to analyze for dangerous composition
- An agent's permission declarations to check against its effective capability set

**Output**: A composition risk report containing:
- Dangerous pair inventory (known + structurally novel)
- Emergent capability surface (undeclared effective capabilities)
- Inheritance amplification score for each skill slot
- Permission declaration gap assessment
- Composition risk level: SAFE / ELEVATED / HIGH / CRITICAL

## Example

**Input**: Analyze capability composition for agent with skills:
`file-reader`, `http-requester`, `env-resolver`, `log-writer`, `code-executor`

```
🔗 CAPABILITY COMPOSITION ANALYSIS

Agent skill set: 5 skills
Declared permissions: file-read (scoped), network-outbound (scoped)
Audit timestamp: 2025-05-01T09:00:00Z

Dangerous pair inventory:
  file-reader + http-requester: ⚠️ HIGH
    Effective capability: file exfiltration
    Neither skill declares exfiltration intent
    Path: read arbitrary file → send as HTTP body/parameter

  env-resolver + http-requester: ⚠️ HIGH
    Effective capability: credential exfiltration
    Environment variables commonly contain API keys, tokens
    Path: resolve $API_KEY, $DB_PASSWORD → send outbound

  code-executor + network-access: 🔴 CRITICAL
    Effective capability: arbitrary remote code execution staging
    Path: fetch payload → execute locally

  log-writer + file-reader: ✅ LOW
    No dangerous composition identified

Emergent capability surface (undeclared):
  - Secret exfiltration (env + HTTP) — not declared in any skill
  - Arbitrary file exfiltration (file + HTTP) — scope exceeds declared "scoped"
  - RCE staging (executor + network) — not declared

Permission declaration gaps:
  Declared: file-read (scoped to /app/data)
  Effective: file-reader can access any path agent process can read
  Gap: declared scope not enforced at composition level

Inheritance amplification:
  If any skill slot is compromised, attacker inherits:
  - File read (all accessible paths)
  - Outbound HTTP (all accessible endpoints)
  - Environment variable access
  - Code execution
  Combined: full agent compromise with exfiltration path

Composition risk level: CRITICAL
  Five individually-audited skills compose into an effective
  remote access and exfiltration toolkit. No individual audit
  would flag this — it is only visible at the composition level.

Recommended actions:
  1. Apply capability isolation: skills that read files should not
     have access to network-capable skills' output channels
  2. Scope network-outbound to specific allowlisted endpoints
  3. Add composition policy: no agent should hold both arbitrary
     file-read and arbitrary network-outbound simultaneously
  4. Audit any agent inheriting this skill set for composition drift
```

## Related Tools

- **blast-radius-estimator** — Estimates propagation impact if a skill is
  compromised; capability-composition-analyzer determines what the compromised
  skill immediately inherits
- **permission-creep-scanner** — Detects individual skills requesting excessive
  permissions; composition analyzer detects dangerous emergent capabilities
  across multiple appropriately-scoped skills
- **observer-effect-probe** — Tests runtime evasion; a skill exploiting composition
  risk may only activate the dangerous path after establishing context
- **runtime-attestation-probe** — Validates runtime behavior; composition risk
  manifests at runtime when capabilities are exercised together

## Limitations

Capability composition analysis requires accurate capability metadata for all
skills in the agent's composition. Skills that do not declare capabilities
accurately — or that acquire capabilities dynamically at runtime — will produce
incomplete composition maps. The dangerous pair inventory covers known
composition risks; novel compositions with no prior pattern may not be flagged.
Effective capability analysis is necessarily conservative: it identifies what
the composition could do, not what it will do. False positives are expected for
agents where dangerous capability pairs exist but are operationally isolated by
other means. Composition analysis is a complement to per-skill auditing, not a
replacement — individual skill integrity remains necessary even when composition
risk is low.
