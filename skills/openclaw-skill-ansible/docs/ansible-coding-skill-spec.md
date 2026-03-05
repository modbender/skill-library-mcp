# Ansible-Coding Skill Specification

**Author**: Architect + Claude
**Date**: 2026-02-17
**Status**: Active — Updated for agent-level addressing schema

---

## Summary

The `ansible-coding` skill provides a safe, auditable wrapper for LLM-driven Ansible work. It enables any agent to delegate coding tasks (scaffold features, author playbooks, run dry-runs, create PRs) to executor agents via structured proposal messages, and receive structured stop-hook replies when work completes.

This spec covers both sides of the delegation transaction. Any agent sending proposals must follow the requester contract. Any agent executing proposals must follow the executor contract.

---

## Design Principles

### Two-Sided API Pattern

Every `ansible-[function]` skill contains both sides of the delegation transaction in a single document:

1. **Requester Side** — How to format and submit proposals, what to expect back
2. **Executor Side** — How to identify proposals, execute the workflow, send stop-hook replies
3. **Stop-Hook Contract** — The shared JSON schema both sides agree on

This means any agent can read a single skill spec and know exactly what to do, whether it is sending work or receiving it.

### Skill Steward Model

- Any agent with the skill loaded may act as executor (steward) for that skill type
- No fixed assignment — agents self-select based on capability and load
- Multiple agents may hold the same skill simultaneously

### Metadata vs. Content

**Critical**: All structured proposal fields go in `metadata`, not in the message `content`. The `content` field carries the human-readable description of the task. This separation ensures metadata is machine-parseable without text parsing.

---

## Agent Topology

### Internal Agents (tool-based, no CLI required)

| Agent ID | Display Name | Gateway | Role |
|---|---|---|---|
| `architect` | Aria | mac-jane | Orchestrator, primary requester |
| `mac-jane` | Jane | mac-jane | Primary executor |
| `librarian` | Astrid | mac-jane | Research, documentation |
| `vps-jane` | Jane | vps-jane | VPS-side executor |
| `chief-of-staff` | Beacon | vps-jane | VPS orchestrator |

### External Agents (CLI-based)

| Agent ID | Display Name | Interface |
|---|---|---|
| `claude` | Claude | `openclaw ansible` CLI |
| `codex` | Codex | `openclaw ansible` CLI |

External agents must register before sending or receiving messages:
```bash
openclaw ansible agent register --id claude --name "Claude"
openclaw ansible agent register --id codex --name "Codex"
```

---

## Message Schema

All ansible messages use this structure:

```typescript
{
  from_agent: AgentId,              // "architect", "claude", "mac-jane", etc.
  from_node?: TailscaleId,          // gateway node (informational, set by plugin)
  to_agents?: AgentId[],            // array of recipients; omit for broadcast
  content: string,                  // human-readable description
  metadata?: {
    conversation_id: string,        // REQUIRED — thread tracking
    corr?: string,                  // correlation ID for request/reply pairs
    kind?: string,                  // proposal | status | result | alert | decision
    // ...skill-specific fields
  },
  readBy_agents: AgentId[],
  delivery: Record<AgentId, DeliveryRecord>
}
```

`CoreMetadata` fields (`conversation_id`, `corr`, `kind`) are required in every message metadata block.

---

## For Requesters

Any agent — internal (architect, chief-of-staff) or external (claude, codex) — may submit coding proposals.

### Proposal Structure

Proposals use `kind: "proposal"` and `task_type: "coding"` in `metadata`. The `content` field carries the task description in plain language.

#### Required Metadata Fields

| Field | Type | Description |
|---|---|---|
| `conversation_id` | string | Thread ID for tracking this work stream |
| `kind` | string | Must be `"proposal"` |
| `corr` | string | Correlation ID — echoed back in stop-hook reply |
| `proposal_id` | string | Unique stable ID for this proposal |
| `task_type` | string | Must be `"coding"` for this skill |
| `acceptance_criteria` | string | Bulleted list of success conditions |
| `callback_target` | AgentId | Agent ID to receive the stop-hook reply |

### For Internal Agents — Tool Usage

Internal agents call `ansible_send_message` directly. The `to` parameter accepts a single agent ID or is omitted for broadcast.

**Targeted proposal (to mac-jane):**
```
ansible_send_message(
  to="mac-jane",
  content="Implement secrets management playbook for VPS infrastructure. Use ansible-vault for sensitive variables, support a rotation workflow, include smoke tests, and document in README.",
  metadata={
    "conversation_id": "conv-secrets-mgmt-001",
    "corr": "aria-req-001",
    "kind": "proposal",
    "proposal_id": "aria-coding-secrets-mgmt",
    "task_type": "coding",
    "acceptance_criteria": "- Feature branch created\n- Playbook scaffolded with role structure\n- Dry-run passes with no errors\n- PR created for review",
    "callback_target": "architect"
  }
)
```

**Broadcast proposal (any capable executor may claim):**
```
ansible_send_message(
  content="Scaffold a new ansible role for UFW firewall management on VPS nodes.",
  metadata={
    "conversation_id": "conv-ufw-role-002",
    "corr": "aria-req-002",
    "kind": "proposal",
    "proposal_id": "aria-coding-ufw-role",
    "task_type": "coding",
    "acceptance_criteria": "- Role directory structure created\n- Default variables defined\n- Dry-run passes\n- PR created",
    "callback_target": "architect"
  }
)
```

**Proposal to multiple agents:**
```
ansible_send_message(
  to=["mac-jane", "vps-jane"],
  content="Set up log rotation for all openclaw service logs across both mac and VPS nodes.",
  metadata={
    "conversation_id": "conv-logrotate-003",
    "corr": "aria-req-003",
    "kind": "proposal",
    "proposal_id": "aria-coding-logrotate",
    "task_type": "coding",
    "acceptance_criteria": "- Logrotate config created for all openclaw services\n- Dry-run passes on both nodes\n- PRs created",
    "callback_target": "architect"
  }
)
```

### For External Agents — CLI Usage

External agents use the `openclaw ansible send` CLI. Metadata is passed as a JSON string via `--metadata`. `--conversation-id` and `--kind` are top-level flags; all other skill-specific fields go inside `--metadata`.

**Targeted proposal:**
```bash
openclaw ansible send \
  --from claude \
  --to mac-jane \
  --conversation-id conv-secrets-mgmt-001 \
  --kind proposal \
  --metadata '{
    "corr": "claude-req-001",
    "proposal_id": "claude-coding-secrets-mgmt",
    "task_type": "coding",
    "acceptance_criteria": "- Feature branch created\n- Playbook scaffolded\n- Dry-run passes\n- PR created",
    "callback_target": "claude"
  }' \
  --message "Implement secrets management playbook for VPS infrastructure. Use ansible-vault for sensitive variables, support a rotation workflow, include smoke tests, and document in README."
```

**Broadcast proposal:**
```bash
openclaw ansible send \
  --from claude \
  --conversation-id conv-ufw-role-002 \
  --kind proposal \
  --metadata '{
    "corr": "claude-req-002",
    "proposal_id": "claude-coding-ufw-role",
    "task_type": "coding",
    "acceptance_criteria": "- Role scaffolded\n- Dry-run passes\n- PR created",
    "callback_target": "claude"
  }' \
  --message "Scaffold a UFW firewall management role."
```

**Proposal to multiple agents:**
```bash
openclaw ansible send \
  --from claude \
  --to mac-jane \
  --to vps-jane \
  --conversation-id conv-logrotate-003 \
  --kind proposal \
  --metadata '{
    "corr": "claude-req-003",
    "proposal_id": "claude-coding-logrotate",
    "task_type": "coding",
    "acceptance_criteria": "- Logrotate configs created\n- Dry-runs pass\n- PRs created",
    "callback_target": "claude"
  }' \
  --message "Set up log rotation for all openclaw service logs."
```

### Reading Replies (External Agents)

```bash
# Read inbox as JSON
openclaw ansible messages --agent claude --format json

# Filter by conversation
openclaw ansible messages --agent claude --format json \
  | jq '[.[] | select(.metadata.conversation_id == "conv-secrets-mgmt-001")]'
```

### What to Expect — Stop-Hook Reply

The executor sends a `kind: "result"` message back to `callback_target`. The `corr` field will match the `corr` in the original proposal.

The message `content` contains a human-readable summary. The stop-hook JSON payload is in `metadata.result`.

Example reply metadata:
```json
{
  "conversation_id": "conv-secrets-mgmt-001",
  "corr": "aria-req-001",
  "kind": "result",
  "proposal_id": "aria-coding-secrets-mgmt",
  "result": {
    "job_id": "ansible-20260217T1400Z-1234",
    "action": "scaffold",
    "branch": "skills/feature/secrets-mgmt",
    "files_created": [
      "skills/openclaw-skill-ansible/subskills/secrets-mgmt/SKILL.md",
      "playbooks/secrets-mgmt.yml",
      "roles/vault/tasks/main.yml"
    ],
    "dryrun_log": "memory/logs/secrets-mgmt-dryrun-20260217T1400Z.md",
    "pr_url": "https://github.com/user/repo/pull/123",
    "status": "success",
    "issues": []
  }
}
```

**Handling replies:**
1. Match on `metadata.corr` to correlate with the original proposal
2. Check `metadata.result.status`: `success` | `partial` | `failed`
3. Review `metadata.result.issues` if status is not `success`
4. Access `metadata.result.dryrun_log` for execution details
5. Review `metadata.result.pr_url` for PR link (if applicable)

---

## For Executors

Any agent with the `ansible-coding` skill loaded may act as executor. Executors watch for incoming proposals and self-select based on capability.

### How to Identify Coding Proposals

Scan incoming messages for both conditions in `metadata`:
- `kind === "proposal"`
- `task_type === "coding"`

**Internal agents — using `ansible_read_messages`:**
```
ansible_read_messages(
  agent="mac-jane",
  all=false
)
```
Then filter the result: select messages where `metadata.kind == "proposal"` and `metadata.task_type == "coding"`.

**External agents — using CLI:**
```bash
openclaw ansible messages --agent codex --format json \
  | jq '[.[] | select(.metadata.kind == "proposal" and .metadata.task_type == "coding")]'
```

### Required Fields to Extract

From `metadata`:
- `proposal_id` — stable identifier for this work item
- `acceptance_criteria` — success conditions to satisfy
- `callback_target` — agent ID to send the stop-hook reply to
- `corr` — correlation ID to echo in the reply
- `conversation_id` — thread ID to carry forward

From the message:
- `content` — full task description and requirements
- `from_agent` — originating agent (for reference)

### Workflow Execution

#### Step 1 — Parse Proposal

Extract the fields above. If any required field is missing, send a `kind: "alert"` reply to `callback_target` describing the problem. Do not attempt execution.

#### Step 2 — Scaffold Feature Branch

```bash
cd ~/code/openclaw-skill-ansible/skills/ansible-coding/runner

./scaffold.sh \
  --proposal-id "aria-coding-secrets-mgmt" \
  --branch "skills/feature/secrets-mgmt" \
  --context "$(cat proposal-body.txt)"
```

Outputs:
- Feature branch created from current HEAD of main
- Skeleton files scaffolded (playbook, role structure, README)
- Initial commit made

#### Step 3 — Run Dry-Run

```bash
./dryrun.sh \
  --proposal-id "aria-coding-secrets-mgmt" \
  --playbook "playbooks/secrets-mgmt.yml"
```

Outputs:
- Ansible `--check` mode output captured
- Log written to `memory/logs/<proposal-id>-dryrun-<TIMESTAMP>.md`
- Exit code: 0 = success, non-zero = failure

If dry-run fails, send a `kind: "result"` with `status: "failed"` back to `callback_target`. Do not proceed to PR creation.

#### Step 4 — Create PR

```bash
git push -u origin skills/feature/secrets-mgmt

gh pr create \
  --title "feat: secrets management playbook [<proposal_id>]" \
  --body-file skills/ansible-coding/templates/PR.md.template
```

#### Step 5 — Finish Hook

```bash
REPLY_JSON=$(./finish-hook.sh \
  --proposal-id "aria-coding-secrets-mgmt" \
  --action "scaffold" \
  --branch "skills/feature/secrets-mgmt" \
  --status "success" \
  --pr-url "https://github.com/user/repo/pull/123")
```

`finish-hook.sh` outputs structured JSON to stdout and writes a markdown audit log to `memory/logs/`.

#### Step 6 — Send Stop-Hook Reply

The reply goes to the `callback_target` agent from the original proposal metadata. Use `to_agents` as a single-element array.

**Internal executor (tool):**
```
ansible_send_message(
  to="architect",
  content="Scaffolded secrets-mgmt on branch skills/feature/secrets-mgmt. Dry-run passed. PR ready for review at https://github.com/user/repo/pull/123.",
  metadata={
    "conversation_id": "conv-secrets-mgmt-001",
    "corr": "aria-req-001",
    "kind": "result",
    "proposal_id": "aria-coding-secrets-mgmt",
    "result": <REPLY_JSON parsed object>
  }
)
```

**External executor (CLI):**
```bash
openclaw ansible send \
  --from codex \
  --to architect \
  --conversation-id conv-secrets-mgmt-001 \
  --kind result \
  --metadata "{
    \"corr\": \"aria-req-001\",
    \"proposal_id\": \"aria-coding-secrets-mgmt\",
    \"result\": $REPLY_JSON
  }" \
  --message "Scaffolded secrets-mgmt on skills/feature/secrets-mgmt. Dry-run passed. PR at https://github.com/user/repo/pull/123."
```

### Apply Mode (Owner ACK Required)

Apply mode runs the playbook against a real environment. It is never triggered automatically.

**Prerequisites:**
1. GitHub PR approval on the feature branch PR, OR
2. An explicit `kind: "decision"` ansible message from the owner with `approved: true` and a reference to the proposal_id

**Execution:**
```bash
./apply.sh \
  --proposal-id "aria-coding-secrets-mgmt" \
  --approval-ref "https://github.com/user/repo/pull/123#pullrequestreview-12345"
```

Send a stop-hook reply with `action: "apply"` upon completion.

---

## Stop-Hook Contract

### JSON Schema (result object)

This is the schema for the `result` object placed in `metadata.result` of stop-hook replies.

```typescript
{
  job_id: string,            // Required. Format: "ansible-<ISO8601>-<random4>"
  action: "scaffold"         // Required. Which action completed.
        | "dryrun"
        | "apply",
  branch: string,            // Required. Git branch name.
  files_created: string[],   // Required. Paths to created/modified files.
  dryrun_log?: string,       // Optional; required if action is "dryrun" or "apply".
  pr_url?: string,           // Optional; included when PR was created.
  status: "success"          // Required.
        | "partial"
        | "failed",
  issues: string[],          // Required. Empty array if status is "success".
}
```

### Field Reference

| Field | Type | Required | Description |
|---|---|---|---|
| `job_id` | string | Yes | `ansible-<ISO8601>-<4 random digits>` |
| `action` | enum | Yes | `scaffold`, `dryrun`, or `apply` |
| `branch` | string | Yes | Git branch where work was done |
| `files_created` | string[] | Yes | All files created or modified |
| `dryrun_log` | string | Conditional | Path to log; required for dryrun/apply |
| `pr_url` | string | No | Full GitHub PR URL if PR was created |
| `status` | enum | Yes | `success`, `partial`, or `failed` |
| `issues` | string[] | Yes | Error/warning messages; `[]` on success |

### Example Outputs

**Success:**
```json
{
  "job_id": "ansible-20260217T1400Z-1234",
  "action": "scaffold",
  "branch": "skills/feature/secrets-mgmt",
  "files_created": [
    "playbooks/secrets-mgmt.yml",
    "roles/vault/tasks/main.yml",
    "roles/vault/defaults/main.yml"
  ],
  "pr_url": "https://github.com/user/repo/pull/123",
  "status": "success",
  "issues": []
}
```

**Partial success (dry-run with warnings):**
```json
{
  "job_id": "ansible-20260217T1415Z-5678",
  "action": "dryrun",
  "branch": "skills/feature/secrets-mgmt",
  "files_created": ["playbooks/secrets-mgmt.yml"],
  "dryrun_log": "memory/logs/secrets-mgmt-dryrun-20260217T1415Z.md",
  "status": "partial",
  "issues": ["Warning: vault password file not found (expected for dry-run environment)"]
}
```

**Failure:**
```json
{
  "job_id": "ansible-20260217T1420Z-9999",
  "action": "scaffold",
  "branch": "skills/feature/broken",
  "files_created": [],
  "status": "failed",
  "issues": [
    "Git branch creation failed: branch already exists",
    "Cannot write to repository: permission denied"
  ]
}
```

---

## Safety & Governance

### No Secrets in Messages

- Never accept secret values in proposal `content` or `metadata`
- Never include secret values in stop-hook replies or audit logs
- Use secret path references only: `~/.openclaw/secrets/<name>` or `{{ vault_password_file }}`
- If a proposal contains inline secrets, reject with a `kind: "alert"` reply

### Dry-Run Required

- Default execution mode is Ansible `--check` (dry-run)
- Apply mode (real execution) requires explicit owner ACK
- Valid ACK forms: GitHub PR approval or a `kind: "decision"` message with `approved: true`
- Executors must verify ACK before running `apply.sh`

### Feature Branch + PR Workflow

- All changes are made on feature branches (`skills/feature/<name>`)
- No direct commits to `main`
- No force-pushes
- PR creation is part of the standard workflow, not optional

### Audit Trail

Every run writes a markdown audit log:
- Path: `memory/logs/ansible-skill-run-<TIMESTAMP>.md`
- Contents: `job_id`, `proposal_id`, `from_agent`, `branch`, `files_created`, `status`, `issues`, PR URL, dry-run log reference
- No sensitive data in logs

### Policy File

`skills/ansible-coding/policy.json`:
```json
{
  "dry_run_required": true,
  "secrets_allowed": false,
  "approval_gate": "owner_ack",
  "audit_log_path": "memory/logs/",
  "default_branch_prefix": "skills/feature/"
}
```

---

## Example Lifecycle

### 1. Aria (architect) Sends Proposal via Tool

```
ansible_send_message(
  to="mac-jane",
  content="Implement secrets management playbook for VPS infrastructure. Use ansible-vault for sensitive variables, support a rotation workflow, include smoke tests, document in README.",
  metadata={
    "conversation_id": "conv-secrets-mgmt-001",
    "corr": "aria-req-001",
    "kind": "proposal",
    "proposal_id": "aria-coding-secrets-mgmt",
    "task_type": "coding",
    "acceptance_criteria": "- Feature branch created\n- Playbook scaffolded with role structure\n- Dry-run passes with no errors\n- PR created for review",
    "callback_target": "architect"
  }
)
```

### 2. mac-jane Receives and Identifies Proposal

mac-jane calls `ansible_read_messages(agent="mac-jane")`, scans results, finds a message where:
- `metadata.kind == "proposal"` — yes
- `metadata.task_type == "coding"` — yes

Extracts: `proposal_id`, `acceptance_criteria`, `callback_target`, `corr`, `conversation_id`, and `content`.

### 3. mac-jane Executes Workflow

```bash
cd ~/code/openclaw-skill-ansible/skills/ansible-coding/runner

# Scaffold feature branch
./scaffold.sh \
  --proposal-id "aria-coding-secrets-mgmt" \
  --branch "skills/feature/secrets-mgmt"

# Author playbook and role (LLM-driven, guided by content field)

# Dry-run
./dryrun.sh \
  --proposal-id "aria-coding-secrets-mgmt" \
  --playbook "playbooks/secrets-mgmt.yml"

# Create PR
git push -u origin skills/feature/secrets-mgmt
gh pr create --title "feat: secrets management playbook [aria-coding-secrets-mgmt]"

# Finish hook
REPLY_JSON=$(./finish-hook.sh \
  --proposal-id "aria-coding-secrets-mgmt" \
  --action "scaffold" \
  --branch "skills/feature/secrets-mgmt" \
  --status "success" \
  --pr-url "https://github.com/user/repo/pull/123")
```

### 4. mac-jane Sends Stop-Hook Reply to architect

```
ansible_send_message(
  to="architect",
  content="Scaffolded aria-coding-secrets-mgmt on skills/feature/secrets-mgmt. Dry-run passed with no errors. PR ready for review.",
  metadata={
    "conversation_id": "conv-secrets-mgmt-001",
    "corr": "aria-req-001",
    "kind": "result",
    "proposal_id": "aria-coding-secrets-mgmt",
    "result": {
      "job_id": "ansible-20260217T1400Z-1234",
      "action": "scaffold",
      "branch": "skills/feature/secrets-mgmt",
      "files_created": [
        "playbooks/secrets-mgmt.yml",
        "roles/vault/tasks/main.yml",
        "roles/vault/defaults/main.yml"
      ],
      "dryrun_log": "memory/logs/secrets-mgmt-dryrun-20260217T1400Z.md",
      "pr_url": "https://github.com/user/repo/pull/123",
      "status": "success",
      "issues": []
    }
  }
)
```

### 5. Aria (architect) Processes Reply

Aria calls `ansible_read_messages(agent="architect")`, finds the reply where `metadata.corr == "aria-req-001"`. It checks:
- `metadata.kind == "result"` — confirmed
- `metadata.result.status == "success"` — confirmed
- `metadata.result.pr_url` — notes PR for human review
- `metadata.result.issues` — empty, no action needed

Aria may notify the human owner: "Secrets management playbook scaffolded and ready for review at PR #123."

---

## Skill Catalog Pattern

### Repository Structure

```
openclaw-skill-ansible/
├── README.md
├── SKILL.md                              # Core ansible coordination skill
├── skills/
│   ├── ansible-skill-creator/           # Meta-skill: how to create skills
│   │   ├── SKILL.md
│   │   ├── templates/
│   │   └── runner/
│   ├── ansible-coding/                  # This skill
│   │   ├── SKILL.md                     # Two-sided API (quick reference)
│   │   ├── policy.json                  # Safety rules and approval gates
│   │   ├── schema/
│   │   │   └── ansible-skill-schema.json
│   │   ├── runner/
│   │   │   ├── scaffold.sh
│   │   │   ├── dryrun.sh
│   │   │   ├── apply.sh
│   │   │   └── finish-hook.sh
│   │   ├── templates/
│   │   │   ├── SKILL.md.template
│   │   │   └── PR.md.template
│   │   ├── examples/
│   │   │   └── sample-lifecycle.md
│   │   └── tests/
│   │       └── lint-and-dryrun.sh
│   └── ...                              # Future: ansible-research, ansible-monitoring
└── docs/
    └── ansible-coding-skill-spec.md     # This document
```

### Skill Loading

OpenClaw loads `SKILL.md` files from:
- `~/.openclaw/workspace/skills/ansible/SKILL.md` — core coordination skill
- `~/.openclaw/workspace/skills/ansible/skills/*/SKILL.md` — skill catalog entries

Agents receive skill context when:
- Configured in `injectContextAgents` (always loaded at startup)
- Claiming tasks that require specific skills
- Receiving `kind: "skill-update"` messages via ansible

### Skill Discovery

Skills are distributed via three mechanisms:
1. **Static**: `openclaw ansible setup` clones the repo
2. **Dynamic**: A skill steward broadcasts `kind: "skill-update"` with the SKILL.md content
3. **On-demand**: An agent requests a skill when it encounters a proposal type it does not recognize

---

## Quick Reference for Aria

To send a coding proposal right now:

```
ansible_send_message(
  to="mac-jane",
  content="<task description — what to build and why>",
  metadata={
    "conversation_id": "<unique thread id>",
    "corr": "<your tracking id>",
    "kind": "proposal",
    "proposal_id": "<unique proposal id>",
    "task_type": "coding",
    "acceptance_criteria": "<bulleted success conditions>",
    "callback_target": "architect"
  }
)
```

Watch for replies with `metadata.kind == "result"` and `metadata.corr` matching your original `corr`.

---

**End of Specification**
