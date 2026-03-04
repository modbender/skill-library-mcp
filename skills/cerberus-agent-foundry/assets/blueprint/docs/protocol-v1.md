# Local Protocol v1 (Cerberus Team)

## Non-Negotiable Isolation
Each agent has a dedicated workspace and **must not** write to other agents' workspaces.

- `agents/team-lead/workspace/`
- `agents/coder/workspace/`
- `agents/researcher/workspace/`
- `agents/qa-ops/workspace/`

Shared coordination happens only in `control-plane/`.

## Task State Machine
`INBOX -> CLAIMED -> IN_PROGRESS -> REVIEW -> DONE | BLOCKED | FAILED`

### Hard constraints
1. CLAIMED requires `owner`, `claimed_at`, `claim_ttl_minutes`.
2. CLAIMED timeout auto-reverts to INBOX.
3. REVIEW must be done by a reviewer different from owner.
4. Every transition appends one record to `control-plane/logs/events.jsonl`.

## Task Schema (required fields)
- task_id
- title
- owner
- status
- deadline
- dod (Definition of Done)
- reviewer
- created_at
- updated_at
- claim_ttl_minutes

## Mailbox Protocol
Message file format: YAML header + markdown body.

Required header:
- message_id
- correlation_id
- task_id
- sender
- receiver
- version
- timestamp
- status: UNREAD | ACK | RESOLVED | REJECTED
- retry_count
- checksum

### Mailbox constraints
- Sender writes append-only new message files.
- Receiver may only update `status` and add response section.
- Only Team Lead can archive/delete old mail.

## Least Privilege Matrix
- Researcher: search/read only, no write, no shell execution.
- Coder: read/write/exec only inside `agents/coder/workspace`.
- QA/Ops: tests/log inspection; deploy requires human approval by writing request into `control-plane/approvals/`.
- Team Lead: routing, arbitration, GC, protocol enforcement.

## Rollout Gates
- Gate 1 (MVP): Team Lead -> Coder -> Mailbox -> Team Lead
- Gate 2: add QA review loop
- Gate 3: add Researcher parallel flow
- Gate 4: consider A2A bridge only after 3+ days stable autonomous runs


## Shared Memory Layer
Shared memory location: `control-plane/shared-memory/`

- `semantic/`: durable cross-agent facts and decisions
- `episodic/`: summarized multi-agent events
- `index/`: retrieval indices/tags
- `archive/`: archived snapshots

Write policy:
- Team Lead: read/write
- Other agents: read + propose via mailbox message to Team Lead


Mailbox topology rule: use only `control-plane/mailbox/` for agent-to-agent messages. Do not create per-agent inbox/outbox channels.
