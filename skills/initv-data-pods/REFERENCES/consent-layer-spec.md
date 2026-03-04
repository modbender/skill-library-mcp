# Agent Consent Layer — Technical Spec v0.1

## Vision
Personal data firewall for AI agents. You choose what pods to expose per interaction. Agents only see what you permit.

---

## Architecture

```
┌─────────────┐      ┌──────────────────┐      ┌─────────────────┐
│   User      │ ───► │  Consent Layer   │ ───► │   Data Pods     │
│ (You)       │      │  (Gateway)       │      │   (SQLite)      │
└─────────────┘      └──────────────────┘      └─────────────────┘
                            │
                            ▼
                    ┌──────────────────┐
                    │   Requesting      │
                    │   Agent          │
                    │ (External AI)    │
                    └──────────────────┘
```

---

## Components

### 1. Pod Registry
- Index all pods in `~/.openclaw/data-pods/`
- Track: name, type, created, tags, last accessed
- JSON config: which pods exist

### 2. Consent Manager
- Per-session consent storage
- Which pods are currently allowed for this agent
- Timeout: auto-revoke after N minutes
- Audit log: what was accessed when

### 3. Access Gateway
- Intercepts agent queries
- Checks consent before allowing pod access
- Returns only allowed data

### 4. Selection UI (CLI/UI)
- List available pods
- Agent declares what it needs
- User approves/denies
- "Remember for this session" option

---

## Data Structures

### Pod Manifest
```yaml
name: scholar-2024
type: scholar
tables:
  - notes
  - embeddings
tags: [research, ai, papers]
created: 2024-01-15
version: 0.1
```

### Consent Record
```json
{
  "session_id": "abc123",
  "agent": "claude-code",
  "pods_allowed": ["scholar-2024", "projects"],
  "expires_at": "2024-01-15T10:00:00Z",
  "created_at": "2024-01-15T09:30:00Z"
}
```

### Audit Log
```json
{
  "timestamp": "2024-01-15T09:35:00Z",
  "session_id": "abc123",
  "agent": "claude-code",
  "pod": "scholar-2024",
  "query": "SELECT * FROM notes WHERE tags LIKE '%ai%'",
  "rows_returned": 12
}
```

---

## Workflows

### 1. New Agent Request
```
[Agent] → "I need context about your research"
[Consent Manager] → Check existing consent
  → If valid: pass to pods
  → If none: prompt user
```

### 2. User Approval
```
[Consent Manager] → Show available pods:
  ☑ scholar-2024 (research papers)
  ☐ health-data (wearables)
  ☐ projects (workspace)
  
User selects → [Consent Manager] stores consent → Agent receives data
```

### 3. Query Execution
```
[Agent] → "What papers on transformers?"
[Access Gateway] → 
  1. Validate session consent
  2. Filter to allowed pods only
  3. Execute query against allowed pods only
  4. Log to audit
  5. Return results
```

### 4. Consent Revocation
```
User → "Revoke access"
[Consent Manager] → Remove consent for session
[Access Gateway] → Future queries blocked
```

---

## API Design (OpenClaw Skill)

```bash
# List pods
consent list

# Show current consent state
consent status --session <id>

# Grant access
consent grant <pod1> <pod2> --session <id> --duration 30m

# Revoke
consent revoke --session <id>

# Audit
consent audit --session <id>
consent logs --today
```

---

## Security

- **No default access** — Everything opt-in
- **Time-bounded** — Consent expires
- **Audit everything** — Full traceability
- **No lateral movement** — Agent can't probe unallowed pods
- **Local only** — Data never leaves your machine

---

## Future Features

- [ ] Remember consent for trusted agents
- [ ] Pod-specific column/row filtering
- [ ] Time-limited data (e.g., "last 30 days only")
- [ ] Multi-device sync (encrypted)
- [ ] Agent reputation system

---

## Why This Matters

Current AI = all or nothing
- Give access = give everything
- Privacy impossible

Consent AI = granular control
- Agent sees only what you choose
- Privacy by design
- Trust through transparency

---

## Name Ideas

- **ConsentOS**
- **PodGate**
- **ScopeAI**
- **DataFirewall**
- **SelectiveMemory**
- **AgentWall**

---

## Next Steps

1. Build v0.1: CLI consent manager
2. Integrate with OpenClaw gateway
3. Test with one external agent
4. Add UI for pod selection
5. Publish as product
