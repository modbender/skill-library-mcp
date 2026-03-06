# Next Session Brief

다음 세션 담당자가 이 문서 하나만 읽고 바로 시작할 수 있도록 유지합니다.

## 0) 먼저 읽을 문서
1. `docs/current-status.md`
2. `docs/decisions.md`
3. `docs/progress-log.md`

## 1) 세션 목표
- 실행 단계 마무리: 실제 TickTick sandbox 검증 + 통합 에러 시나리오 테스트 + 배포/패키징 준비

## 2) 현재 구현 상태 요약
- 완료: 기본 스캐폴딩(`src/auth`, `src/api`, `src/core`, `src/shared`, `tests/unit`) 및 TS 설정(`package.json`, `tsconfig.json`)
- 완료: 계약/클라이언트/도메인(`src/common/contract-validation.ts`, `src/config/ticktick-env.ts`, `src/auth/oauth2-contract.ts`, `src/api/ticktick-api-client.ts`, `src/domain/task-contract.ts`, `src/domain/project-contract.ts`)
- 완료: Core 실행 구현체(`src/core/ticktick-usecases.ts`, `src/core/ticktick-runtime.ts`) + 배럴 export(`src/core/index.ts`) 반영
- 완료: Auth/API/Core 테스트 본문 반영(`tests/unit/auth.unit.test.ts`, `tests/unit/api.unit.test.ts`, `tests/unit/core.unit.test.ts`) 및 `npm run typecheck`/`npm test` 통과
- 완료: 루트 `README.md` step-by-step 시작 가이드 작성
- 완료: 루트 `SKILL.md`를 레퍼런스 기반 표준 구조(Quick Reference/Setup/Workflow/Gates)로 정규화
- 미완료: 실 API sandbox 검증/샘플 응답 캡처, 통합 에러 매핑 테스트 추가

## 3) 의존성/핸드오프 포인트
- Auth 계약 확정 후 API 클라이언트 인증 주입 방식 고정
- API 타입 확정 후 Core UseCase 구현 착수
- QA는 타입/에러 계약 확정 시점부터 병렬 테스트 작성 시작

## 4) 다음 세션 즉시 실행 3개 작업
1. 실 TickTick sandbox 계정으로 `/task`, `/project` 호출 smoke script를 추가하고 응답 필드 alias(`title/content`, `desc/description`) 샘플 캡처
2. 401/403/404/429/5xx + timeout/network를 usecase/gateway 경로에서 검증하는 통합 테스트 파일(`tests/unit/integration-error-mapping.unit.test.ts` 등) 추가
3. 배포 전 점검용 smoke entrypoint(script) 작성 + README/`SKILL.md` 운영 섹션(토큰 저장/갱신 정책, 재인증 훅) 동기화

## 5) 이번 세션 종료 전 업데이트 체크리스트
- [ ] `docs/progress-log.md`에 Entry Template 기준으로 append(`What changed`, `Evidence`, `Risks/Blockers`, `Next actions`)
- [ ] `docs/current-status.md`의 `## 이번 세션 변경점(YYYY-MM-DD)`과 `- 검증 상태:` 갱신
- [ ] `## 2) 현재 구현 상태 요약`의 `완료/미완료` 재분류
- [ ] `## 4) 다음 세션 즉시 실행 3개 작업`을 잔여 작업 기준으로 재작성(파일 경로 + 검증 기준 포함)
- [ ] 미해결 이슈를 `## 3) 의존성/핸드오프 포인트`에 반영
