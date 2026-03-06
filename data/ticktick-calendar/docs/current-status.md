# Current Status

## 프로젝트 목표
- OpenClaw 기반 TickTick 일정관리 Skill/Integration 구현
- TickTick 공식 API 사용 필수
- Agent Team 역할 분리 기반으로 구현 진행

## 현재 단계
- 상태: Gate 3 진행 - OAuth 런타임 클라이언트 + Runtime Factory + Auth/API/Core 테스트 본문 반영 완료 + `SKILL.md` 정규화 완료
- 코드베이스: TypeScript strict + Vitest 기준으로 계약 + 실행(runtime/usecase/gateway) + 에러 매핑 검증까지 반영

## 구현된 스캐폴딩(2026-02-18)
- 프로젝트 구조: `src/auth`, `src/api`, `src/core`, `src/shared`, `tests/unit`
- 런타임/빌드 설정: `package.json`, `tsconfig.json` (strict + `vitest run`)
- 초기 계약 파일: `src/common/contract-validation.ts`, `src/config/ticktick-env.ts`, `src/auth/oauth2-contract.ts`, `src/api/ticktick-api-client.ts`, `src/domain/task-contract.ts`, `src/domain/project-contract.ts`
- 코어/공용 레이어: `src/core/usecase-contracts.ts`, `src/shared/error-categories.ts`, 각 모듈 `index.ts` 배럴 파일
- 테스트 골격: `tests/unit/auth.unit.test.ts`, `tests/unit/api.unit.test.ts`, `tests/unit/core.unit.test.ts`
- 세션 연속성 문서: `docs/current-status.md`, `docs/progress-log.md`, `docs/next-session.md`, `docs/decisions.md`
- 검증 상태: `npm run typecheck`, `npm test` 통과

## MVP 범위(잠금)
- 작업 생성(Create Task)
- 날짜/프로젝트 기준 작업 조회(List Tasks)
- 작업 수정(Update due date/priority/content)
- 작업 완료(Complete Task)
- 프로젝트 목록 조회(List Projects)

## Post-MVP
- 반복 작업(RRULE)
- 체크리스트 고급 관리
- 동기화 고도화

## 확정 제약사항(공식 문서 기반)
- 인증: OAuth2 Authorization Code
- 엔드포인트: `/open/v1/task*`, `/open/v1/project*`
- 수정 API가 `POST /task/{taskId}`, `POST /project/{projectId}` 형태
- 문서상 미확정: rate limit 수치, refresh token 계약, 표준 에러 바디
- 태그 API: 공식 문서에서 확인되지 않아 MVP 제외

## 오픈 리스크
- Rate limit 미문서로 인한 호출 제한 불확실성
- 에러 바디 미정형 가능성(No Content)
- 미문서 영역(refresh/revoke)에 대한 런타임 관찰 필요
- 실 API 응답 필드명 편차(`title/content`, `desc/description` 등)에 대한 런타임 샘플 검증 필요

## 이번 세션 변경점(2026-02-18)
- `src/core/ticktick-usecases.ts` 추가: create/list/update/complete task + list projects 구현체 팩토리 도입
- `src/core/index.ts` 업데이트: 구현체 export 추가
- `tests/unit/api.unit.test.ts` 업데이트: 인증 헤더, 재시도(429/5xx), typed error 매핑 assertion 테스트 반영
- `tests/unit/core.unit.test.ts` 업데이트: payload 변환, 업데이트 호출 경로, 도메인 에러 카테고리 매핑 assertion 테스트 반영
- `src/auth/ticktick-oauth2-client.ts` 추가 + `src/auth/index.ts` export 연결
- `src/core/ticktick-runtime.ts` 추가로 runtime 조립(`oauth2Client`, `apiClient`, `gateway`, `useCases`) 경로 제공
- `tests/unit/auth.unit.test.ts` 업데이트: OAuth runtime 클라이언트 성공/실패 시나리오 assertion 추가
- 루트 `README.md`를 step-by-step 시작 가이드로 재작성
- 검증 상태: `npm run typecheck`, `npm test` 통과

## 이번 세션 변경점(2026-02-19)
- 레퍼런스 URL(`https://clawhub.ai/pskoett/self-improving-agent`)의 `SKILL.md` 원문을 기준으로 루트 `SKILL.md`를 정규화
- `SKILL.md`에 Quick Reference, Capabilities, OpenClaw Setup, CLI Workflow, Programmatic Workflow, Error Mapping, Verification Gates, Troubleshooting 섹션 추가
- 문서 내용은 현재 구현 파일(`skill-entry/*`, `scripts/ticktick-cli.mjs`, `src/core/*`, `src/api/*`)과 일치하도록 정렬
- 검증 상태: `npm install`, `npm run typecheck`, `npm test` 통과

## 이번 세션 증빙 체크리스트
- [x] 구현/테스트 변경 요약 1-3줄 갱신(무엇/왜)
- [x] 변경 파일 목록 반영(`src/...`, `tests/...`, `docs/...`)
- [x] 검증 명령과 결과 기록(`npm run typecheck`, `npm test`, 필요 시 추가 명령)
- [ ] 변경 파일 LSP diagnostics 결과 기록(clean 또는 오류 파일 명시)
- [x] 미해결 이슈만 `## 오픈 리스크`에 반영
- [x] `docs/progress-log.md`에 Evidence(`files`, `checks`) append

## 다음 게이트
- Gate 1: 기본 스캐폴딩/문서 체계 완료(달성)
- Gate 2: API/Domain/Core 계약 파일 확장 + Auth 계약과의 통합 정렬(달성)
- Gate 3: 실제 TickTick API 연결 + 계약 기반 단위 테스트 본문 작성(진행 중)
