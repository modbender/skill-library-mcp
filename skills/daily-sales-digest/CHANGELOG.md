# Changelog

## v1.0.0 (2026-02-18)

### 초기 릴리스

#### 기능
- ✅ 매출 데이터 수집 스크립트 (`collect.js`)
  - 네이버 스마트스토어 API (mock)
  - 쿠팡 Wing API (mock)
  - 배민셀러 API (mock)
  - POS 시스템 (mock)
- ✅ 일일 요약 리포트 (`digest.js`)
  - 텍스트/JSON 형식 출력
  - 전일/전주/전월 대비 비교 분석
  - 채널별 매출 분석
- ✅ 이상 탐지 알림 (`alert.js`)
  - 임계값 기반 급증/급감 감지
  - Discord/이메일 알림
- ✅ 주간/월간 리포트
- ✅ OpenClaw cron 연동

#### 문서
- ✅ SKILL.md - 스킬 메타데이터 및 사용법
- ✅ README.md - 빠른 시작 가이드
- ✅ EXAMPLES.md - 사용 예시 모음
- ✅ API_INTEGRATION.md - API 연동 가이드
- ✅ CHANGELOG.md - 변경 이력

#### 설정
- ✅ config.template.json - 설정 템플릿
- ✅ .gitignore - 민감 정보 보호

#### 테스트
- ✅ test.sh - 자동 테스트 스크립트
- ✅ Mock 데이터로 전체 플로우 검증

### TODO (향후 구현)

#### v1.1.0
- [ ] 네이버 스마트스토어 실제 API 연동
- [ ] 쿠팡 Wing 실제 API 연동
- [ ] 배민셀러 실제 API 연동
- [ ] Markdown 형식 리포트 포맷

#### v1.2.0
- [ ] 카카오톡 알림 연동
- [ ] 상품별 매출 분석
- [ ] 시간대별 매출 패턴 분석
- [ ] Canvas를 활용한 대시보드 UI

#### v1.3.0
- [ ] AI 기반 매출 예측
- [ ] Google Sheets 자동 업데이트
- [ ] Slack 연동
- [ ] 커스텀 리포트 템플릿

#### v2.0.0
- [ ] 웹 대시보드 (실시간)
- [ ] 모바일 앱 연동
- [ ] 다중 고객사 지원
- [ ] 역할 기반 접근 제어 (RBAC)

### 알려진 이슈
- 현재 mock 데이터만 지원 (실제 API 미연동)
- Markdown 리포트 포맷 미구현
- 주간/월간 리포트에 상세 분석 부족

### 기여자
- [@subagent] - 초기 개발
