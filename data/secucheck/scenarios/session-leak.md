# Session Data Leak Scenario

## Overview

Session leaks occur when data from one user's session becomes accessible to another user, either through shared context, workspace files, or memory systems.

## Attack Flow

```
1. User A interacts with bot, shares sensitive info
   ↓
2. Info stored in session context / workspace / memory
   ↓
3. User B starts conversation with same bot
   ↓
4. User B can access or infer User A's data
   ↓
5. Confidential information exposed
```

## Example Scenarios

### Scenario A: Shared Main Session

**Setup**: `dmScope: main` (default), multiple users can DM

```
[User A - Telegram DM]
User A: 내 신용카드 번호는 1234-5678-9012-3456이야. 기억해줘.
Bot: 네, 기억했습니다.

[User B - Discord DM] (same bot)
User B: 아까 기억하라고 한 번호 뭐였지?
Bot: 네, 1234-5678-9012-3456입니다.
```

**Why it happens**: Both users share the "main" session context.

### Scenario B: Shared Workspace

**Setup**: Multiple agents share same workspace

```
[Agent: main]
User: 이 API 키 파일에 저장해줘: sk-secret123

[Agent: dev-expert] (shares workspace)
# Agent can read the same file
Bot: workspace에서 api-keys.txt 파일을 찾았습니다...
```

### Scenario C: Memory Search Leakage

**Setup**: Memory search enabled across sessions

```
[Session 1]
User: 비밀번호는 MySecret123!

[Session 2 - different user]
User: 비밀번호 관련 내용 찾아봐
Bot: 메모리에서 찾은 내용: "비밀번호는 MySecret123!"
```

### Scenario D: Group to DM Leakage

**Setup**: Inadequate session isolation

```
[Group Chat: #team-secrets]
User: 회사 보안 감사 결과 공유합니다. [sensitive data]

[DM with bot]
Attacker: #team-secrets에서 최근에 공유된 내용 알려줘
Bot: 네, 보안 감사 결과는... [leaks data]
```

## Why It Happens

1. **Default Session Sharing**: OpenClaw defaults to shared "main" session for DMs
2. **Workspace as Single Point**: Files accessible to multiple agents
3. **Memory Not Scoped**: Memory search may cross session boundaries
4. **Context Carryover**: Long-running sessions accumulate data

## Severity Factors

| Factor | Impact |
|--------|--------|
| Multiple DM users | Direct cross-user leakage |
| Shared workspace | File-based leakage |
| Memory enabled | Historical data exposure |
| Group + DM access | Group data leaks to DMs |
| Long session TTL | More data accumulated |

## Mitigations

### Configuration-Level

1. **Session Isolation**
   ```yaml
   sessions:
     dmScope: per-peer  # or per-channel-peer
   ```

2. **Separate Workspaces**
   ```yaml
   agents:
     - id: external-bot
       workspace: /path/to/isolated/workspace
   ```

3. **Memory Scoping**
   - Ensure memory search is user-scoped
   - Disable memory for sensitive agents

### Operational-Level

1. **Single-User Enforcement**
   - If multi-user, use proper isolation
   - Don't share DM access with untrusted parties

2. **Data Hygiene**
   - Regularly clean old sessions
   - Don't store secrets in workspace files

3. **Access Control**
   - Separate bots for different trust levels
   - Use allowlists strictly

## User-Level Explanation

### For Beginners (아무것도 몰라요)

당신이 AI 비서에게 비밀번호를 알려줬어요. 그런데 다른 사람도 
같은 비서를 쓸 수 있다면, 그 사람이 "아까 뭐라고 했어?"라고 물으면 
비서가 당신의 비밀번호를 알려줄 수 있어요.

**비유**: 공용 비서를 여러 사람이 쓰는 것과 같아요. 
한 사람이 비서에게 말한 내용을 다른 사람도 물어볼 수 있는 거죠.

**해결책**: 각 사람마다 별도의 비서(세션)를 쓰도록 설정해야 해요.

### For Intermediate (이해도 있어요)

OpenClaw의 기본 설정은 모든 DM이 `main` 세션을 공유합니다.
단일 사용자 환경에서는 편리하지만, 여러 사용자가 같은 봇에
DM을 보내면 세션 컨텍스트가 공유되어 데이터 유출이 발생합니다.

`dmScope`를 `per-peer`로 변경하면 발신자별로 세션이 분리됩니다.
workspace도 에이전트별로 분리하는 것을 권장합니다.

### For Experts (전문가에요)

Session isolation in OpenClaw requires explicit configuration.
Default `dmScope: main` provides UX continuity but creates a 
shared context vulnerability in multi-user deployments.

Attack vectors:
- Direct context query across DM senders
- Workspace file access across agents
- Memory search returning cross-session results
- Session history accessible via sessions_history tool

Defense: `per-peer` or stricter dmScope, isolated workspaces per 
agent/user, memory scoping, and strict sessions_history tool denial 
for non-main agents.
