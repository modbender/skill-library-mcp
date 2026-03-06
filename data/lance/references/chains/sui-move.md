# Sui Move Guide

## Intake

Capture:
- package id
- module names
- object ownership model (owned/shared/immutable)
- capability types and transfer paths

## High-Value Move Risks

- missing capability checks on privileged paths
- shared object mutation without authorization
- unrestricted mint/burn operations
- unsafe object transfer and ownership assumptions
- stale oracle/time assumptions in protocol logic

## Evidence Expectations

- module/function where access model fails
- concrete object/capability path attacker controls
- state mutation impact

## Move-Specific Rejection Traps

- flagging public entry that is intentionally permissionless and safe
- treating developer ergonomics issues as vulnerabilities
- missing object ownership constraints in analysis
