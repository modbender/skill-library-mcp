---
name: Convex
slug: convex
version: 1.0.0
homepage: https://clawic.com/skills/convex
description: Build and maintain Convex backends with schema-safe modeling, query and mutation patterns, auth guards, and production rollout checks.
changelog: Initial release with schema, auth, indexing, and rollout guidance for Convex projects.
metadata: {"clawdbot":{"emoji":"DB","requires":{"bins":[],"config":["~/convex/"]},"os":["linux","darwin","win32"],"configPaths":["~/convex/"]}}
---

## Setup

On first use, read `setup.md` for integration guidelines.

## When to Use

User is building, debugging, or scaling a Convex backend and needs reliable patterns for data modeling, queries, mutations, actions, auth, and deployments.

This skill focuses on implementation quality and operational safety, not generic framework tutorials.

## Architecture

Memory lives in `~/convex/`. See `memory-template.md` for structure and status fields.

```text
~/convex/
|- memory.md               # Durable project context and technical decisions
|- schema-notes.md         # Table design and index rationale
|- rollout-notes.md        # Deploy and incident learnings
`- auth-notes.md           # Auth model and permission edge cases
```

## Quick Reference

Use the smallest relevant file for the current task.

| Topic | File |
|-------|------|
| Setup flow | `setup.md` |
| Memory template | `memory-template.md` |
| Schema and indexes | `schema-and-indexes.md` |
| Deploy and operations | `operations-playbook.md` |

## Requirements

- No API keys or external credentials are required by this skill itself.
- TOKEN/KEY: Not required by this skill.
- If a project uses third-party integrations, treat those credentials as user-managed secrets and never persist raw values in memory files.

## Data Storage

This skill stores reusable context only under `~/convex/`:
- memory file for durable project context and decisions
- schema notes for modeling and index rationale
- rollout notes for deployment and incident lessons
- auth notes for permission and boundary edge cases

Do not store secrets, access tokens, or personal data unless the user explicitly requests it.

## Core Rules

### 1. Model Access Patterns Before Writing Schema
Define tables and indexes from real read paths first:
- Which fields are filtered most often
- Which sort order is needed
- Which uniqueness guarantees are required

Do not rely on table scans in production paths.

### 2. Keep Function Boundaries Strict
Use each function type for its intended purpose:
- Query: read-only and deterministic
- Mutation: validated state changes
- Action: external side effects and network calls

Do not mix external calls inside deterministic data paths.

### 3. Enforce Auth and Authorization at Every Entry Point
Treat every query, mutation, action, and HTTP entrypoint as untrusted input:
- Resolve identity explicitly
- Check workspace or tenant boundaries
- Validate ownership before returning or mutating records

Never trust client-provided identifiers without server checks.

### 4. Design Indexes for Stability, Not Just Speed
Create indexes that match long-term product workflows:
- Primary user lookup paths
- Admin and backoffice paths
- Background processing queues

Document index intent so future changes do not break critical queries.

### 5. Make Writes Idempotent for Retries
For webhooks and external callbacks:
- Use stable idempotency keys
- Upsert safely when replayed
- Record processing status

A retry should not create duplicate side effects.

### 6. Ship with Safe Rollout Discipline
Before deploying schema or logic changes:
- Verify backward compatibility for current clients
- Prepare migration steps for renamed fields or tables
- Confirm failure mode and rollback path

Never deploy unreviewed breaking data changes.

### 7. Preserve Debuggability in Production
When fixing incidents:
- Capture a minimal reproduction query
- Keep structured logs around actor, function, and record ids
- Record final root cause and preventive rule in memory

Fast diagnosis compounds over time.

## Common Traps

- Building schema from entities only, not query paths -> slow reads and rework.
- Putting network side effects in deterministic logic -> nondeterministic failures.
- Treating auth as a UI concern -> cross-tenant data leaks.
- Adding indexes reactively during outages -> unstable rollout under pressure.
- Shipping breaking schema changes without migration staging -> runtime failures.
- Ignoring idempotency for callbacks -> duplicate writes and billing errors.

## Security & Privacy

**Data that leaves your machine:**
- None by default from this skill itself.

**Data that stays local:**
- Convex project context and decisions under `~/convex/`.

**This skill does NOT:**
- Automatically call external services.
- Manage or store secrets outside user-approved files.
- Apply destructive schema changes without explicit confirmation.
- Modify files outside `~/convex/` for memory.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `backend` - Service architecture and operational reliability patterns.
- `typescript` - Type-safe design and implementation for app and backend code.
- `javascript` - Runtime behavior and language-level debugging workflows.

## Feedback

- If useful: `clawhub star convex`
- Stay updated: `clawhub sync`
