# Fleet Communication Skill

Multi-agent communication system for OpenClaw fleets. Enables real-time messaging between multiple OpenClaw instances running on different machines.

## When to use
- User asks agents to communicate with each other
- Multi-machine OpenClaw setups need coordination
- Task delegation between fleet nodes
- Broadcasting announcements to all nodes

## Setup
The skill runs a lightweight HTTP message bus on the coordinator node (default port 18800).

### Start the bus (on coordinator node)
```bash
node fleet-comm/fleet_bus.js
```

### Environment
- `FLEET_NODE_ID` — This node's ID (default: `00`)
- `FLEET_BUS_URL` — URL of the message bus (default: `http://127.0.0.1:18800`)
- `FLEET_BUS_PORT` — Port to run bus on (default: `18800`)

## Commands

### Send a message to a specific node
```bash
node fleet-comm/fleet_cli.js send <target_node> <message>
# Example: node fleet-comm/fleet_cli.js send 01 "start bounty scan"
```

### Broadcast to all nodes
```bash
node fleet-comm/fleet_cli.js broadcast <message>
```

### Read messages for this node
```bash
node fleet-comm/fleet_cli.js read
```

### Check bus status
```bash
node fleet-comm/fleet_cli.js status
```

## Architecture
```
  00 (Mac Mini)          01 (WSL2)           02 (Windows)
  ┌──────────┐          ┌──────────┐        ┌──────────┐
  │ Fleet Bus │◄────────│ CLI/Poll │        │ CLI/Poll │
  │ :18800   │─────────►│          │        │          │
  └──────────┘          └──────────┘        └──────────┘
       ▲                                         │
       └─────────────────────────────────────────┘
                    Tailscale Network
```

## Message Format
```json
{
  "from": "00",
  "to": "01",       // or "all" for broadcast
  "msg": "message text",
  "type": "task|info|alert|result",
  "ts": 1234567890
}
```

## Free vs Pro (future)
- Free: basic messaging, broadcast, status
- Pro: encrypted messages, web dashboard, task queue, auto-discovery, message persistence
