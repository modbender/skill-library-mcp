# Korail Manager 스킬 (한국어 안내서)

KTX/SRT 예매 자동화 스킬입니다. 열차를 검색하고, 표를 예매하며, 빈자리가 날 때까지 자동으로 감시하는 기능을 제공합니다.

## ⚠️ 중요: 최초 설정

가장 간편한 설정을 위해, 포함된 자동 설정 스크립트를 실행하십시오. 이 스크립트가 가상 환경 생성과 모든 의존성 설치를 자동으로 처리해 줍니다.

```bash
bash scripts/setup.sh
```

이 스크립트는 스킬을 설치하거나 업데이트한 후 **단 한 번만** 실행하면 됩니다.

<details>
<summary><strong>수동 설정 절차</strong></summary>

만약 수동으로 환경을 설정하고 싶다면 아래 절차를 따르십시오.

**1. 가상 환경 생성:**
작업 공간의 루트(`~/.../workspace`)에서, 아래 명령어를 실행하여 스킬 폴더 내부에 가상 환경을 생성하십시오.
```bash
python3 -m venv skills/korail-manager/venv
```

**2. 의존성 설치:**
`requirements.txt`에 명시된 필요 패키지들을 가상 환경 내부에 설치합니다.
```bash
skills/korail-manager/venv/bin/pip install -r skills/korail-manager/requirements.txt
```
</details>

## 사용법

모든 스크립트는 **반드시 위에서 생성한 가상 환경의 파이썬으로 실행**해야 합니다.

### KTX

#### 열차 검색 (`search.py`)
```bash
venv/bin/python scripts/search.py --dep "부산" --arr "서울" --date "20260210"
```

#### 좌석 감시 및 자동 예매 (`watch.py`)

이 스크립트는 백그라운드에서 실행되며, `interval` 초마다 빈자리를 확인하고, 표를 발견하면 자동으로 예매를 시도합니다. 성공 시 텔레그램/슬랙으로 알림을 보냅니다.

```bash
venv/bin/python scripts/watch.py --dep "부산" --arr "서울" --date "20260210" --start-time 15 --end-time 17 --interval 300
```

#### 예약 취소 (`cancel.py`)
```bash
# 전체 예약 취소
venv/bin/python scripts/cancel.py

# 특정 날짜 예약만 취소
venv/bin/python scripts/cancel.py --date "20260210"
```

### SRT

#### 열차 검색 (`srt_search.py`)
```bash
venv/bin/python scripts/srt_search.py --dep "수서" --arr "대전" --date "20260210"
```

#### 좌석 감시 및 자동 예매 (`srt_watch.py`)

```bash
venv/bin/python scripts/srt_watch.py --dep "수서" --arr "대전" --date "20260210" --start-time 14 --end-time 18 --interval 300
```

#### 예약 취소 (`cancel_srt.py`)
```bash
# 전체 예약 취소
venv/bin/python scripts/cancel_srt.py

# 특정 날짜 예약만 취소
venv/bin/python scripts/cancel_srt.py --date "20260210"
```

### 공통 인수

| 인수 | 설명 | 예시 |
|------|------|------|
| `--dep` | 출발역 | `"서울"`, `"수서"`, `"오송"` |
| `--arr` | 도착역 | `"부산"`, `"대전"` |
| `--date` | 날짜 (YYYYMMDD) | `"20260210"` |
| `--time` | 시간 (HHMMSS, 검색 전용) | `"140000"` |
| `--start-time` | 감시 시작 시간 (0-23) | `15` |
| `--end-time` | 감시 종료 시간 (0-23) | `17` |
| `--interval` | 확인 주기, 초 (기본값: 300초 = 5분) | `300` |

## 환경 변수 설정
이 스킬은 로그인 및 알림을 위해 민감한 정보를 필요로 합니다.
**올바르게 작동하려면 반드시 이 정보들을 설정해야 합니다.**

가장 권장되는 방식은, 스킬의 루트 폴더에 `.env` 파일을 생성하여 정보를 관리하는 것입니다.

1.  견본 파일을 복사합니다: `cp .env.example .env`
2.  새로 생성된 `.env` 파일을 열어 실제 정보를 입력합니다.

```dotenv
# Korail (KTX) Login
KORAIL_ID="YOUR_KORAIL_ID"
KORAIL_PW="YOUR_KORAIL_PASSWORD"

# SRT Login
SRT_ID="YOUR_SRT_ID"
SRT_PW="YOUR_SRT_PASSWORD"

# Telegram Bot
TELEGRAM_BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID="YOUR_TELEGRAM_CHAT_ID"

# Slack Webhook (선택 사항)
SLACK_WEBHOOK_URL="YOUR_SLACK_WEBHOOK_URL"
```

⚠️ **경고:** `.env` 파일은 `.gitignore`에 포함되어 Git 저장소에 올라가지 않습니다. 하지만 이 파일은 매우 민감한 자격 증명을 담고 있으니, **절대로 외부에 공개하거나 버전 관리에 포함시키지 마십시오.**

스크립트는 실행 시 자동으로 이 파일의 변수들을 불러옵니다.

<details>
<summary><strong>텔레그램 토큰과 Chat ID는 어떻게 찾나요?</strong></summary>

**1. 봇 토큰(Bot Token) 찾기:**
   - 텔레그램에서 `@BotFather` 봇을 검색합니다.
   - `/mybots` 명령을 보냅니다.
   - 목록에서 당신의 봇을 선택합니다.
   - **API Token** 버튼을 클릭하면 토큰을 볼 수 있습니다.

**2. Chat ID 찾기:**
   - 텔레그램에서 `@userinfobot`을 검색합니다.
   - 봇과의 대화를 시작합니다.
   - 봇이 즉시 당신의 사용자 정보를 회신하며, 여기에 포함된 **Id**가 바로 당신의 Chat ID입니다.

</details>

<details>
<summary><strong>슬랙 웹훅 URL은 어떻게 만드나요?</strong></summary>

1.  **Slack 앱 페이지로 이동:** `https://api.slack.com/apps`
2.  **앱 생성 또는 선택:** "Create New App"을 클릭하거나, 알림을 받고자 하는 기존 앱을 선택합니다.
    *   "From scratch"를 선택하고, 앱 이름(예: "코레일 알리미")을 정한 뒤, 워크스페이스를 선택합니다.
3.  **Incoming Webhooks 활성화:** 왼쪽 사이드바의 "Incoming Webhooks" 메뉴를 클릭하고, 기능을 **On**으로 켭니다.
4.  **워크스페이스에 웹훅 추가:** 페이지 하단의 "Add New Webhook to Workspace" 버튼을 클릭합니다.
5.  **채널 선택:** 알림을 받을 채널을 선택하고 "Allow"를 클릭합니다.
6.  **URL 복사:** 목록에 `https://hooks.slack.com/...`로 시작하는 새 웹훅 URL이 나타납니다. 이 주소를 복사합니다.
7.  **환경 변수 설정:** 복사한 주소를 `SLACK_WEBHOOK_URL` 환경 변수 값으로 사용합니다.

</details>

## 보안 및 프라이버시
이 스킬은 아래의 목적으로 외부 네트워크 호출을 사용합니다:
1. **코레일 (letskorail.com):** KTX 열차 조회 및 예매
2. **SRT (srail.or.kr):** SRT 열차 조회 및 예매
3. **텔레그램 API:** 예매 알림 발송 (설정 시)
4. **슬랙 웹훅:** 예매 알림 발송 (설정 시)

자격 증명 정보는 오직 환경 변수를 통해서만 읽어오며, 다른 곳에 저장되거나 전송되지 않습니다.
