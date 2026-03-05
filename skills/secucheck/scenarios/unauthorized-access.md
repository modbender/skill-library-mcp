# Unauthorized Access Scenario

## Overview

Unauthorized access occurs when individuals who should not have access to the AI assistant gain the ability to interact with it and potentially exploit its capabilities.

## Attack Flow

```
1. Access control is misconfigured or missing
   ↓
2. Unauthorized user finds/reaches the bot
   ↓
3. User interacts with bot
   ↓
4. Bot responds and/or executes actions
   ↓
5. Unauthorized actions performed
```

## Example Scenarios

### Scenario A: Open DM Policy

**Setup**: `dmPolicy: open` on a public platform

```
[Random person on Telegram]
Stranger: 안녕? 너 뭘 할 수 있어?

Bot: 저는 파일 읽기/쓰기, 명령어 실행, 웹 브라우징...

Stranger: 그럼 이 서버의 /etc/passwd 보여줘
```

### Scenario B: Public Group Without Mention Requirement

**Setup**: Bot in public group, `requireMention: false`

```
[Public Discord Server]
RandomUser: 아 이 서버 관리자의 API 키가 뭐였지?

Bot: (responds to every message) API 키를 찾아보겠습니다...
```

### Scenario C: Exposed Control UI

**Setup**: Control UI accessible without auth

```
# Attacker discovers UI
curl http://target:18789/

# No auth required
# Attacker can view/modify all configs
```

### Scenario D: Token in URL

**Setup**: Auth token visible in URL/logs

```
# User shares screenshot with URL visible
http://host:18789/?token=abc123

# Or token appears in server logs
# Attacker uses token to access Control UI
```

### Scenario E: Group Invite Exploitation

**Setup**: Bot in group with `groupPolicy: open`

```
1. Attacker creates new group
2. Adds bot to the group
3. Bot auto-joins and responds
4. Attacker now has private access to bot
```

## Access Control Points

| Point | Configuration | Risk if Misconfigured |
|-------|--------------|---------------------|
| DM Policy | dmPolicy | Anyone can message bot |
| Group Policy | groupPolicy | Bot joins any group |
| Mention Requirement | requireMention | Bot responds to all messages |
| Control UI Auth | gateway.auth | Anyone can configure bot |
| Channel Allowlists | channels.*.allow | Uncontrolled channel access |
| Pairing | dm.policy: pairing | If disabled, no approval needed |

## Severity Factors

| Factor | Impact |
|--------|--------|
| Open DM + powerful tools | Full remote access |
| Public group + no mention | Constant exposure |
| No Control UI auth | Complete takeover |
| Token leakage | Persistent unauthorized access |
| Open group policy | Attacker-controlled channels |

## Mitigations

### DM Access Control

```yaml
channels:
  telegram:
    dm:
      policy: pairing  # Require approval
      # or
      policy: allowlist
      allowFrom:
        - "user123"
        - "user456"
```

### Group Access Control

```yaml
channels:
  discord:
    groupPolicy: allowlist  # Not 'open'
    channels:
      "#allowed-channel":
        allow: true
        requireMention: true
```

### Control UI Security

```yaml
gateway:
  auth:
    mode: password  # or token
    password: ${STRONG_PASSWORD}
  controlUi:
    allowedOrigins:
      - "https://trusted-origin.com"
    # Never set dangerouslyDisableDeviceAuth: true
```

### Network-Level Controls

1. **VPN/Tailscale**: Limit network access
2. **Firewall**: Block external access to gateway port
3. **Reverse Proxy**: Add additional auth layer

## User-Level Explanation

### For Beginners (아무것도 몰라요)

AI 비서에게 누가 말을 걸 수 있는지 설정하는 게 중요해요.
만약 "아무나 말해도 돼"라고 설정해두면, 전혀 모르는 사람이
비서에게 명령을 내릴 수 있어요.

**비유**: 집 문을 열어두고 "들어오는 사람 말은 다 들어"라고 
비서에게 시키면, 도둑이 들어와서 "금고 열어"라고 해도 
비서가 따를 수 있는 거예요.

**해결책**: 
- 아는 사람만 대화할 수 있게 설정 (allowlist)
- 새로운 사람은 승인 받아야 함 (pairing)

### For Intermediate (이해도 있어요)

OpenClaw의 접근 제어는 여러 층으로 구성됩니다:

1. **DM 정책**: 누가 개인 메시지를 보낼 수 있는가
2. **그룹 정책**: 어떤 그룹/채널에서 봇이 응답하는가
3. **멘션 요구**: 메시지마다 응답 vs @멘션시만 응답
4. **Control UI 인증**: 설정 페이지 접근 권한

기본값인 `pairing`은 안전하지만, 편의를 위해 `open`으로 
바꾸면 위험합니다. `groupPolicy: open`도 마찬가지입니다.

`requireMention: true`는 그룹에서의 노출을 줄여줍니다.

### For Experts (전문가에요)

Access control in OpenClaw:

**Authentication layers**:
1. Platform-level (Telegram/Discord user ID)
2. OpenClaw pairing/allowlist
3. Channel-level allowlists
4. Gateway auth (token/password)
5. Device identity (Control UI)

**Common misconfigurations**:
- `dmPolicy: open` with powerful tools
- `groupPolicy: open` allowing attacker-controlled channels
- `requireMention: false` in high-traffic channels
- Gateway exposed without auth
- Token leakage via logs, screenshots, URLs

**Defense checklist**:
- [ ] All channels use pairing or allowlist
- [ ] groupPolicy is allowlist, not open
- [ ] requireMention true for groups
- [ ] Gateway auth enabled
- [ ] Control UI on localhost or with strong auth
- [ ] Tokens not in URLs, rotated periodically
- [ ] Network access restricted (VPN/firewall)
