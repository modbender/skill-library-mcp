---
name: Agent Swarm Network
version: 1.0.6
description: >
  Agent communication protocol skill. Provides: inter-agent messaging, context
  snapshot/restore, event-driven collaboration, model dispatch notifications,
  sub-agent management, task routing, file transfer, and network diagnostics.
  Invoke this Skill when cross-session context persistence, multi-agent coordination,
  or context overflow handling is needed.
  Built on top of Pilot Protocol (https://github.com/TeoSlayer/pilotprotocol).
---

# Agent Swarm Network — Agent Communication Skill

> A unified communication backbone for every AI tool in the OpenClaw ecosystem
> (OpenClaw / Antigravity / Codex).
>
> Analogy: This network = the Agent's nervous system. OpenClaw = the Agent's brain.

## Acknowledgments

This Skill is built on top of [Pilot Protocol](https://github.com/TeoSlayer/pilotprotocol) by [@TeoSlayer](https://github.com/TeoSlayer). Pilot Protocol provides the core daemon, encrypted tunnels, NAT traversal, and peer-to-peer addressing that this Skill leverages. Huge thanks to the Pilot Protocol team for building the Internet of Agents.

---

## Permissions & Privacy

**This Skill executes local CLI commands and writes files to the `~/.pilot/` directory.** Full transparency:

| Permission | What | Why |
|------------|------|-----|
| **CLI Exec** | `~/.pilot/bin/pilotctl` | All agent operations go through this binary |
| **File Write** | `~/.pilot/inbox/` | Context snapshots and incoming messages land here |
| **File Write** | `~/.pilot/received/` | Received files from peer agents |
| **File Read** | `~/.pilot/inbox/` | Reading snapshots for context restoration |
| **File Read** | `~/.pilot/received/` | Reading transferred files |
| **Network** | Local Unix socket | Daemon communication (localhost only) |
| **Network** | UDP tunnels (encrypted) | Agent-to-agent communication (AES-256-GCM) |
| **Script Exec** | `~/.pilot/context-snapshot.sh` | Context snapshot helper script |
| **Script Exec** | `~/.pilot/pilot-publish.sh` | Event publishing helper script |
| **Process** | Daemon lifecycle | Start/stop/status of the pilotctl daemon |

> **Privacy Note:** All inter-agent traffic is encrypted end-to-end using X25519 key exchange + AES-256-GCM. Agents are private by default and require mutual trust handshake before communication. No data passes through relay servers. The rendezvous registry defaults to localhost (`127.0.0.1:9000`) — no peer-discovery metadata leaves the machine unless you explicitly change `registry_url` to a remote address. Snapshots are unencrypted JSON; you must secure the `~/.pilot/` directory (`chmod 700`).

---

## Prerequisites

| Tool | Purpose | Required? |
|------|---------|-----------|
| **Pilot Protocol** | Core daemon + CLI (`pilotctl`) | ✅ Required |
| **OpenClaw** | Skill host + Agent orchestration | ✅ Required |

## Configuration

Edit `config.json` after installation:

```json
{
  "pilotctl_path": "~/.pilot/bin/pilotctl",
  "daemon_start_script": "~/.pilot/start-local.sh",
  "snapshot_script": "~/.pilot/context-snapshot.sh",
  "publish_script": "~/.pilot/pilot-publish.sh",
  "inbox_path": "~/.pilot/inbox/",
  "received_path": "~/.pilot/received/",
  "agent_hostname": "keke-agent"
}
```

| Field | Description | Default |
|-------|-------------|---------|
| `pilotctl_path` | Path to the pilotctl binary | `~/.pilot/bin/pilotctl` |
| `daemon_start_script` | Script to start the daemon | `~/.pilot/start-local.sh` |
| `snapshot_script` | Context snapshot helper script | `~/.pilot/context-snapshot.sh` |
| `publish_script` | Event publish helper script | `~/.pilot/pilot-publish.sh` |
| `inbox_path` | Directory for incoming messages/snapshots | `~/.pilot/inbox/` |
| `received_path` | Directory for received files | `~/.pilot/received/` |
| `agent_hostname` | This agent's hostname on the Pilot network | `keke-agent` |

### First-time Setup

1. **Install Pilot Protocol securely:** We strongly recommend **building from source** to eliminate supply-chain risk. Clone `https://github.com/TeoSlayer/pilotprotocol`, audit the source, compile via `go build`, and place the binary at `~/.pilot/bin/pilotctl`.
2. Secure your directories: `chmod 700 ~/.pilot`
3. Start the daemon: `~/.pilot/start-local.sh`
4. Verify: `~/.pilot/bin/pilotctl --json daemon status`

---

## Global Rules

1. All `pilotctl` commands use the full path: `~/.pilot/bin/pilotctl`
2. Always append the `--json` flag for structured output
3. Check the returned `status` field: `ok` = success, `error` = failure
4. On failure, read the `hint` field for remediation guidance

---

## ⚠️ Single-Node Mode (Current State)

Currently running with only one node (`keke-agent`). **Cannot send network messages to self** (publish/send-message will return `connection_failed`).

### Single-Node Workarounds

| Operation | Multi-node Command | Single-node Alternative |
|-----------|-------------------|------------------------|
| Publish event | `pilotctl publish keke-agent topic --data ...` | `~/.pilot/pilot-publish.sh topic '{"key":"val"}'` |
| Send to inbox | `pilotctl send-message keke-agent --data ...` | Write file directly to `~/.pilot/inbox/` |
| Context snapshot | `pilotctl send-message ...` | `~/.pilot/context-snapshot.sh` |
| Read inbox | `pilotctl inbox` → read `~/.pilot/inbox/` | Same (read directory directly) |
| Check status | `pilotctl info` | ✅ Works normally |
| Set tags | `pilotctl set-tags ...` | ✅ Works normally |

When a second node joins (e.g., VPS or another Mac), network commands will activate automatically.

---

## Capability 1: Context Snapshot & Restore (Highest Priority)

### 1.1 Save Context Snapshot

When a session ends, compaction triggers, or manual request is made, save critical context:

```bash
# Using the snapshot script (works in both single-node and multi-node)
~/.pilot/context-snapshot.sh SESSION_ID "Key summary of current context"

# Or manually write to inbox
echo '{"type":"context_snapshot","session_id":"ID","summary":"Summary"}' > ~/.pilot/inbox/snapshot_$(date +%Y%m%d_%H%M%S).json
```

### 1.2 Restore Context

When a new session starts, read the previous session's snapshot:

```bash
~/.pilot/bin/pilotctl --json inbox
```

Returns a `messages` array sorted by `received_at`. Read the most recent `context_snapshot` type message.

### 1.3 Context Overflow Protocol

When context usage exceeds 80%:

```
Step 1: Extract critical information from current context
Step 2: Serialize as JSON snapshot
Step 3: pilotctl send-message keke-agent --data "{snapshot}" --type json
Step 4: pilotctl publish keke-agent context.overflow --data "overflow at TOKEN_COUNT tokens"
Step 5: Suggest user starts a new session
Step 6: New session automatically restores from inbox
```

---

## Capability 2: Event-Driven Collaboration

### 2.1 Publish Events

When significant events occur, use `pilot-publish.sh` (automatically handles single-node/multi-node):

```bash
# Model switch
~/.pilot/pilot-publish.sh model.switch '{"from":"flash-lite","to":"opus-4.6","reason":"strategic analysis"}'

# Task completion
~/.pilot/pilot-publish.sh task.complete '{"task":"intelligence_ingestion","source":"twitter"}'

# Context compaction
~/.pilot/pilot-publish.sh context.compaction '{"before_tokens":150000,"after_tokens":30000}'

# Error alert
~/.pilot/pilot-publish.sh error.alert '{"type":"model_402","model":"gemini","action":"fallback"}'

# Intelligence ingested
~/.pilot/pilot-publish.sh intel.ingested '{"source":"url","title":"Article Title","category":"infra"}'
```

### 2.2 Subscribe to Events

Listen for specific topics (used by sub-agents or external monitors):

```bash
# Listen to all events
~/.pilot/bin/pilotctl --json subscribe keke-agent "*" --timeout 60s

# Listen only to model switches
~/.pilot/bin/pilotctl --json subscribe keke-agent model.switch --count 1

# Listen for error alerts
~/.pilot/bin/pilotctl --json subscribe keke-agent error.* --timeout 300s
```

### 2.3 Standard Event Topics

| Topic | Trigger | Data Schema |
|-------|---------|-------------|
| `context.snapshot` | Session end / manual save | `{session_id, summary, key_decisions}` |
| `context.overflow` | Token usage > 80% | `{token_count, threshold}` |
| `context.compaction` | Compaction triggered | `{before_tokens, after_tokens}` |
| `model.switch` | Model changed | `{from, to, reason}` |
| `model.error` | Model failure | `{model, error, fallback}` |
| `task.start` | Task initiated | `{task, type, model}` |
| `task.complete` | Task finished | `{task, result_summary}` |
| `task.error` | Task failed | `{task, error, retry}` |
| `intel.ingested` | Information ingested | `{source, title, category, value}` |
| `error.alert` | Error notification | `{type, details, action}` |
| `agent.spawn` | Sub-agent created | `{hostname, purpose, model}` |
| `agent.exit` | Sub-agent exited | `{hostname, reason, result}` |

---

## Capability 3: Sub-Agent Management

### 3.1 Naming Convention

```
Primary agent:    keke-agent
Sub-agents:       keke-sub-{purpose}  (e.g., keke-sub-code, keke-sub-writer)
Nested sub:       keke-sub-{purpose}-{n}
```

### 3.2 Spawning Sub-Agents

When OpenClaw needs to create a sub-agent for overflow tasks:

```bash
# Publish agent spawn event
~/.pilot/bin/pilotctl --json publish keke-agent agent.spawn \
  --data '{"hostname":"keke-sub-code","purpose":"code refactoring","model":"sonnet-4.6"}'
```

### 3.3 Collecting Sub-Agent Results

```bash
# Sub-agent sends results via Data Exchange
~/.pilot/bin/pilotctl --json send-message keke-agent \
  --data '{"type":"sub_agent_result","from":"keke-sub-code","result":"refactoring complete","files_changed":3}' \
  --type json

# Primary agent checks results
~/.pilot/bin/pilotctl --json inbox
```

---

## Capability 4: Task Routing

### 4.1 Route by Tags

Assign capability tags to different agents:

```bash
# Tag self
~/.pilot/bin/pilotctl --json set-tags orchestrator chinese fast
```

Tag conventions:

| Tag | Meaning | Best Fit Agent |
|-----|---------|---------------|
| `orchestrator` | Scheduling & dispatch | OpenClaw primary agent |
| `deep-reasoning` | Deep reasoning tasks | Antigravity (Opus) |
| `code-gen` | Code generation | Codex (Sonnet) |
| `local-inference` | Local model inference | LM Studio (Qwen) |
| `fast` | Fast responses | Flash Lite instances |
| `chinese` | Chinese language tasks | Qwen / Chinese-optimized models |

### 4.2 Find the Best Agent

```bash
~/.pilot/bin/pilotctl --json peers --search "code-gen"
```

---

## Capability 5: Model Dispatch Notifications

### 5.1 Publish Model Switch Events

Every model switch gets logged to the event stream:

```bash
~/.pilot/bin/pilotctl --json publish keke-agent model.switch \
  --data '{"from":"CURRENT_MODEL","to":"NEW_MODEL","reason":"reason","timestamp":"ISO8601"}'
```

### 5.2 Model Fallback Chain

On model failure, automatically publish degradation events:

```bash
~/.pilot/bin/pilotctl --json publish keke-agent model.error \
  --data '{"model":"gemini-3-flash","error":"402 quota exceeded","fallback":"minimax-m2.5"}'
```

---

## Capability 6: File Transfer

### 6.1 Send File

```bash
~/.pilot/bin/pilotctl --json send-file keke-agent /path/to/file
```

Files are saved to `~/.pilot/received/`.

### 6.2 View Received Files

```bash
~/.pilot/bin/pilotctl --json received
```

### 6.3 Use Cases

- Transfer context snapshot files
- Transfer code diffs
- Transfer analysis reports
- Share configuration across agents

---

## Capability 7: Network Diagnostics

### 7.1 Health Checks

```bash
# Daemon status
~/.pilot/bin/pilotctl --json daemon status

# Agent info
~/.pilot/bin/pilotctl --json info

# Connection list
~/.pilot/bin/pilotctl --json connections

# Peer list
~/.pilot/bin/pilotctl --json peers
```

### 7.2 Performance Testing

```bash
# Ping latency
~/.pilot/bin/pilotctl --json ping keke-agent --count 3

# Throughput benchmark
~/.pilot/bin/pilotctl --json bench keke-agent 1
```

---

## Capability 8: Gateway IP Bridging

### 8.1 Map Agent to Local IP

```bash
# Gateway bridging on user-space ports (>1024) does NOT require root/sudo.
~/.pilot/bin/pilotctl gateway start --ports 1234,8080 0:0000.0000.0001
```

Once mapped, standard HTTP tools can be used:
```bash
curl http://10.4.0.1:1234/v1/chat/completions  # Like calling LM Studio directly
```

### 8.2 Use Cases

- Expose LM Studio through Gateway as a Pilot address
- Unify all model endpoints under one entry point
- Access agent services with standard HTTP tools

---

## Capability 9: Webhook Real-time Monitoring

### 9.1 Set Up Webhook

```bash
~/.pilot/bin/pilotctl --json set-webhook http://localhost:8080/pilot-events
```

### 9.2 Event Types

All native daemon events are pushed to the webhook:
- `node.registered` / `node.reregistered`
- `conn.established` / `conn.fin` / `conn.rst`
- `handshake.received` / `handshake.approved`
- `message.received` / `file.received`
- `pubsub.published` / `pubsub.subscribed`
- `security.syn_rate_limited` / `security.nonce_replay`

---

## Standing Orders (Automation Rules)

### Rule 1: Snapshot Before Session End
Automatically execute a context snapshot (Capability 1.1) before every session ends.

### Rule 2: Critical Events Must Be Published
The following events must always be published to the Event Stream:
- Model switches
- Intelligence ingestion completions
- Task completions/failures
- Context compactions
- Error alerts

### Rule 3: Auto-Restore on New Session
On every new session start, check `pilotctl inbox` for the latest snapshot and restore context.

### Rule 4: Daemon Heartbeat
Check daemon status every 30 minutes. Auto-restart on failure.

---

## Troubleshooting

| Problem | Diagnostic Command | Solution |
|---------|--------------------|----------|
| Daemon not running | `pilotctl daemon status` | `~/.pilot/start-local.sh` |
| Registry unreachable | `pilotctl info` (check peers) | Verify rendezvous server is running |
| Messages not sending | `pilotctl connections` | Check trust state with target |
| Inbox overflowing | `pilotctl inbox` | `pilotctl inbox --clear` |
