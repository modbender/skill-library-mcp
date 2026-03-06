# CORD Python API Reference

## Core Function

```python
from cord_engine import evaluate, Proposal

verdict = evaluate(proposal, repo_root=None, lock_path=None, log_path=None)
```

## Proposal Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `text` | str | Yes | Description of the proposed action |
| `action_type` | str | No | `command`, `file_op`, `network`, `financial`, `communication`, `system`, `query`, `unknown` |
| `target_path` | str | No | File or resource path being targeted |
| `network_target` | str | No | Domain or network destination |
| `grants` | list[str] | No | Permissions: `shell`, `network`, `write:file`, `read:secrets`, etc. |
| `session_intent` | str | No | Declared purpose for this session |
| `context` | dict | No | Additional metadata (see below) |
| `tool_name` | str | No | OpenClaw tool being called: `exec`, `write`, `browser`, `read`, `message`, `network` |
| `source` | str | No | Input origin: `agent` (default), `external`, `user`, `tool_result` |
| `raw_input` | str | No | Untrusted external input to scan for prompt injection |

## Context Keys

| Key | Type | Effect |
|-----|------|--------|
| `financial_amount` | float | Triggers Article VI checks |
| `impulsive` | bool | Flags impulsive financial behavior |
| `roi_evaluated` | bool | Reduces financial risk score |
| `burnout_risk` | bool | Triggers Article V sustainability check |
| `exceeds_capacity` | bool | Flags capacity overload |
| `bypasses_review` | bool | Triggers Article I short-term concern |
| `consequence_analysis_done` | bool | Reduces Article IV score |
| `risk_assessment_done` | bool | Reduces Article IX score |
| `alternative_considered` | bool | Reduces Article IX score |
| `consequences_stated` | bool | Reduces Article IX score |
| `unverified_data` | bool | Triggers Article III truth check |

## Verdict Fields

| Field | Type | Description |
|-------|------|-------------|
| `decision` | Decision | ALLOW, CONTAIN, CHALLENGE, or BLOCK |
| `score` | float | Composite risk score (0-10) |
| `risk_profile` | dict | Per-dimension score breakdown |
| `reasons` | list[str] | Human-readable explanations |
| `alternatives` | list[str] | Suggested safer approaches |
| `article_violations` | list[str] | Constitutional articles that flagged risk |
| `log_id` | str | Hash reference to audit log entry |

## Intent Lock

```python
from cord_engine import set_intent_lock

set_intent_lock(
    user_id="alex",
    passphrase="session-pass",
    intent_text="Deploy site updates",
    scope={
        "allow_paths": ["/repo"],
        "allow_commands": [r"^git\s+"],
        "allow_network_targets": ["github.com"],
    },
)
```

## Audit Log

```python
from cord_engine import verify_chain, read_log

valid, count = verify_chain()  # Returns (bool, int)
entries = read_log()           # Returns list[dict]
```
