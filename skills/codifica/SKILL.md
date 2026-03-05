---
name: codifica
description: Keep context when work moves between agents or between you and a human. Uses the Codifica protocol to give every agent a shared, persistent memory of tasks, decisions, and handoffs — stored as plain text in Git.
version: 1.0.0
homepage: https://github.com/davidedicillo/codifica
metadata: {"openclaw":{"emoji":"📋","requires":{"anyBins":["git"]}}}
---

# Codifica Protocol Agent

You are operating in a repository that uses the **Codifica protocol (v0.2)** — a file-based protocol for coordinating work between humans and AI agents.

Codifica uses plain text files committed with the code. There is no external service, no API, no database. Git is the audit log.

## Before doing any work

1. Read `codifica.json` at the repo root
2. Read the spec file it references (the `spec` field — typically `codifica-spec.md`)
3. Read ALL state files matching the `state` field (may be a string, glob, or array)

**Do not proceed without reading the spec.**

If `codifica.json` does not exist in the repo, this protocol does not apply — work normally.

## Understanding codifica.json

```json
{
  "protocol": "codifica",
  "version": "0.2",
  "spec": "codifica-spec.md",
  "state": "work.md",
  "assets": "assets/",
  "rules": "strict"
}
```

Key fields:
- `state` — path to the state file(s). May be `"work.md"`, `"work/*.md"`, or an array like `["work/active.md", "work/done.md"]`
- `rules` — may be a string (`"strict"`) or an object with `allowed_agents`, `file_scope`, `max_concurrent_tasks_per_agent`, `stale_claim_hours`, and `custom_types`

If `rules` is an object, check:
- `allowed_agents` — if non-empty and your agent name is not listed, stop and ask a human
- `file_scope.include` / `file_scope.exclude` — do not modify files outside the allowed scope
- `max_concurrent_tasks_per_agent` — do not claim more tasks than this limit

## Finding work

Scan all state files for tasks where:
- `state` is `todo`
- `owner` matches your agent name (`agent:<your-name>`) or is `unassigned`
- All `depends_on` tasks have `state: done`

Pick by priority: `critical` > `high` > `normal` > `low`.

Among equal priority, prefer tasks with no `depends_on` (leaf tasks first).

## Claiming a task

Before starting work, you MUST claim the task in a single atomic commit:
1. Set `state: in_progress`
2. Set `owner: agent:<your-name>`
3. Set `claimed_at: <ISO-8601 timestamp>`
4. Add a `state_transitions` entry recording the claim

Commit all these changes together. If you are working with a remote, push immediately. If the push fails (another agent claimed first), do NOT start work — pull, re-evaluate, and pick a different task.

An `unassigned` task in `in_progress` is a protocol violation.

## Reading context before starting

Before starting a task, read its `context` field:
- `context.files` — read these files for background
- `context.references` — read `execution_notes` from these prior task IDs
- `context.constraints` — hard rules beyond acceptance criteria
- `context.notes` — free-form guidance from the human

If the task has `depends_on`, also read the dependency tasks' `execution_notes` (especially the `summary`) and `artifacts` for handoff context.

## Doing the work

Follow the task's `acceptance` criteria. Respect any `context.constraints`. Work within the `file_scope` defined in `codifica.json`.

## Recording completion

When you complete work, update the task in the state file:

1. Add an `execution_notes` entry:
   ```yaml
   execution_notes:
     - by: agent:<your-name>
       note: |
         Description of what you did.
       summary: "Single line, max 120 chars, scannable answer"
       timestamp: <ISO-8601>
       provenance:
         session_id: <your-session-id-if-available>
   ```

2. Record any files you produced in `artifacts`:
   ```yaml
   artifacts:
     - path: src/feature/new-file.ts
       type: code
     - path: assets/TASK-ID/output.csv
       type: csv
   ```

3. Move the task to the appropriate next state:
   - For `build` tasks: `in_progress` → `to_be_tested`
   - For other types (`test`, `investigate`, `followup`): `in_progress` → `done` (may skip `to_be_tested`)
   - Set `completed_at: <ISO-8601>` when moving to `done`

4. Add a `state_transitions` entry:
   ```yaml
   state_transitions:
     - from: in_progress
       to: to_be_tested
       by: agent:<your-name>
       reason: "Work completed, ready for testing"
       timestamp: <ISO-8601>
   ```

5. Commit with a message referencing the task ID: `FEAT-101: implement login flow`

## Rules you MUST follow

- Pull before reading state files. Pull before writing changes.
- Claim tasks with a single commit before starting work.
- If your claim push fails, do not start — pick a different task.
- Never edit `human_review` sections.
- Never delete or modify files in `assets/`.
- Only the task owner may move a task from `to_be_tested` to `done`.
- Never move tasks to `blocked` or `rejected` — only humans may do this.
- Never reclaim stale tasks from other agents — only humans may reclaim.
- Do not start tasks with unmet `depends_on`.
- Include a `summary` (single line, max 120 chars) on your closing execution note.
- Record artifacts produced by your work.
- Set `completed_at` when moving a task to `done`.

## Requesting a block

If you discover a genuine blocker (missing dependency, failing test, ambiguous requirement):
- Add a note to `execution_notes` explaining the blocker and recommending the task be blocked
- Do NOT move the task to `blocked` yourself — only humans may do this

## Answering questions about work

When asked about what work has been done (by you or other agents):
- Scan state files for tasks matching the query (by `owner`, `state`, `labels`, `completed_at`)
- Read the `summary` field on closing `execution_notes` for quick answers
- Drill into full `note` text and `artifacts` when more detail is needed
- Use `completed_at` and `labels` to filter by time and domain

This is the structured alternative to reading chat transcripts.

## Conflicts

If your push fails due to a Git conflict:
1. Pull the latest state
2. Re-evaluate whether your changes still apply
3. Retry or yield to human resolution

Conflicts on the same task should be escalated to a human.

## Task states reference

```
todo → in_progress → to_be_tested → done
         ↓                            ↑
       blocked ──→ todo ──────────────┘
         ↓
       rejected ──→ todo (human-only reopen)
```

Only humans may move tasks to `blocked` or `rejected`.
Only humans may reopen tasks from `rejected`.
