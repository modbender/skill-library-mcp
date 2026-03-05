# Safety and Risk Model

Classify every action before executing commands.

## Risk Classes

### `read-only`

No state change expected.

Examples:

- `social doctor`
- `social auth status`
- `social query ...`
- `social marketing insights ...`

Execution policy: execute directly.

### `write-low`

State changes are limited and reversible.

Examples:

- profile default updates
- schedule setup updates
- integration metadata updates

Execution policy: request one explicit confirmation.

### `write-high`

Action can create spend, send messages, publish public content, or trigger production automations.

Examples:

- marketing writes affecting live spend
- outbound customer messaging
- production content publishing
- approval actions that trigger execution

Execution policy:

1. State impact in plain language.
2. Show exact command.
3. Request explicit confirmation.
4. Provide rollback or mitigation command when available.

## Confirmation Templates

### Low-Risk Write

`This command changes workspace state. Confirm to continue.`

### High-Risk Write

`This command can affect live spend, customer messaging, or production content. Confirm to continue.`

## Secret Handling

- Never print full tokens.
- Mask secrets in diagnostics and examples.
- Prefer prompting for secure input over inline plaintext tokens.
