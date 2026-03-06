# Agent Capabilities Reference

## Claude Code
- **Key:** claude-code
- **Best for:** Code development, refactoring, debugging
- **Capabilities:** dev, refactor, debug, docs
- **Dispatch:** CLI via PowerShell (Windows native) or WSL
- **Parallel:** Up to 3 instances
- **Token cost:** High (~12k+ per session)
- **Self-reports:** Yes (openclaw system event on completion)

## Eva
- **Key:** eva
- **Best for:** Testing, validation, system operations, orchestration
- **Capabilities:** test, validate, system-ops, docs
- **Dispatch:** Self-execution
- **Parallel:** 1 (orchestrator)
- **Self-reports:** Always (she IS the orchestrator)

## Agent Selection Logic

1. If a preferred agent is specified and capable of the subtask type → use it
2. Match agent by `preferred_types` (claude-code prefers dev, eva prefers test/validate)
3. Match agent by broader `capabilities` list
4. Fallback to eva (orchestrator handles anything unmatched)

## Dispatch Methods

| Method | Description | Used by |
|--------|-------------|---------|
| `cli` | Launched via CLI command with structured prompt | Claude Code |
| `self` | Eva executes the subtask herself | Eva |

## Capacity Tracking

The dispatcher counts IN_PROGRESS subtasks per agent across all active tasks.
If an agent is at its `max_parallel` limit, new dispatches to that agent are deferred.
