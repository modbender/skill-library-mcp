---
name: a2a-protocol
version: 1.0.0
description: Agent2Agent (A2A) Protocol implementation - communicate with other AI agents
metadata: {"openclaw": {"emoji": "🤝", "category": "communication", "requires": {"bins": ["python"], "pip": ["requests"]}, "homepage": "https://a2a-protocol.org"}}
---

# A2A Protocol Skill

Implementation of the Agent2Agent (A2A) Protocol for inter-agent communication.

## What it does

- **Agent Discovery** via Agent Cards
- **Send Messages** to remote agents
- **Task Management** (submit, check status, get results)
- **Streaming** via Server-Sent Events (SSE)
- **Authentication** support (API keys, Bearer tokens)

## Installation

```powershell
# Install Python dependencies
pip install requests sseclient-py
```

## Usage

### Register Your Agent

```powershell
.\a2a.ps1 -Action register -Name "MyAgent" -Description "Research agent" -Capabilities "research,analysis" -Endpoint "https://my-agent.com/a2a"
```

### Get Agent Card

```powershell
.\a2a.ps1 -Action card -AgentId "uuid-of-agent"
```

### Send Message

```powershell
.\a2a.ps1 -Action send -ToAgent "target-agent-uuid" -Content "Hello agent!"
```

### Submit Task

```powershell
.\a2a.ps1 -Action task -ToAgent "target-agent-uuid" -Task "Research quantum computing"
```

### Check Task Status

```powershell
.\a2a.ps1 -Action status -TaskId "task-uuid"
```

### List Remote Agents

```powershell
.\a2a.ps1 -Action list -RegistryUrl "https://registry.agentlink.io"
```

## A2A Concepts

- **Agent Card**: JSON describing agent capabilities (name, endpoint, methods)
- **Client Agent**: Agent that sends tasks
- **Remote Agent**: Agent that receives and processes tasks
- **Task**: Work request with ID, status, and result
- **Message**: Direct communication between agents

## API Reference

```
POST /a2a/agents/register - Register agent
GET  /a2a/agents/{id}    - Get agent info
GET  /a2a/agents/{id}/card - Get Agent Card
POST /a2a/messages       - Send message
POST /a2a/tasks          - Submit task
GET  /a2a/tasks/{id}     - Get task status
GET  /a2a/tasks/{id}/result - Get task result
```

## Examples

### Python Usage

```python
from a2a import A2AClient

client = A2AClient("https://remote-agent.com/a2a", api_key="your-key")

# Send message
client.send_message("target-agent-id", "Hello!")

# Submit task
task_id = client.submit_task("target-agent-id", "Do X")
result = client.get_result(task_id)
```

## Requirements

- Python 3.8+
- requests library
- sseclient-py (for streaming)

## License

MIT
