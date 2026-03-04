# Local Task Runner

This skill provides a mechanism to execute Node.js code snippets or full scripts locally on the host machine.
It is the **default execution method** when subagent spawning is unavailable or inefficient.

## Purpose

- **Replace Subagents**: Instead of spawning a full subagent for simple tasks, use this skill to run code directly.
- **Safety**: Isolates execution logic, handles cleanup, and enforces timeouts.
- **Convenience**: No manual file management required (`write` + `exec` + `rm`).

## Usage

When you need to perform a calculation, check system status, or run a utility script:

1.  Construct the Node.js code as a string.
2.  Call `run_task` (or execute via CLI) with the code.

### Command Line Interface

```bash
# Execute a task
node skills/local-task-runner/index.js run --code "console.log('Hello World')"

# Execute with timeout (ms)
node skills/local-task-runner/index.js run --code "while(true){}" --timeout 5000
```

### Response Format

Success:
```
[TASK: <id>] Completed in 123ms
--- STDOUT ---
...
```

Error:
```
[TASK: <id>] Failed in 123ms
Error: ...
--- STDERR ---
...
```
