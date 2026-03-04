# 🔒 OpenClaw 보안 가이드

## 1. API 키 관리 (최우선)

### ❌ 절대 하면 안 되는 것
- SOUL.md, USER.md, MEMORY.md에 API 키 적기
- 에이전트한테 "이 키 기억해" 하기
- 파일에 키를 평문으로 저장하기

### ✅ 올바른 방법
```bash
# OpenClaw 설정으로 관리
openclaw configure --section web      # Brave API 키
openclaw configure --section models   # AI 모델 API 키

# 환경변수로 관리
export OPENAI_API_KEY=sk-xxxxx
export ANTHROPIC_API_KEY=sk-ant-xxxxx
```

### .gitignore 설정
```
.env
*.env
secrets/
```

---

## 2. 채널 보안 (메신저)

### 텔레그램
- **allowlist 필수**: 본인 전화번호만 등록
- 모르는 사람이 봇에 메시지 보내면 자동 무시
- 그룹챗 추가 시 주의 (에이전트가 모든 메시지를 읽음)

### 확인 방법
```bash
openclaw configure --section channels
# → allowlist에 본인 번호 확인
```

---

## 3. 외부 행동 제어

에이전트가 혼자 판단해서 하면 위험한 것들:
- 이메일 발송
- SNS 게시
- 파일 삭제
- 결제/구매

### 설정
```bash
openclaw configure --section security
```
- 외부 발송: 승인 모드 (에이전트가 먼저 물어봄)
- 파일 삭제: `trash` 사용 강제 (`rm` 금지)

---

## 4. Gateway 보안

### 토큰 관리
- gateway 토큰 = 에이전트 접근 열쇠
- **절대 외부 공유 금지**
- 카톡/메신저로 보내지 말 것

### 네트워크
- 공용 WiFi (카페, 공항)에서 대시보드 접속 주의
- 가능하면 VPN 사용
- Tailscale 설정하면 안전한 원격 접속 가능

---

## 5. 데이터 보안

### 에이전트가 아는 것
- SOUL.md, USER.md → 당신의 기본 정보
- memory/ → 대화 기록, 학습 자료
- 연결된 서비스 (이메일, 캘린더 등)

### 관리 원칙
- 민감 정보 (주민번호, 카드번호 등) 에이전트에게 알려주지 않기
- `memory/` 폴더 정기 백업 (월 1회 권장)
- 다른 사람과 공유 시 민감정보 마스킹

---

## 6. 정기 보안 점검

### 월 1회 체크리스트
```
□ openclaw health 실행
□ 설치된 스킬 목록 확인 (모르는 스킬 없는지)
□ allowlist 확인 (허용 번호 맞는지)
□ API 키 유효성 확인
□ memory/ 폴더 백업
□ 크론잡 목록 확인 (불필요한 것 삭제)
```

### 명령어
```bash
openclaw health         # 전체 상태 점검
openclaw status         # 현재 상태
openclaw doctor         # 문제 진단
```

---

## 7. 비상 시 대처

### 에이전트가 이상한 행동을 하면
1. `openclaw gateway stop` → 즉시 중지
2. 로그 확인: `openclaw logs`
3. 설정 확인: `openclaw configure`
4. 필요시 리셋: `openclaw reset` (주의: 설정 초기화)

### API 키가 유출된 것 같으면
1. 해당 서비스에서 즉시 키 폐기 (Revoke)
2. 새 키 발급
3. `openclaw configure`로 새 키 등록
