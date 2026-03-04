# 📇 Bizcard — Business Card Scanner for OpenClaw

Telegram에서 명함 사진을 보내면 자동으로 OCR → 연락처 저장까지 처리하는 OpenClaw 스킬.

## Features

- **자동 명함 감지** — 이미지 분석으로 명함 자동 인식
- **OCR 추출** — Google Gemini 3 Flash (imageModel)로 이름, 회사, 직함, 전화, 이메일, 주소 추출
- **이미지 보정** — Nano Banana Pro로 배경 제거 + 정면 보정 + 1:1 정사각형 (모든 명함에 자동 적용)
- **한국식 연락처** — familyName 비움 + givenName에 풀네임 (한국 비즈니스 관행)
- **이름 포맷** — #해시(카카오 방지), 직함, 회사명 자동 추가
- **전화번호 정규화** — 한국 번호 → +82 국제 형식 자동 변환
- **복수 거점 분리** — 본사/공장/영업부 별 전화번호+주소 그룹핑
- **중복 감지** — 이름 + 전화번호 2필드 자동 매칭
- **Korean Reading** — 외국 명함의 이름/회사를 한국어 독음 (phoneticName 필드, 검색 가능)
- **설정 토글** — `/bizcard config`로 번호 입력만으로 on/off

## Prerequisites

| 항목 | 필수 | 설치 |
|------|:----:|------|
| OpenClaw | **필수** | [docs.openclaw.ai/install](https://docs.openclaw.ai/install) |
| Telegram Bot | **필수** | @BotFather에서 생성 |
| Maton API Key | **필수** | [maton.ai/settings](https://maton.ai/settings) |
| Google Contacts 연결 | **필수** | Maton OAuth (`google-contacts`) |
| Nano Banana Pro API Key | **필수** | [aistudio.google.com](https://aistudio.google.com/app/apikey) |

## Quick Start

### 1. 스킬 설치

`skills/bizcard/` 폴더를 OpenClaw 워크스페이스에 복사.

### 2. Maton API Key 설정

```bash
# 환경변수 등록
echo 'export MATON_API_KEY="your-key-here"' >> ~/.zshrc
source ~/.zshrc

# LaunchAgent에도 적용
launchctl setenv MATON_API_KEY "your-key-here"
```

### 3. Google Contacts 연결

Maton에서 `google-contacts` OAuth 연결을 활성화한다.
[maton.ai](https://maton.ai) → Connections → Google Contacts → Connect

### 4. ImageMagick 설치 (Perspective Transform용)

```bash
brew install imagemagick
```

### 5. 전용 Telegram Bot 설정 (권장)

메인 봇과 분리해서 명함 전용 봇을 운영하는 것을 권장한다.

```
1. @BotFather에서 새 봇 생성
2. openclaw.json에 별도 account로 등록:
```

```json
{
  "channels": {
    "telegram": {
      "accounts": {
        "default": { "botToken": "메인봇토큰", "dmPolicy": "pairing" },
        "bizcard": { "botToken": "명함봇토큰", "dmPolicy": "pairing" }
      }
    }
  },
  "agents": {
    "list": [
      { "id": "main" },
      { "id": "bizcard", "workspace": "~/openclaw/workspace-bizcard" }
    ]
  },
  "bindings": [
    { "agentId": "main", "match": { "channel": "telegram", "accountId": "default" } },
    { "agentId": "bizcard", "match": { "channel": "telegram", "accountId": "bizcard" } }
  ]
}
```

### 6. Bizcard 전용 워크스페이스

`workspace-bizcard/` 폴더에 SOUL.md, AGENTS.md를 생성한다.
에이전트가 자신이 bizcard 전용임을 인식하고, `sessions_spawn` 없이 직접 처리하도록 지시.

핵심: SOUL.md에 **7단계 필수 체크리스트**를 명시하여 에이전트가 파이프라인을 건너뛰지 않도록 강제.

### 7. 게이트웨이 재시작

```bash
openclaw gateway restart
```

### 8. 페어링

Telegram에서 봇에게 아무 메시지나 보내면 pairing code가 나온다.

```bash
openclaw pairing approve telegram <CODE>
```

## Configuration

`/bizcard config`를 Telegram에 입력하면 설정 화면이 나온다.

```
📇 Bizcard Settings

1. Hashtag           : on 🟢 — #이름 (카카오 자동추가 방지)
2. Append title      : on 🟢 — 이름 뒤에 직함
3. Append company    : off ❌ — 이름 뒤에 (회사명)
4. Card as photo     : on 🟢 — 명함→연락처 사진
5. Korean reading    : on 🟢 — 외국 이름 한국어 독음
6. Korean style name : on 🟢 — 성 비움, 이름에 풀네임

번호만 입력하면 on↔off 전환.
00 = Reset ♺ / 38 = All on 🟢 / 49 = All off ❌
```

### Recommended Settings

| 사용 환경 | 권장 설정 |
|-----------|-----------|
| 한국 비즈니스 | 1,2,4,5,6 on / 3 off (기본값) |
| 전부 켜기 | `38` (All on) |
| 해외 명함 위주 | 1,2,4 on / 5,6 off |

## Architecture

### 전용 Telegram 봇 + 서브 에이전트 (권장)

메인 봇과 명함 봇을 분리하는 것을 **강력히 권장**한다.

**장점:**
- 메인 대화를 어지럽히지 않음
- 명함 처리가 독립적으로 진행
- PII(개인정보)가 메인 세션에 노출되지 않음

```
메인 봇 (@main_bot) → 일반 대화
명함 봇 (@bizcard_bot) → 명함 전용 (별도 에이전트)
```

설정 방법은 Quick Start의 Step 5를 참조.

### OCR + 이미지 보정 파이프라인

```
명함 사진 → Gemini 3 Flash OCR (원본으로 텍스트 추출)
→ 필드 파싱 → Name 포맷 적용 → 중복 감지
→ 사용자 확인 → Nano Banana Pro (배경 제거 + 정면 보정 + 1:1)
→ Google Contacts 저장 + 보정된 사진 업로드
```

**핵심:** OCR은 원본 이미지로, 이미지 보정은 사진 저장용으로만 사용. 보정 시 텍스트 훼손을 방지.

### Korean Name Convention

한국에서는 성과 이름을 분리하지 않는다. "홍길동 대표", "김과장" 처럼 풀네임이 하나의 단위.

- `familyName` → 비움
- `givenName` → 풀네임 (홍길동)
- `displayName` → 포맷 적용 (#홍길동 대표)

외국 명함은 first/last name 분리가 기본.

### Perspective Transform

카메라로 찍은 기울어진 명함을 정면 직사각형으로 보정한다.
ImageMagick의 `-distort Perspective`를 사용하며, imageModel이 4꼭지점 좌표를 자동 추출.

## Limitations (v0.1)

- 양면 명함 미지원 (앞면만 처리)
- 한 장에 여러 명함 미지원
- OCR 정확도는 Gemini 3 Flash에 의존
- 이미지 보정 품질은 Nano Banana Pro에 의존
- config 변경 시 에이전트가 파일을 실제 수정하지 않는 경우가 있음 (v0.2에서 개선)

## File Structure

```
skills/bizcard/
├── SKILL.md              # 스킬 정의 (에이전트 지시문)
├── config.json           # 사용자 설정 (7개 on/off)
├── _meta.json            # ClawHub 메타데이터
├── LICENSE               # CC BY-NC 4.0
├── README.md             # 이 파일
└── references/
    └── people-api-fields.md  # Google People API 필드 레퍼런스
```

## License

CC BY-NC 4.0 — 수정/재배포 가능, 상업적 사용 금지.
