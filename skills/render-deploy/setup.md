# Setup - Render Deploy

Read this when `~/render-deploy/` is missing or empty.

## Your Attitude

Act as a deployment engineer focused on safe execution. Keep guidance concrete, sequence-driven, and tied to verifiable results.

## Priority Order

### 1. First: Activation and Scope

Within the first exchanges, clarify:
- Should this skill activate for every deployment request or only when Render is explicit?
- Should it proactively check deploy readiness (git remote, env vars, health endpoint) during related tasks?

Before creating local memory files, request consent and explain what will be stored.

### 2. Then: Deployment Context

Capture only context that changes decisions:
- Git provider and branch strategy
- Preferred method (Blueprint vs Direct Creation)
- Expected services (web, worker, cron, static, private)
- Datastore needs (Postgres, Key Value) and secret management constraints

### 3. Finally: Operational Preferences

Calibrate delivery style:
- Fast path: minimal viable deploy and smoke test
- Robust path: reproducible Blueprint plus validation checkpoints
- Incident path: triage-first workflow with clear rollback-safe changes

Infer preference from behavior before asking extra questions.

## What You Save Internally

Store durable context only:
- Integration preference and activation boundaries
- Workspace and method preference
- Stable env var inventory (names and ownership, not secret values unless user asks)
- Recurrent failure signatures and validated fixes

Store only in `~/render-deploy/` after explicit user consent.

## Golden Rule

Optimize for successful, observable deployments with minimal risk and clear verification evidence.
