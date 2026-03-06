---
name: agentrelay
description: Reliable agent-to-agent communication protocol for transferring large payloads via shared files with pointer references and secret code verification. Triggered by explicit 'AgentRelay:' prefix in messages.
metadata: {"openclaw":{"triggerPatterns":["AgentRelay:","Please use AgentRelay skill to handle","Use AgentRelay"],"emoji":"📨"}}
---

# AgentRelay 📨

**Reliable Agent-to-Agent Communication Protocol** — Solves `sessions_send` timeout issues for large payloads using shared files + short message pointers.

## 🎯 When to Use This Skill

**When you see messages like the following**, immediately use this Skill to handle:

```
Please use AgentRelay skill to handle this message:
REQ,r1_r,s/r1_r.json,,
```

Or

```
📨 AgentRelay Protocol Message

Please use AgentRelay skill to handle:
- Message Type: REQ
- Event ID: r1_r  
- File Pointer: s/r1_r.json
```

**Key Trigger Phrases**:
- "use AgentRelay skill to handle"
- "AgentRelay protocol message"
- "Use AgentRelay"

When you see these keywords, **immediately execute the Commands below**!

## 🚀 Quick Start

### Standard Flow After Receiving AgentRelay Message

**Step 1: Parse Message**
```bash
python3 {baseDir}/run_relay.py receive "REQ,r1_r,s/r1_r.json,,"
```

Example output:
```json
{
  "type": "REQ",
  "event_id": "r1_r",
  "content": {"task": "write_poem", "sender_color": "red"},
  "secret": "ABC123"
}
```

**Step 2: Understand Task and Execute**

Check the `content` field to understand what needs to be done (e.g., write poem, analyze data, generate report).

**Step 3: Update Result**
```bash
python3 {baseDir}/run_relay.py complete r1_r "Task completed" "agent:red:red"
```

**Step 4: Send CMP Confirmation**
```bash
# generate CMP message (done automatically by run_relay.py complete)
# Output: CMP,r1_r,,,ABC123
# Then send via sessions_send
sessions_send(target='agent:red:red', message='CMP,r1_r,,,ABC123')
```

---

## 📚 Commands

### `receive <csv_message>`

Parse AgentRelay CSV message and read shared file content.

**Parameters**:
- `csv_message`: CSV format message (without `AgentRelay:` prefix)

**Example**:
```bash
python3 {baseDir}/run_relay.py receive "REQ,r1_r,s/r1_r.json,,"
```

**Output** (JSON):
```json
{
  "type": "REQ",
  "event_id": "r1_r",
  "ptr": "s/r1_r.json",
  "content": {...},
  "secret": "ABC123"
}
```

---

### `update <event_id> <json_updates>`

Update shared file content.

**Parameters**:
- `event_id`: Event ID
- `json_updates`: JSON format updates (merged into `payload.content`)

**Example**:
```bash
python3 {baseDir}/scripts/handle_relay.py update r1_r '{"status":"completed","result":"done"}'
```

**Output**:
```json
{"status":"ok","file":"/path/to/r1_r.json","ptr":"s/r1_r.json"}
```

---

### `ack <event_id> <secret>`

Generate ACK confirmation message.

**Parameters**:
- `event_id`: Event ID
- `secret`: Secret Code read from file

**Example**:
```bash
python3 {baseDir}/scripts/handle_relay.py ack r1_r ABC123
```

**Output**:
```json
{
  "status": "ok",
  "ack_message": "ACK,r1_r,,,ABC123",
  "instruction": "Call sessions_send with message='ACK,r1_r,,,ABC123'"
}
```

---

## 🔄 Complete Communication Flow

### Sender Agent

```python
# 1. Prepare data
content = {
    "task": "write_poem",
    "sender": "red",
    "receiver": "orange",
    "sender_color": "red",
    "receiver_color": "orange"
}

# 2. Write to shared file
from agentrelay.api import agentrelay_send
result = agentrelay_send("orange", "REQ", "r1_r", content)

# 3. Send message with prefix
message = f"AgentRelay: {result['csv_message']}"
sessions_send(target='agent:orange:main', message=message)
```

### Receiver Agent

```bash
# 1. Receive message: AgentRelay: REQ,r1_r,s/r1_r.json,,

# 2. Parse message
python3 {baseDir}/scripts/handle_relay.py receive "REQ,r1_r,s/r1_r.json,,"
# → Get content and secret

# 3. Understand task, call LLM to execute
# (This is your LLM capability)

# 4. Update result
python3 {baseDir}/scripts/handle_relay.py update r1_r '{"status":"completed"}'

# 5. Send ACK
ACK_OUTPUT=$(python3 {baseDir}/scripts/handle_relay.py ack r1_r SECRET)
ACK_MSG=$(echo "$ACK_OUTPUT" | jq -r '.ack_message')
sessions_send(target='agent:red:main', message="$ACK_MSG")
```

---

## 📊 Message Format Details

### CSV Format

```
TYPE,ID,PTR,,DATA
```

**Field Descriptions**:
- `TYPE`: Message type (REQ | ACK | NACK | PING)
- `ID`: Event ID (unique identifier)
- `PTR`: File pointer (e.g., `s/event_id.json`)
- `RESERVED`: Reserved field (leave empty)
- `DATA`: Additional data (Secret Code for ACK)

**Examples**:
```
REQ,r1_r,s/r1_r.json,,          # Request
ACK,r1_r,,,ABC123               # Confirmation
NACK,r1_r,,,File not found      # Rejection
PING,test_1,,,,                 # Heartbeat test
```

### Full Message (with prefix)

```
AgentRelay: REQ,r1_r,s/r1_r.json,,
```

**Why need prefix?**
- ✅ Clearly identifies this as AgentRelay protocol message
- ✅ LLM immediately knows to call AgentRelay Skill when seeing it
- ✅ Avoids confusion with other messages

---

## 🛡️ Security Mechanisms

### 1. Secret Code Verification

- Sender generates 6-character random code (e.g., `ABC123`)
- Secret is written to file
- Receiver must return the same Secret when ACKing
- Sender verifies Secret matches, ensuring receiver actually read the file

### 2. Burn-on-read (Optional)

When `burn_on_read=true` is set, file is automatically deleted after reading to protect sensitive data.

### 3. Integrity Check

File content includes SHA-256 hash to prevent tampering.

---

## 📁 Data Storage

- **Shared Files**: `~/.openclaw/data/agentrelay/storage/*.json`
- **Transaction Logs**: `~/.openclaw/data/agentrelay/logs/transactions_*.jsonl`
- **Registry**: `~/.openclaw/data/agentrelay/registry.json`

---

## 🧪 Testing and Examples

### Ping Test
```bash
python3 {baseDir}/scripts/ping_relay.py
```

### 5-Hop Relay Test
```bash
python3 {baseDir}/examples/relay_5hops.py
```

### 10-Hop Relay Test
```bash
python3 {baseDir}/examples/relay_10hops.py
```

---

## ❓ FAQ

### Q: Why use AgentRelay instead of direct sessions_send?

A: `sessions_send` tends to timeout when transmitting messages larger than 30 characters. AgentRelay uses shared files + short pointers (less than 30 characters) to transmit arbitrarily large data.

### Q: What is Secret Code for?

A: Secret Code is a 6-character random code used to verify the receiver actually read the file. Receiver must return the correct Secret in ACK.

### Q: How long are files retained?

A: Files are retained for 24 hours by default. You can adjust this with `ttl_hours` parameter, or enable `burn_on_read` to delete immediately after reading.

---

## 📖 More Documentation

- [README.md](https://github.com/your-repo/agentrelay/blob/main/README.md) - Project overview
- [ARCHITECTURE.md](https://github.com/your-repo/agentrelay/blob/main/ARCHITECTURE.md) - Architecture design
- [API.md](https://github.com/your-repo/agentrelay/blob/main/API.md) - API reference
- [DEPLOYMENT.md](https://github.com/your-repo/agentrelay/blob/main/DEPLOYMENT.md) - Deployment guide

---

**Version**: v1.0.1-alpha.3  
**Last Updated**: 2026-02-28  
**Author**: AgentRelay Team  
**Maintainer**: AgentRelay Team
