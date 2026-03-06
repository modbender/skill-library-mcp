# SPAWN-INTEGRATION.md

## Overview

Automatically update the Mission Control board when sub-agents launched via OpenClaw's `sessions_spawn` complete or fail.

---

## 1. Mission Start Flow

### 1.1 Prerequisites
- Task decomposition complete
- Agent list determined
- Irreversible operation check done

### 1.2 Execution Steps

```python
# 1. Send Phase 1 INIT message
init_msg = await message_send(
    channel=MISSION_CONTROL_CHANNEL,
    message=mission_board_template(
        mission_name="...",
        agents=[...],
        phase=1,
        irreversible=False
    )
)
message_id = init_msg.messageId

# 2. Pin message
await miso_telegram_pin(message_id)

# 3. React with 🔥
await message_react(channel=MISSION_CONTROL_CHANNEL, messageId=message_id, emoji="🔥")

# 4. Spawn each agent
agent_states = {}
for agent_name, agent_task in agents.items():
    result = await sessions_spawn(
        prompt=agent_task,
        label=agent_name,  # Used to identify completion notifications
        ...
    )
    agent_states[agent_name] = {
        "status": "INIT",
        "subagent_session": result.session,
        "messageId": message_id,
        "findings": None
    }

# 5. Transition all agents to RUNNING
for agent_name in agent_states:
    agent_states[agent_name]["status"] = "RUNNING"

# 6. Update mission board (Phase 2)
await message_edit(
    channel=MISSION_CONTROL_CHANNEL,
    messageId=message_id,
    message=update_board(
        phase=2,
        agent_states=agent_states,
        progress=0
    )
)
```

---

## 2. Agent Completion Flow

### 2.1 Completion Notification Detection

```
"A subagent task X just completed/failed"
```

Detect this pattern via log or event stream.

```python
# Regex extraction
pattern = r'A subagent task (.*?) just (completed|failed)'
match = re.search(pattern, notification)

agent_name = match.group(1)
status = "DONE" if match.group(2) == "completed" else "ERROR"
```

### 2.2 State Update

```python
# Update the relevant agent's state
agent_states[agent_name]["status"] = status

# Summarize findings on completion
if status == "DONE":
    findings = await summarize_findings(agent_name)
    agent_states[agent_name]["findings"] = findings
```

### 2.3 Mission Board Update

```python
# Phase determination & transition
done_count = sum(1 for s in agent_states.values() if s["status"] == "DONE")
error_count = sum(1 for s in agent_states.values() if s["status"] == "ERROR")
total = len(agent_states)

if error_count > 0:
    phase = "ERROR"
elif done_count == total:
    if has_irreversible_operations:
        phase = 4  # Awaiting approval
    else:
        phase = 5  # Complete
else:
    phase = 3  # Partial

# Calculate progress
progress = int(done_count / total * 100)

# Update board
await message_edit(
    channel=MISSION_CONTROL_CHANNEL,
    messageId=message_id,
    message=update_board(
        phase=phase,
        agent_states=agent_states,
        progress=progress
    )
)
```

### 2.4 All Agents Complete

#### Phase 4 (Approval gate)
```python
await message_react(channel=MISSION_CONTROL_CHANNEL, messageId=message_id, emoji="👀")
# Include approval buttons
```

#### Phase 5 (Complete)
```python
await message_react(channel=MISSION_CONTROL_CHANNEL, messageId=message_id, emoji="🎉")
await miso_telegram_unpin(message_id)
```

---

## 3. Error Flow

```python
# Phase ERROR
agent_states[agent_name]["status"] = "ERROR"

await message_edit(
    channel=MISSION_CONTROL_CHANNEL,
    messageId=message_id,
    message=update_board(
        phase="ERROR",
        agent_states=agent_states,
        error_message=f"Error in {agent_name}",
        retry_button=True
    )
)

await message_react(channel=MISSION_CONTROL_CHANNEL, messageId=message_id, emoji="❌")
```

---

## 4. Status Determination Logic

### 4.1 Agent State Transitions

```
INIT → RUNNING → DONE
            ↘ ERROR
```

### 4.2 Progress Bar Calculation

```python
progress = (done_count / total_agents) * 100

# Display: ████████░░░░░░░░ 40%
```

### 4.3 Phase Determination Rules

| Condition | Phase | Description |
|-----------|-------|-------------|
| Initializing | 1 | Right after INIT message sent |
| Running | 2 | All agents RUNNING |
| Partial | 3 | 1+ DONE, some still running |
| Awaiting approval | 4 | All DONE + irreversible ops pending |
| Complete | 5 | All DONE + no irreversible ops |
| Error | ERROR | Any agent in ERROR state |

---

## 5. Data Structures

### 5.1 agent_states

```python
{
    "agent_name": {
        "status": "INIT | RUNNING | DONE | ERROR",
        "subagent_session": "session-id",
        "messageId": "telegram-message-id",
        "findings": "Summarized result"
    },
    ...
}
```

---

## 6. Implementation Notes

1. **messageId management**: Retain the INIT message ID and use it for all updates
2. **Label importance**: Use spawn label to identify agents in completion notifications
3. **Parallelism**: Design must not depend on agent completion order
4. **Irreversible operation check**: Determine at mission start, affects Phase 4/5 routing
5. **Error handling**: Single agent error should not halt the entire mission
