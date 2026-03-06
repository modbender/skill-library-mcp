# 설치 및 초기 설정 가이드

## 1. 필수 요구사항

- Node.js 18 이상
- OpenClaw gateway 실행 중
- Discord/이메일 알림을 위한 채널 설정

## 2. 설치 단계

### 2.1 디렉토리 확인

스킬이 이미 설치되어 있습니다:

```bash
ls -la /Users/mupeng/.openclaw/workspace/skills/daily-sales-digest/
```

### 2.2 설정 파일 생성

```bash
# 설정 디렉토리 생성
mkdir -p ~/.openclaw/workspace/config

# 템플릿 복사
cp /Users/mupeng/.openclaw/workspace/skills/daily-sales-digest/config.template.json \
   ~/.openclaw/workspace/config/daily-sales-digest.json
```

### 2.3 설정 파일 편집

```bash
# 에디터로 설정 파일 열기
vim ~/.openclaw/workspace/config/daily-sales-digest.json

# 또는
code ~/.openclaw/workspace/config/daily-sales-digest.json
```

최소한 다음 항목을 설정하세요:

1. **데이터 소스 활성화**:
   ```json
   "naver": {
     "enabled": true,
     "clientId": "실제_클라이언트_ID",
     "clientSecret": "실제_시크릿"
   }
   ```

2. **Discord 채널 ID**:
   ```json
   "discord": {
     "enabled": true,
     "channelId": "1468204132920725535"
   }
   ```

### 2.4 데이터 디렉토리 생성

```bash
mkdir -p ~/.openclaw/workspace/data/sales
```

## 3. 테스트 실행

```bash
cd /Users/mupeng/.openclaw/workspace/skills/daily-sales-digest

# 전체 테스트 스크립트 실행
./test.sh
```

또는 개별 테스트:

```bash
# 데이터 수집
node scripts/collect.js --date yesterday

# 요약 출력
node scripts/digest.js --date yesterday

# 이상 탐지
node scripts/alert.js --date yesterday
```

## 4. cron 스케줄 설정

### 4.1 매일 아침 8시 요약 전송

```bash
openclaw cron add \
  --name "daily-sales-digest:daily" \
  --schedule "0 8 * * *" \
  --command "node /Users/mupeng/.openclaw/workspace/skills/daily-sales-digest/scripts/digest.js --date yesterday --deliver discord"
```

### 4.2 매일 자정 데이터 수집

```bash
openclaw cron add \
  --name "daily-sales-digest:collect" \
  --schedule "0 0 * * *" \
  --command "node /Users/mupeng/.openclaw/workspace/skills/daily-sales-digest/scripts/collect.js --date today"
```

### 4.3 매일 저녁 9시 이상 탐지

```bash
openclaw cron add \
  --name "daily-sales-digest:anomaly" \
  --schedule "0 21 * * *" \
  --command "node /Users/mupeng/.openclaw/workspace/skills/daily-sales-digest/scripts/alert.js --date today --deliver discord"
```

### 4.4 주간 리포트 (매주 월요일 오전 9시)

```bash
openclaw cron add \
  --name "daily-sales-digest:weekly" \
  --schedule "0 9 * * 1" \
  --command "node /Users/mupeng/.openclaw/workspace/skills/daily-sales-digest/scripts/digest.js --period week --deliver discord"
```

### 4.5 월간 리포트 (매월 1일 오전 9시)

```bash
openclaw cron add \
  --name "daily-sales-digest:monthly" \
  --schedule "0 9 1 * *" \
  --command "node /Users/mupeng/.openclaw/workspace/skills/daily-sales-digest/scripts/digest.js --period month --deliver email"
```

## 5. cron 작업 확인

```bash
# 등록된 작업 목록
openclaw cron list | grep daily-sales

# 특정 작업 실행 이력
openclaw cron runs daily-sales-digest:daily
```

## 6. 실제 API 연동 (선택)

현재는 mock 데이터를 사용합니다. 실제 API를 연동하려면:

1. API_INTEGRATION.md 문서 참고
2. scripts/collect.js의 TODO 섹션 구현
3. 필요한 npm 패키지 설치:
   ```bash
   cd /Users/mupeng/.openclaw/workspace/skills/daily-sales-digest
   npm init -y
   npm install axios
   ```

## 7. 트러블슈팅

### 설정 파일이 없다는 에러

```bash
# 설정 파일 존재 확인
ls ~/.openclaw/workspace/config/daily-sales-digest.json

# 없으면 다시 복사
cp /Users/mupeng/.openclaw/workspace/skills/daily-sales-digest/config.template.json \
   ~/.openclaw/workspace/config/daily-sales-digest.json
```

### 데이터가 수집되지 않음

```bash
# 설정 파일에서 enabled 확인
cat ~/.openclaw/workspace/config/daily-sales-digest.json | grep enabled

# 모든 소스가 false면 최소 하나는 true로 변경
```

### Discord 전송 실패

```bash
# OpenClaw message 스킬 확인
openclaw message send --help

# 채널 ID 확인 (형님 DM: 1468204132920725535)
```

### cron 작업이 실행되지 않음

```bash
# gateway 상태 확인
openclaw gateway status

# 재시작 필요시
openclaw gateway restart

# cron 로그 확인
openclaw cron runs daily-sales-digest:daily
```

## 8. 제거 방법

스킬을 제거하려면:

```bash
# cron 작업 삭제
openclaw cron list | grep daily-sales-digest | awk '{print $1}' | xargs -I {} openclaw cron delete {}

# 데이터 백업 (선택)
tar -czf ~/sales-data-backup.tar.gz ~/.openclaw/workspace/data/sales/

# 스킬 디렉토리 삭제
rm -rf /Users/mupeng/.openclaw/workspace/skills/daily-sales-digest

# 설정 파일 삭제 (선택)
rm ~/.openclaw/workspace/config/daily-sales-digest.json

# 데이터 삭제 (선택)
rm -rf ~/.openclaw/workspace/data/sales/
```

## 9. 백업 권장사항

주기적으로 데이터를 백업하세요:

```bash
# 매월 1일 백업 cron 추가
openclaw cron add \
  --name "daily-sales-digest:backup" \
  --schedule "0 3 1 * *" \
  --command "tar -czf ~/backups/sales-$(date +%Y%m).tar.gz ~/.openclaw/workspace/data/sales/"
```

## 10. 지원

문제가 발생하면:

1. EXAMPLES.md의 트러블슈팅 섹션 확인
2. 로그 파일 확인: `openclaw cron runs <job-id>`
3. GitHub Issues에 문의
