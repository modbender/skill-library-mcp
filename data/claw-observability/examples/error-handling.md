# Error Handling Example

This example shows how hooks automatically report errors when a Task tool fails.

## Scenario: Sub-agent task fails

User asks: "Refactor the authentication middleware"

### Automatic Hook Flow

**1. UserPromptSubmit** → Sheev Palpatine `running`

**2. Agent invokes Task (chewie-backend):**

PreToolUse fires:
```json
{"agent_id": "chewbacca", "status": "running", "message": "Refactor auth middleware"}
```

Dashboard: Chewbacca lights up green.

**3. The Task fails (e.g., sub-agent encounters an error):**

PostToolUseFailure fires:
```json
{"agent_id": "chewbacca", "status": "error", "message": "Failed: Refactor auth middleware"}
```

Dashboard: Chewbacca turns red with error glow.

**4. Agent retries with a different approach (new Task call):**

PreToolUse fires:
```json
{"agent_id": "chewbacca", "status": "running", "message": "Retry auth middleware refactor"}
```

Dashboard: Chewbacca turns green again.

PostToolUse fires:
```json
{"agent_id": "chewbacca", "status": "success", "message": "Completed: Retry auth middleware refactor"}
```

Dashboard: Chewbacca dims to success.

**5. Stop** → Sheev Palpatine `success`

## What the human sees

In the CLAW dashboard:
- Chewbacca's node turns **red** when the error occurs
- The error shows in the event feed and analytics
- After retry, Chewbacca turns **green** (running) then dims (success)
- The timeline shows the full error-to-recovery sequence

## Hook Events Summary

| Event | Hook | Agent | Status |
|-------|------|-------|--------|
| User sends message | UserPromptSubmit | Sheev Palpatine | running |
| Task invoked | PreToolUse | Chewbacca | running |
| Task fails | PostToolUseFailure | Chewbacca | error |
| Retry task | PreToolUse | Chewbacca | running |
| Retry succeeds | PostToolUse | Chewbacca | success |
| Response done | Stop | Sheev Palpatine | success |
