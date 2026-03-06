# Session Security Checks

## What to Examine

Session configuration from `config.sessions` and `config.agents.defaults`.

## Check 1: DM Scope

**Location**: `sessions.dmScope` or default behavior

| Scope | Risk Level | Notes |
|-------|------------|-------|
| `main` | Depends | All DMs share context (default) |
| `per-peer` | 🟢 Low | Isolated by sender |
| `per-channel-peer` | 🟢 Low | Isolated by channel+sender |
| `per-account-channel-peer` | 🟢 Low | Most isolated |

**Risk with `main` scope**:
- Multiple users DM the same bot = shared context
- User A's secrets visible to User B

**Context-Aware Assessment**:
```
Single user (personal deployment) + main scope = 🟢 Low (no risk)
Multi-user + main scope = 🔴 Critical (session leak)
Unknown user count + main scope = 🟡 Medium (ask user)
```

**Finding if multi-user + main scope**:
- Scenario: `session-leak`
- Recommendation: Switch to `per-peer` or more specific

## Check 2: Session Memory

**Location**: `agents.defaults.memorySearch`

| Setting | Consideration |
|---------|---------------|
| `enabled: true` | Sessions can search past conversations |
| `provider: local` | Memory stored locally |
| `provider: api` | Memory sent to external API |

**Risks**:
- Memory search across sessions could leak data
- External provider = data leaves your control

## Check 3: Workspace per Session

**Location**: `agents.list[].workspace`

**Check if sessions share workspace**:
- Files created in one session accessible to others
- Credentials, notes, generated content could leak

**Single workspace for all agents**: 🟡 Medium
- Recommend separate workspaces for external-facing agents

## Check 4: Session Persistence

**Location**: `~/.openclaw/agents/<agentId>/sessions/`

**Check**:
- Old session logs accumulating
- Sensitive data in session history
- Permissions on session directories

**If sessions contain sensitive data**:
- Recommend periodic cleanup
- Verify `chmod 600` on session files

## Check 5: Context Pruning

**Location**: `agents.defaults.contextPruning`

| Mode | Notes |
|------|-------|
| `none` | Full context kept |
| `cache-ttl` | Prunes after time |
| (others) | Various strategies |

**No pruning + long sessions**:
- Old context may contain sensitive data
- Larger attack surface for context manipulation

## Multi-User Environment Checks

If the deployment serves multiple users:

### A. Session Isolation Verification
- Each user should have isolated sessions
- Test: Can user A's data appear in user B's context?

### B. Workspace Isolation
- Users should not share workspace
- Or workspace should have per-user subdirectories

### C. Memory Isolation
- Memory search should be scoped to user
- Check if cross-user memory access is possible

## Recommendations

| Scenario | Recommended Config |
|----------|-------------------|
| Single user, personal | `main` scope OK |
| Multi-user, same team | `per-peer` minimum |
| Public bot | `per-channel-peer` + separate workspace |
| Enterprise | Full isolation + audit logging |
