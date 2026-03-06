# Proxy Recovery Pattern

**Use case:** Define what "dying cleanly" means for a sacrificial security proxy, and how core responds when a proxy crashes — adversarially or otherwise.

**Companion to:** `security-proxy.md`

---

## The Problem

The blast shield philosophy says "when attacked, proxy dies alone." That's correct. But without a defined recovery protocol, you get:

- Silent failures (proxy dies, nobody knows, task hangs)
- Poisoned state (proxy wrote bad data before dying; core uses it)
- Blind re-spawns (core re-spawns without knowing what happened)
- Unnotified humans (adversarial attack happens, nobody pings the owner)

This template defines the full lifecycle: graceful shutdown → crash report → core response → optional quarantine → human notification.

---

## Shutdown Trigger Conditions

| Trigger | Category | Severity |
|---|---|---|
| Stage 4 injection detection fired | Adversarial | Critical |
| Forbidden tool call attempted | Policy violation | Critical |
| Burn limit hit (rate limiter) | Resource exhaustion | Medium |
| Unhandled exception / OOM | Bug | Low–Medium |
| Auth failure (token expired) | Configuration | Low |
| Task completed normally | Clean | None |

---

## Pre-Death Checklist

Before terminating for **any** reason, the proxy executes this checklist in order:

```javascript
async function gracefulShutdown(trigger, triggerDetail, sessionStats) {
  // 1. Flush audit log
  await auditLog.flush();

  // 2. Write crash report (even on clean shutdown — trigger: "TASK_COMPLETE")
  const report = {
    crash_id:                    `crash-${new Date().toISOString()}`,
    timestamp:                   new Date().toISOString(),
    trigger,                     // See trigger table above
    trigger_detail:              triggerDetail,
    last_action:                 sessionStats.lastToolCall,
    session_request_count:       sessionStats.requestCount,
    // Adversarial only: hash + length, NEVER the content itself
    suspicious_content_hash:     trigger.adversarial ? sessionStats.suspiciousHash : null,
    suspicious_content_length:   trigger.adversarial ? sessionStats.suspiciousLength : null,
    adversarial:                 trigger.adversarial ?? false,
    files_written_this_session:  sessionStats.filesWritten
  };

  await fs.writeFile(
    `logs/crash-${Date.now()}.json`,
    JSON.stringify(report, null, 2)
  );

  // 3. Mark in-progress drafts ABANDONED
  for (const draft of await listInProgressDrafts()) {
    await markAbandoned(draft);
  }

  // 4. Release credentials (do NOT write token to disk)
  sessionToken = null;

  // 5. Exit
  process.exit(trigger.adversarial ? 1 : 0);
}
```

**If the proxy is killed externally (OOM, SIGKILL) before completing the checklist:**
Core treats it as a potential adversarial crash — worst-case assumption, then verify.

---

## Crash Report Schema

```json
{
  "crash_id": "crash-2026-02-23T14:32:01.443Z",
  "timestamp": "2026-02-23T14:32:01.443Z",
  "trigger": "INJECTION_DETECTED",
  "trigger_detail": "Stage 4: pattern 'ignore_prev_instructions' matched",
  "last_action": "web_fetch: moltbook.com/threads/4829",
  "session_request_count": 47,
  "suspicious_content_hash": "a3f9b2c1d4e5f6a7",
  "suspicious_content_length": 2841,
  "adversarial": true,
  "files_written_this_session": [
    "posts/thread-4829-clean.json",
    "logs/audit.jsonl"
  ]
}
```

**Logging rules:**
- Suspicious content: hash + length ONLY — never the payload itself
- File paths: relative to proxy workspace (never absolute system paths)
- Credentials: never appear anywhere in the report

---

## Core Agent Response Decision Tree

```
Core reads crash-*.json
        │
        ├─ File missing (proxy killed externally, no report)
        │         └─ Treat as potential adversarial → investigate before re-spawn
        │
        ├─ adversarial: false
        │   ├─ BURN_LIMIT / AUTH_FAILURE → re-spawn with same task, log incident
        │   ├─ EXCEPTION → investigate root cause, fix if known, then re-spawn
        │   └─ TASK_COMPLETE → normal; no action needed
        │
        └─ adversarial: true
                  │
                  ├─ files_written_this_session: [] (wrote nothing)
                  │         └─ Alert human immediately
                  │            Hold re-spawn until human clears
                  │
                  └─ files_written_this_session: [non-empty]
                            └─ QUARANTINE MODE (see below)
                               Alert human immediately
                               Do NOT re-spawn until cleared
```

---

## Quarantine Mode

**Trigger:** Adversarial crash AND proxy wrote files during the session.

**Why:** A compromised proxy may have written poisoned data (e.g., tampered `relationships.json`, injected content in `posts/`). Don't trust anything it touched.

**Steps:**

```bash
# 1. Archive entire proxy workspace
mv moltbook/ moltbook-quarantine-$(date +%Y%m%dT%H%M%S)/

# 2. Restore from last known-good backup
cp backups/relationships-$(date +%Y%m%d).json moltbook/relationships.json
# (Assumes daily backup — see backup schedule below)

# 3. Flag modified relationships for review
# For each relationship in crash report's files_written list:
# → Set "status": "REVIEW_REQUIRED" in restored relationships.json

# 4. Create fresh workspace directories
mkdir -p moltbook/{posts,drafts,logs}

# 5. DO NOT re-spawn until human reviews and explicitly clears quarantine
```

**Known-good backup schedule:**
```bash
# Core agent maintains daily snapshot (not the proxy)
0 3 * * * cp moltbook/relationships.json backups/relationships-$(date +%Y%m%d).json
find backups/ -name "relationships-*.json" -mtime +30 -delete  # 30-day retention
```

---

## Human Notification

| Crash type | Notification |
|---|---|
| Clean (TASK_COMPLETE) | None |
| Non-adversarial (burn limit, auth, bug) | Log only; ping human if 3+ same-type in 24h |
| Adversarial (injection, policy violation) | **Immediate Discord/channel alert** |

**Adversarial alert format:**
```
🚨 [ProxyName] adversarial crash
Trigger: {trigger} — {trigger_detail}
Session requests: {session_request_count}
Files written: {files_written_this_session.length}
Action required: Review crash-{timestamp}.json
Quarantine: {ACTIVE | not triggered}
```

---

## Re-Spawn Decision Guide

| Situation | Action |
|---|---|
| Clean task completion | No re-spawn needed |
| Non-adversarial crash, root cause known | Re-spawn after fixing root cause |
| Non-adversarial crash, root cause unknown | Investigate first, then re-spawn |
| Adversarial crash, no files written | Human review → clear → re-spawn |
| Adversarial crash, files written | Quarantine → backup restore → human review → re-spawn |
| Missing crash report (SIGKILL) | Treat as adversarial with files written |
| Same crash type 3× in 24h (non-adversarial) | Escalate to human — pattern suggests systemic issue |

---

## Integration with Security Proxy Template

The pre-death checklist and crash report schema are defined here as a standalone reference. The `security-proxy.md` template references this file for recovery behavior.

**Recommended file layout:**
```
[proxy-workspace]/
├── posts/           ← scraped/processed content
├── drafts/          ← outgoing content pending approval
├── logs/
│   ├── audit.jsonl  ← append-only audit trail (all tool calls, events)
│   └── crash-*.json ← one file per termination event
└── backups/
    └── relationships-YYYYMMDD.json  ← daily snapshots (written by core, not proxy)
```

---

## Checklist for New Proxy Implementations

- [ ] `gracefulShutdown()` called on all exit paths (success, error, signal handlers)
- [ ] Crash report written even on clean shutdown (trigger: `TASK_COMPLETE`)
- [ ] In-progress drafts marked `ABANDONED` before exit
- [ ] Credentials never written to disk (token = null before exit)
- [ ] Core has crash report reading logic implemented
- [ ] Daily backup cron for any mutable state (relationships, config)
- [ ] Human alert channel configured for adversarial crash notifications
- [ ] Quarantine restore procedure tested (simulate adversarial crash, verify clean restore)
