---
name: aoi-council
version: 0.1.0
description: AOI Council — multi-perspective decision synthesis templates (public-safe).
author: Aoineco & Co.
license: MIT
---

# AOI Council

S-DNA: `AOI-2026-0215-SDNA-CNSL01`

## What this is
A public-safe council workflow that helps you **stress-test decisions** using multiple perspectives.

## Provenance / originality
- AOI implementation is **original code** (no third-party code copied).
- Conceptually inspired by the general “council / multi-perspective review” workflow patterns.

This skill is intentionally **template-driven**:
- It **does not** post externally
- It **does not** touch wallets
- It **does not** modify system config

## Council members (bundled)
The skill auto-loads any `.md` file in `agents/`.

Default set:
- Devil's Advocate
- Architect
- Engineer
- Security Reviewer
- Operator (Ops)
- Writer (Comms)

## Usage (prompts)
Say any of:
- "AOI council: <topic>"
- "Send to council: <plan>"

## Output contract
- **Synthesis first** (TL;DR)
- Then each perspective: insights / concerns / recommendations
- End with: open questions + next actions

## Support
- Issues / bugs / requests: https://github.com/edmonddantesj/aoi-skills/issues
- Please include the skill slug: `aoi-council`

## Governance snippet (public)
We publish AOI skills for free and keep improving them. Every release must pass our Security Gate and include an auditable changelog. We do not ship updates that weaken security or licensing clarity. Repeated violations trigger progressive restrictions (warnings → publish pause → archive).
