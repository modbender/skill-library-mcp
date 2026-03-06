---
name: self-prompt
description: 'Force agent responses to scheduled/automated messages. Use when
  cron jobs, monitoring scripts, or automated systems send messages that agents
  ignore. Solves the problem where agents treat system-sent messages as
  "background info" instead of tasks requiring response. Key pattern: use
  `openclaw agent` instead of `openclaw message send` to trigger actual agent
  turns.'
---


# Self-Prompt: Forcing Agent Responses

## The Problem

When automated scripts (cron, monitoring) send messages via `openclaw message send`:
- Messages appear in chat as "system messages"
- Agents may treat them as background info, not tasks
- Agents respond to user messages but ignore automated ones
- Accountability checks, alerts, and tasks go unanswered

## The Solution

Use `openclaw agent` instead of `openclaw message send` for messages requiring agent response:

```bash
# OLD (agent may ignore):
openclaw message send --target -GROUP_ID --message "TASK: Do something"

# NEW (agent MUST respond):
RESPONSE=$(openclaw agent \
    --agent AGENT_ID \
    --session-id "agent:AGENT_ID:telegram:group:GROUP_ID" \
    --channel telegram \
    --message "TASK: Do something" \
    --timeout 180)

# Send response to chat:
openclaw message send --target -GROUP_ID --message "$RESPONSE"
```

## Why This Works

- `openclaw message send` → Creates chat message → Agent sees as "notification"
- `openclaw agent` → Triggers actual agent turn → Agent MUST process and respond

## Quick Start

### For Bash Scripts

Use `scripts/send_agent_task.sh`:

```bash
# Simple usage:
~/.openclaw/skills/self-prompt/scripts/send_agent_task.sh \
    "AGENT_ID" \
    "GROUP_ID" \
    "Your task message here"
```

### For Python Scripts

Use `scripts/send_agent_task.py`:

```python
from send_agent_task import send_and_deliver

success, response = send_and_deliver(
    agent_id="stock-trading",
    group_id="-5283045656", 
    message="TASK: Analyze current positions",
    timeout=180
)
```

## Pattern: Data + Task Separation

For monitoring scripts, separate data delivery from task requests:

```bash
# 1. Send DATA immediately (informational)
openclaw message send --target "$GROUP_ID" --message "📊 Position Data:
$POSITIONS"

# 2. Send TASK via agent (forces response)
RESPONSE=$(openclaw agent \
    --agent "$AGENT_ID" \
    --session-id "agent:$AGENT_ID:telegram:group:$GROUP_ID" \
    --message "Analyze the data above and report findings" \
    --timeout 180)

# 3. Deliver response
openclaw message send --target "$GROUP_ID" --message "📊 Analysis:
$RESPONSE"
```

## Common Use Cases

### Accountability Checks
```bash
# Force agent to respond to accountability check
send_agent_task.sh "my-agent" "-123456789" \
    "ACCOUNTABILITY CHECK: Did you complete the required tasks? Respond with status."
```

### Monitoring Alerts
```bash
# Force agent to investigate and report
send_agent_task.sh "trading-agent" "-123456789" \
    "ALERT: Position down 5%. Investigate and report findings."
```

### Scheduled Research Tasks
```bash
# Force agent to do research
send_agent_task.sh "research-agent" "-123456789" \
    "DAILY TASK: Search for news on $SYMBOLS and summarize findings."
```

## Session Key Format

The session key follows this pattern:
```
agent:AGENT_ID:CHANNEL:TYPE:TARGET
```

Examples:
- `agent:stock-trading:telegram:group:-5283045656`
- `agent:main:telegram:direct:123456789`
- `agent:assistant:discord:channel:987654321`

## Script Reference

### send_agent_task.sh
Location: `scripts/send_agent_task.sh`

```bash
send_agent_task.sh AGENT_ID GROUP_ID "message" [timeout]
```

- Sends task via `openclaw agent`
- Captures response
- Sends response to group via `message send`
- Logs to `~/agent_task.log`

### send_agent_task.py
Location: `scripts/send_agent_task.py`

```python
from send_agent_task import send_and_deliver

success, response = send_and_deliver(
    agent_id="agent-name",
    group_id="-123456789",
    message="Task message",
    timeout=180,
    channel="telegram"
)
```

## Troubleshooting

### Agent not responding
- Verify agent is running: `openclaw gateway status`
- Check session key format matches your agent/group
- Increase timeout for long-running tasks

### Response not appearing in chat
- Ensure script sends response via `message send` after capturing
- Check GROUP_ID is correct (negative for groups)
- Verify channel is correct (telegram/discord/etc)

### Timeout errors
- Increase timeout for research/analysis tasks (300-600 seconds)
- Check if agent is overloaded with concurrent requests
