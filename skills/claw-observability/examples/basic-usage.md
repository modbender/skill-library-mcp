# Basic Usage Example

This example shows how hooks automatically report a simple task flow.

## Scenario: User asks to fix a bug

### User prompt
> "Fix the login validation bug"

### What happens automatically (via hooks)

**1. UserPromptSubmit hook fires**

The user presses Enter. Before the agent even starts thinking, the hook reports:

```json
{
  "agent_id": "sheev-palpatine",
  "agent_name": "Sheev Palpatine",
  "agent_type": "orchestrator",
  "status": "running",
  "message": "Processing user request"
}
```

Dashboard: Sheev Palpatine lights up green.

**2. Agent invokes Task tool (subagent_type: "chewie-backend")**

PreToolUse hook fires automatically:

```json
{
  "agent_id": "chewbacca",
  "agent_name": "Chewbacca",
  "agent_type": "backend",
  "parent_agent_id": "anakin",
  "status": "running",
  "message": "Fix login validation bug",
  "task_id": "fix-login-validation-bug"
}
```

Dashboard: Chewbacca appears in the organogram, connected to Anakin, glowing green.

**3. Task tool returns successfully**

PostToolUse hook fires automatically:

```json
{
  "agent_id": "chewbacca",
  "agent_name": "Chewbacca",
  "agent_type": "backend",
  "parent_agent_id": "anakin",
  "status": "success",
  "message": "Completed: Fix login validation bug",
  "task_id": "fix-login-validation-bug"
}
```

Dashboard: Chewbacca dims to success state.

**4. Agent finishes responding**

Stop hook fires automatically:

```json
{
  "agent_id": "sheev-palpatine",
  "agent_name": "Sheev Palpatine",
  "agent_type": "orchestrator",
  "status": "success",
  "message": "Finished responding to user"
}
```

Dashboard: Sheev Palpatine dims to success state.

## What the human sees

1. Sheev Palpatine lights up green immediately when the message is sent
2. Chewbacca appears and lights up when the Task tool is invoked
3. Chewbacca dims when the task completes
4. Sheev Palpatine dims when the response is done
5. The timeline shows all 4 events in order

**No curl commands were executed by the agent.** Everything was automatic via hooks.
