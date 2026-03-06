# Docs 운영 가이드

이 폴더는 세션이 바뀌어도 작업을 이어가기 위한 단일 기록 소스입니다.

## 시작할 때 읽는 순서
1. `docs/current-status.md`
2. `docs/decisions.md`
3. `docs/progress-log.md`
4. `docs/next-session.md`

## 기록 규칙
- 중요한 결정은 항상 `docs/decisions.md`에 먼저 기록
- 실제 진행 내역은 시간순으로 `docs/progress-log.md`에 추가(append-only)
- 현재 상태(범위/리스크/다음 작업)는 `docs/current-status.md`를 최신으로 유지
- 세션 종료 전 `docs/next-session.md`를 다음 담당자가 바로 실행할 수 있게 갱신

## 최소 업데이트 체크리스트
- [ ] 오늘 변경/검토한 내용 1줄 요약 기록
- [ ] 새 결정 또는 결정 변경 반영
- [ ] 블로커/리스크 상태 갱신
- [ ] 다음 세션 첫 3개 액션 확정

## 파일 역할
- `docs/current-status.md`: 현재 프로젝트 스냅샷(단일 진실 원천)
- `docs/decisions.md`: 아키텍처/정책 의사결정 로그
- `docs/progress-log.md`: 작업 히스토리 로그
- `docs/next-session.md`: 다음 세션 실행 브리프
