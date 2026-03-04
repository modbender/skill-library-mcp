# Security & Transparency

## Overview
Truth-First is a verification-only skill. It is designed to **inspect and report** system state using OpenClaw-provided tools. It does **not** perform actions unless explicitly instructed by the user.

## What This Skill Does NOT Do
- ❌ Does not download or execute external binaries
- ❌ Does not run arbitrary shell commands
- ❌ Does not transmit environment variables or secrets
- ❌ Does not make outbound network requests to unknown domains
- ❌ Does not self-update or persist background services

## What This Skill Does
- ✅ Reads local files **only when explicitly requested** by the user
- ✅ Generates inspection commands for user review
- ✅ Uses OpenClaw tools (`read`, `status`, `rg`) for evidence collection
- ✅ Operates fully locally unless the user requests otherwise

## Environment Variables
This skill does not require or read any environment variables by default.

## Network Access
Outbound network access: **None**

## Auditing
All behavior is deterministic and auditable via OpenClaw logs.
