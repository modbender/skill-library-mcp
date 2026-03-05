---
name: governance-guard
description: >
  Structural authority separation for autonomous agent actions.
  Three-phase governance pipeline: PROPOSE, DECIDE, PROMOTE.
  No action is both proposed and approved by the same computational pathway.
version: 0.1.0
metadata:
  author: MetaCortex Dynamics LLC
  license: MIT
  openclaw:
    requires:
      bins:
        - node
        - npx
    install:
      - kind: node
        package: tsx
        bins: [tsx]
---

# governance-guard

Governance guard enforces structural authority separation on all agent actions through a PROPOSE-DECIDE-PROMOTE pipeline.

## When to activate

Before performing any **write**, **execute**, **network**, **create**, or **delete** action. The governance pipeline MUST be invoked before the action executes. Read actions may also be governed under standard or strict policies.

## How to use

### 1. Full pipeline (recommended)

Run the complete PROPOSE → DECIDE → PROMOTE pipeline in a single call:

```bash
npx tsx scripts/governance.ts pipeline '<intent-json>' --policy policies/standard.yaml
```

The intent JSON must include:
- `skill`: skill identifier
- `tool`: tool/function being invoked
- `model`: LLM model name
- `actionType`: one of `read`, `write`, `execute`, `network`, `create`, `delete`
- `target`: resource being acted upon
- `parameters`: tool parameters (object)
- `dataScope`: data categories accessed (array, e.g. `["personal", "financial"]`)
- `conversationId`: current conversation ID
- `messageId`: current message ID
- `userInstruction`: the user message that triggered this action

### 2. Handle the verdict

The pipeline returns a JSON response:

- If `"governance": "approved"` — proceed with the action
- If `"governance": "deny"` — do NOT proceed; inform the user with the `reason`
- If `"governance": "escalate"` — present the action to the user for approval:

```
Action requires your approval:
  Skill: <skill>
  Action: <actionType> on <target>
  Reason: <reason>
Reply APPROVE or DENY
```

Then resolve:

```bash
npx tsx scripts/governance.ts resolve-escalation <intent-id> approve
# or
npx tsx scripts/governance.ts resolve-escalation <intent-id> deny
```

### 3. Audit decisions

```bash
npx tsx scripts/governance.ts audit --last 10
```

## Policy presets

| Preset | Default | Description |
|--------|---------|-------------|
| `minimal` | approve | Blocks only credentials and destructive commands. Lowest friction. |
| `standard` | deny | Allows common ops, escalates network and data access. Recommended. |
| `strict` | deny | Reads only. Everything else requires explicit approval. Maximum safety. |

## Fail-closed guarantee

If any error occurs during governance evaluation, the default verdict is **DENY**. Missing policy files result in DENY ALL. This is by design. The system fails safe, never open.

## Configuration

Governance data is stored in `~/.openclaw/governance/`:
- `policy.yaml` — active policy file
- `witness.jsonl` — append-only, hash-chained audit log

## Verify witness chain

```bash
npx tsx scripts/governance.ts verify
```

Any tampering with historical records is detected by recomputing the hash chain from genesis.
