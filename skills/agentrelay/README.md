# AgentRelay 📨

**Reliable Agent-to-Agent Communication Protocol** — Solves `sessions_send` timeout issues for large payloads using shared files + short message pointers.

---

## 🎯 Core Value

When your agents need to send messages **larger than 30 characters**, `sessions_send` tends to timeout. AgentRelay provides the solution:

| Traditional Approach | AgentRelay Approach |
|---------------------|---------------------|
| ❌ Send large text directly → ⏰ Timeout | ✅ Write to file + send short pointer → Success |
| ❌ No verification if received | ✅ Secret Code mechanism ensures delivery |
| ❌ No audit trail | ✅ Complete transaction logs (4 entries/event) |

---

## 🚀 Quick Start

### 1️⃣ Install

```bash
clawhub install agentrelay
```

### 2️⃣ Send Message

```python
from agentrelay import AgentRelayTool

# Prepare data
content = {"task": "write_poem", "theme": "spring"}

# Write to shared file and get CSV message
result = AgentRelayTool.send("yellow", "REQ", "hop1", content)

# Send to target agent
sessions_send(
    target='agent:yellow:yellow',
    message=f"AgentRelay: {result['csv_message']}"
)
```

### 3️⃣ Receive Message

```bash
# Use unified script to parse
python3 scripts/run_relay.py receive "REQ,hop1,s/hop1.json,,"
```

Output:
```json
{
  "type": "REQ",
  "event_id": "hop1",
  "content": {"task": "write_poem", ...},
  "secret": "ABC123"
}
```

### 4️⃣ Complete Task and Reply

```bash
python3 scripts/run_relay.py complete hop1 "Task completed" "agent:red:red"
```

Output:
```
✅ Updated hop1
✅ CMP: CMP,hop1,,,ABC123
```

---

## 🔄 Complete Flow

```
Sender                          Receiver
  |                              |
  |-- 1. REQ (with file ptr) --->|
  |                              |-- receive()
  |                              |-- 📍 LOG #1: REQ/RECEIVED
  |                              |-- 📍 LOG #2: ACK/ACKNOWLEDGED
  |                              |
  |<-- 2. ACK (implicit confirm)-|  
  |                              |
  |                    [Executing task...]
  |                              |
  |<-- 3. CMP (with Secret) -----|-- ack()
  |                              |-- 📍 LOG #3: CMP/COMPLETED
  |                              |
  |                    [Preparing for next hop]
  |                              |-- 📍 LOG #4: CREATE_POINTER/PREPARING
```

---

## 📊 Message Format

### CSV Format

```
TYPE,ID,PTR,,DATA
```

**Examples**:
```
REQ,event_001,s/event_001.json,,          # Request
CMP,event_001,,,ABC123                     # Complete (with Secret)
```

### Full Message (with prefix)

```
AgentRelay: REQ,event_001,s/event_001.json,,
```

---

## 🔒 Security Mechanisms

### Secret Code Verification

1. Sender generates 6-character random code (e.g., `ABC123`)
2. Secret is written to file
3. Receiver must return the same Secret in CMP
4. Sender verifies Secret matches

### Complete Logging

All operations automatically logged to:
```
~/.openclaw/data/agentrelay/logs/transactions_YYYYMMDD.jsonl
```

Each record contains:
- timestamp, event_id, type, status
- sender, receiver (real agent IDs)
- next_action_plan (next step plan)

---

## 🎮 Real-World Examples

### Example 1: 5-Hop Poetry Relay
- **Theme**: Four Seasons Cycle
- **Format**: Seven-character regulated verse with topological linkage
- **Validates**: Basic protocol functionality
- [View Details](./examples/5hop_relay.md)

### Example 2: Wuxia + Disney Story Relay
- **Theme**: Legend of Peach Blossom Island Overseas
- **Format**: Creative writing with continuous plot twists
- **Validates**: Autonomous agent communication + new logging system
- **Highlights**: 5 brilliant plot twists, converging into epic narrative
- [View Details](./examples/wuxia_disney_relay_final.md)

### Example 3: Autonomous Mahjong Game 🀄
- **Theme**: Multi-agent mahjong game with 5 players
- **Format**: Complex coordination (30-60 min autonomous gameplay)
- **Validates**: Advanced multi-agent collaboration + state management
- **Highlights**: 
  - 5 agents (Yellow=Dealer, Red/Green/Blue/Orange=Players)
  - Blood Flow mode (game continues after first win)
  - Complete game state synchronization via AgentRelay
  - Automatic win validation and scoring
- **Duration**: ~1 hour (setup + game + scoring)
- [View Full Guide](./examples/mahjong_relay.md)

#### Mahjong Example Quick Preview

```
Game Flow:
1. Yellow shuffles 108 tiles and deals hands
2. Yellow sends each player their hand via AgentRelay
3. Red (East) draws 14th tile and plays
4. Yellow broadcasts move to all players
5. Green/Blue/Orange respond (PONG/KONG/WIN/PASS)
6. Next player's turn (clockwise)
7. Repeat until someone wins
8. Blood Flow: continue until 3 players win
9. Yellow calculates scores and announces ranking
```

**Key Learning**: See how AgentRelay handles complex state synchronization across 5 agents with complete audit trail!

---

## 📁 Project Structure

```
skills/agentrelay/
├── SKILL.md              # ClawHub skill documentation
├── SKILL.py              # Skill entry point
├── __init__.py           # Core implementation (AgentRelayTool)
├── handle_relay.py       # Legacy handler script
├── run_relay.py          # Unified execution script ✨Recommended
├── clawhub.json          # ClawHub manifest
├── README.md             # This document
├── docs/
│   ├── PROTOCOL.md       # Protocol specification
│   ├── API.md            # API reference
│   ├── LOGGING.md        # Logging system
│   └── CHANGELOG.md      # Change log
└── examples/
    ├── 5hop_relay.md     # Poetry relay example
    └── wuxia_disney_relay_final.md  # Wuxia+Disney example
```

---

## 🛠️ API Reference

### AgentRelayTool Class

#### send(agent_id, msg_type, event_id, content)
Send message to shared file.

**Parameters**:
- `agent_id` (str): Target agent ID
- `msg_type` (str): "REQ", "CMP", "NACK"
- `event_id` (str): Unique event identifier
- `content` (dict): Message content

**Returns**:
```python
{
    "file_path": "/path/to/event_id.json",
    "ptr": "s/event_id.json",
    "csv_message": "REQ,event_id,s/event_id.json,,",
    "secret": "ABC123"
}
```

#### receive(csv_msg)
Parse and read shared file.

**Parameters**:
- `csv_msg` (str): CSV format message (without `AgentRelay:` prefix)

**Returns**:
```python
{
    "type": "REQ",
    "event_id": "hop1",
    "content": {...},
    "secret": "ABC123"
}
```

#### update(event_id, updates, next_event_id=None)
Create pointer file for next hop.

**Parameters**:
- `event_id` (str): Current event ID
- `updates` (dict): Fields to update
- `next_event_id` (str, optional): Next hop event ID

#### ack(event_id, secret)
Generate CMP (Complete) message.

**Parameters**:
- `event_id` (str): Event ID
- `secret` (str): Secret Code

**Returns**: `str` - `"CMP,event_id,,,ABC123"`

---

## 📝 Changelog

### v2.0.0 - English Documentation

**Changes**:
- ✅ All documentation converted to English
- ✅ Removed all personal information and hardcoded paths
- ✅ Environment variable configuration for data directory
- ✅ Cross-platform compatibility (macOS/Linux/Windows)

### v1.4.0 - Critical Security Fix

**Fixes**:
- ✅ Removed all hardcoded paths
- ✅ Use `Path(__file__)` for dynamic script path resolution
- ✅ Use `OPENCLAW_DATA_DIR` environment variable for data directory
- ✅ Safe multi-user environment isolation

[View Full Changelog](./docs/CHANGELOG.md)

---

## 🤝 Contributing

1. Fork this project
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📄 License

MIT License - See [LICENSE](./LICENSE) for details

---

## 📞 Contact

- **Project Homepage**: https://clawhub.ai/skills/agentrelay
- **Documentation**: https://docs.openclaw.ai/skills/agentrelay

---

**📨 Enjoy reliable agent communication!**
