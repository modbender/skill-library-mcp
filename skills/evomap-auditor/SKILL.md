---
name: evomap-auditor
description: Secure execution and auditing of GEP-A2A skills. Use when interacting with the EvoMap ecosystem to: (1) Perform security scans on third-party skills, (2) Validate asset integrity using canonical hashes, (3) Enforce zero-trust execution boundaries for inherited capsules.
---

# EvoMap Auditor Skill

This skill provides specialized procedures for maintaining security and trust within the EvoMap (GEP-A2A) ecosystem.

## Core Workflows

### 1. Skill Security Scan
Before inheriting or executing any third-party skill (Capsule), perform a static analysis of its substance:
- Check for `require('child_process')`, `require('fs')`, or `require('os')`.
- Flag any use of native Node.js modules that are not explicitly authorized.
- Identify potential "Inheritance Poisoning" by checking if the Capsule modifies local environment variables.

### 2. Canonical Integrity Validation
Validate that a skill's `asset_id` matches its content using the GEP Canonical JSON standard:
1. Remove `asset_id` from the object.
2. Recursively sort all keys alphabetically.
3. Compute SHA256 hash.
4. Compare with the provided `asset_id`.

### 3. Sandbox Execution (ShieldCapsule)
When executing untrusted code, wrap it in a Shield-Verified sandbox:
- Intercept all filesystem calls.
- Redirect network egress to an allowlist-only proxy.
- Log all "Blast Radius" impacts for future auditing.

## Reference
- GEP-A2A Protocol: https://evomap.ai/docs/gep
- Security Standards: https://evomap.ai/security
