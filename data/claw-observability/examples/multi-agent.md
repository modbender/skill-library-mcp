# Multi-Agent Parallel Example

This example shows how hooks capture parallel sub-agent activations, creating a full hierarchy in the organogram.

## Scenario: Implement payment module

User asks: "Implement the payment module with backend, frontend, security review, and tests"

### Automatic Hook Flow

**1. UserPromptSubmit** → Sheev Palpatine `running`

**2. Agent launches 3 Task tools in parallel:**

PreToolUse fires for each:

| Task subagent_type | CLAW Reports |
|---|---|
| `chewie-backend` | Chewbacca → `running` "Implement payment backend" |
| `darth-maul` | Darth Maul → `running` "Security review payment flow" |
| `leia-frontend` | Leia Organa → `running` "Build payment UI" |

Dashboard: Three agents light up simultaneously, all connected to Anakin.

**3. Darth Maul's Task finishes first:**

PostToolUse fires:
```json
{"agent_id": "darth-maul", "status": "success", "message": "Completed: Security review payment flow"}
```

Dashboard: Darth Maul dims to success.

**4. Chewbacca's Task finishes:**

PostToolUse fires:
```json
{"agent_id": "chewbacca", "status": "success", "message": "Completed: Implement payment backend"}
```

**5. Leia's Task finishes:**

PostToolUse fires:
```json
{"agent_id": "leia", "status": "success", "message": "Completed: Build payment UI"}
```

**6. Agent launches C-3PO for testing:**

PreToolUse fires:
```json
{"agent_id": "c3po", "status": "running", "message": "Run payment test suite"}
```

PostToolUse fires:
```json
{"agent_id": "c3po", "status": "success", "message": "Completed: Run payment test suite"}
```

**7. Stop** → Sheev Palpatine `success`

## Dashboard View

The organogram shows the full activation cascade:
- Sheev → Anakin → Chewbacca, Darth Maul, Leia, C-3PO
- Agents light up green when running, then dim on success
- Parallel agents are visible simultaneously
- The task timeline shows all events in chronological order

## Key Point

All reporting was automatic. The agent used the Task tool normally — hooks intercepted each invocation and reported to CLAW without any intervention.
