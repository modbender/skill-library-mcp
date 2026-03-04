# Decisions Log

아키텍처/정책 결정은 아래 형식으로 누적합니다.

## Decision Table

| ID | Date | Status | Decision | Why | Impact |
|---|---|---|---|---|---|
| D-001 | 2026-02-18 | Accepted | MVP 범위를 5개 유스케이스로 잠금 | 구현 복잡도와 검증 범위 통제 | 초기 릴리즈 속도 향상 |
| D-002 | 2026-02-18 | Accepted | 태그 기능은 MVP에서 제외 | TickTick 공식 OpenAPI에서 tag endpoint 불명확 | 문서 기반 구현 안정성 증가 |
| D-003 | 2026-02-18 | Accepted | idempotency는 클라이언트 측 dedupe로 처리 | 공식 idempotency key 계약 미문서 | 중복 생성 리스크 감소 |
| D-004 | 2026-02-18 | Accepted | 429/5xx에 지수 백오프 재시도 적용 | rate limit/일시 장애 가능성 대응 | 안정성 향상 |
| D-005 | 2026-02-18 | Accepted | 빈 에러 응답(No Content) 허용 설계 | 에러 바디 표준 스키마 미확정 | 오류 처리 회복력 향상 |

## 변경 규칙
- 기존 결정을 수정할 때는 새 행을 추가하고 이전 ID를 참조
- `Status`는 `Proposed`, `Accepted`, `Superseded`, `Rejected` 중 하나 사용
- 구현 시작 전, `Accepted`가 필요한 항목은 모두 채워져야 함
