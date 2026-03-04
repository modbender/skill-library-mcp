# Task Routing Rules

## Decision Tree

```
User Request
    |
    ├─→ Kendin yapabilir misin?
    │   ├─→ Evet → Yap ve sonuçlan
    │   └─→ Hayır ↓
    │
    ├─→ can_assign_to kontrol et
    │   ├─→ Uygun agent var mı?
    │   │   ├─→ Evet → sessions_send(agent)
    │   │   │   └─→ Tamamlandı mı?
    │   │   ├─→ Hayır ↓
    │   │   └─→ Agent yanıt vermedi? ↓
    │   │
    │   └─→ Uygun agent yok ↓
    │
    ├─→ reports_to'ya sor
    │   ├─→ Agent mı? → sessions_send(supervisor)
    │   └─→ İnsan mı? → message(channel=target)
    │
    └─→ Çözülemedi → escalation_path yukarı çık
```

## Approval Protocol (Handshake)

Before executing a task assigned by another agent:

1.  **Check Origin:** Is the sender in `auto_accept_from`?
    *   **Yes:** Accept and start task.
    *   **No:** Check `requires_approval`.
        *   `false`: Accept and start task.
        *   `true`: **HOLD** task and request approval.

2.  **Request Approval:**
    *   Send internal message to specific `reports_to` target.
    *   "Agent X wants to assign task Y. Approve?"

3.  **Result:**
    *   **Approved:** Notify Sender "Accepted", start task.
    *   **Denied:** Notify Sender "Rejected". Sender must find another route or escalate.

## Routing Heuristics

### SAP Tasks (Keywords)
- ABAP, FI, CO, MM, SD, HANA, BAPI, IDoc, CDS, S/4HANA
→ Check for SAP agent → If not, spawn with SAP context

### Development Tasks (Keywords)
- code, programming, bug fix, API, frontend, backend, web app, mobile app
→ Check for dev agent → If not, spawn with dev context

### Research Tasks (Keywords)
- research, analyze, study, investigate, find, discovery
→ Check for research agent → If not, spawn with research context

### General Tasks (Default)
- conversation, planning, brainstorming, general assistance
→ Handle as main agent

---

## Agent Communication Matrix

| From | To | Method | Tool | Notes |
|------|----|--------|------|-------|
| main | sub-agent (spawn) | sessions_send | sessions_send | Message running agent |
| main | new agent | sessions_spawn | sessions_spawn | Create new session |
| agent | supervisor (agent) | sessions_send | sessions_send | Internal routing |
| agent | human (Ilkerkaan) | message | message | Telegram channel |

---

## spawn vs send vs message

| Method | When to Use | Tool | Context |
|--------|-------------|------|---------|
| `sessions_spawn` | New task, isolated context, fresh start | Create sub-agent | No history |
| `sessions_send` | Continue existing conversation, add context | Message running agent | Has history |
| `message` | Human notification, external channel | Send to channel | Not a session |

---

## Escalation Flow

```
Level 0: User Request
    ↓
Level 1: main (agent)
    ├─→ can_assign_to? → Delegate
    └─→ Can't solve? → Escalate
        ↓
Level 2: Ilkerkaan (human)
    └─→ Direct notification via Telegram
```

---

## Delegation Protocol

When assigning task to another agent:

```javascript
// 1. Check can_assign_to
if (agent.can_assign_to.includes(targetAgentId)) {
  
  // 1b. Check if target requires details (Handshake)
  const targetCard = getAgentCard(targetAgentId);
  
  // 2. Prepare task context
  const task = {
    from: 'main',
    originalUserRequest: userRequest,
    context: { /* relevant info */ },
    deadline: timestamp,
    reportTo: 'main', 
    handshake: {
        request_id: uuid(),
        requires_ack: true
    }
  };

  // 3. Send or spawn
  if (agentIsRunning) {
    sessions_send(sessionKey, task);
  } else {
    sessions_spawn(task, agentId);
  }
} else {
  // 4. Escalate to reports_to
  escalate(task);
}
```

---

## Reporting Protocol

When task is completed or fails:

```javascript
// 1. Prepare report
const report = {
  task: originalTask,
  status: 'completed' | 'failed' | 'blocked',
  result: { /* output */ },
  error: errorIfAny,
  timestamp: now
};

// 2. Send to reports_to
if (reports_to.type === 'agent') {
  sessions_send(reports_to.sessionKey, report);
} else if (reports_to.type === 'human') {
  message(action='send', channel=reports_to.channel, text=summary);
}
```
