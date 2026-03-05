# Policy File Schema

Policy files are YAML documents stored at `~/.openclaw/governance/policy.yaml`.

## Top-level fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `version` | string | Yes | Schema version. Currently `"0.1"` |
| `default_verdict` | `"deny"` \| `"approve"` | Yes | Verdict when no rules match. Use `deny` for fail-closed. |
| `rules` | array | No | Ordered list of policy rules. First match wins. |
| `sensitive_data` | array | No | Sensitive data patterns. Checked before rules. |

## Rule fields

Each rule in the `rules` array:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Unique rule identifier |
| `match` | object | Yes | Matching conditions (all must be true) |
| `verdict` | `"approve"` \| `"deny"` \| `"escalate"` | Yes | Action to take on match |
| `reason` | string | No | Human-readable explanation |

## Match conditions

All specified conditions must be true for a rule to match (AND logic):

| Field | Type | Semantics |
|-------|------|-----------|
| `action_type` | string or string[] | Exact match against intent action type |
| `target_pattern` | string | Glob pattern against action target. `~` expands to home dir. `!` prefix for negation. |
| `tool_pattern` | string | Glob pattern against `skill.tool` identifier |
| `skill_pattern` | string | Glob pattern against skill identifier |
| `data_scope` | string[] | Array intersection with intent's data_scope (at least one match) |

## Glob patterns

- `*` matches any characters within a single path segment
- `**` matches any characters across path segments (recursive)
- `{a,b,c}` matches any of the alternatives
- `!pattern` negates the match (target does NOT match pattern)
- `~` at the start expands to the user's home directory

## Sensitive data rules

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `category` | string | Yes | Category name (e.g., `credentials`, `financial`) |
| `patterns` | string[] | No | Glob patterns to match against action target |
| `action` | `"deny"` \| `"escalate"` | Yes | Action when matched |

Sensitive data rules are evaluated before regular rules. If the action target matches any pattern, or the intent's `data_scope` contains the category name, the sensitive data rule fires.

## Evaluation order

1. Sensitive data rules (any match → immediate verdict)
2. Regular rules in declaration order (first match wins)
3. `default_verdict` if nothing matched

## Example

```yaml
version: "0.1"
default_verdict: deny

rules:
  - name: allow-read-workspace
    match:
      action_type: read
      target_pattern: "./**"
    verdict: approve
    reason: "Reads within workspace are safe"

  - name: escalate-network
    match:
      action_type: network
    verdict: escalate
    reason: "Network access needs user confirmation"

sensitive_data:
  - category: credentials
    patterns:
      - "**/*.env"
      - "**/.ssh/**"
    action: deny
```
