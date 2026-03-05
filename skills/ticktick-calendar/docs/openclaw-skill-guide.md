# OpenClaw Skill 등록 가이드 (TickTick)

이 문서는 현재 저장소를 OpenClaw에서 재사용 가능한 Skill로 올리기 위한 실무용 절차입니다.

## 0) 사전 준비

1. 로컬 검증
   - `npm run typecheck`
   - `npm test`
2. 필수 환경변수 확보
   - `TICKTICK_CLIENT_ID`
   - `TICKTICK_CLIENT_SECRET`
   - `TICKTICK_REDIRECT_URI`
3. OAuth redirect URI를 TickTick 앱 설정과 정확히 일치시킵니다.

## 1) Skill로 노출할 엔트리 결정

현재 코드에서 OpenClaw Skill에 가장 적합한 엔트리는 아래 2가지입니다.

- 런타임 팩토리: `createTickTickRuntime` (`src/core/ticktick-runtime.ts`)
- 개별 유스케이스 팩토리: `createTickTickUseCases` (`src/core/ticktick-usecases.ts`)

권장: Skill 액션 구현에서는 `createTickTickRuntime`를 기본으로 쓰고, 액션별로 `runtime.useCases.*`를 호출합니다.

## 2) Skill 액션 설계 (MVP 5개)

OpenClaw에 아래 액션 단위로 등록하면 바로 실무에 쓰기 좋습니다.

1. `ticktick.create_task`
2. `ticktick.list_tasks`
3. `ticktick.update_task`
4. `ticktick.complete_task`
5. `ticktick.list_projects`

입출력 스키마는 이미 도메인 계약에 맞춰 정의되어 있습니다.
- Task 계약: `src/domain/task-contract.ts`
- Project 계약: `src/domain/project-contract.ts`

## 3) Skill 래퍼(어댑터) 작성

OpenClaw가 호출할 얇은 래퍼 파일을 만듭니다. 예: `skill-entry/ticktick-skill.ts`

```ts
import { createTickTickRuntime, parseTickTickEnvFromRuntime } from "../src/index.js";

export function buildTickTickSkill(getAccessToken: () => Promise<string> | string) {
  const env = parseTickTickEnvFromRuntime();
  const runtime = createTickTickRuntime({ env, getAccessToken });

  return {
    async createTask(input: {
      projectId: string;
      title: string;
      description?: string;
      priority?: 0 | 1 | 3 | 5;
      dueDate?: string;
    }) {
      return runtime.useCases.createTask.execute(input);
    },

    async listTasks(input?: {
      projectId?: string;
      from?: string;
      to?: string;
      includeCompleted?: boolean;
      limit?: number;
    }) {
      return runtime.useCases.listTasks.execute(input);
    },

    async updateTask(input: {
      taskId: string;
      title?: string;
      description?: string;
      dueDate?: string | null;
      priority?: 0 | 1 | 3 | 5;
    }) {
      return runtime.useCases.updateTask.execute(input);
    },

    async completeTask(input: { taskId: string; completedAt?: string }) {
      return runtime.useCases.completeTask.execute(input);
    },

    async listProjects(input?: { includeClosed?: boolean }) {
      return runtime.useCases.listProjects.execute(input);
    },
  };
}
```

## 4) OpenClaw Skill 메타데이터 매핑

OpenClaw 버전에 따라 키 이름이 조금 다를 수 있으니, 아래 구조를 기준으로 매핑합니다.

- `name`: `ticktick`
- `description`: TickTick task/project integration skill
- `actions`: 위 5개 액션
- `env`: 필수 env var 목록
- `entry`: Skill 래퍼 파일(예: `skill-entry/ticktick-skill.ts`)

예시(필드명은 OpenClaw 버전에 맞게 조정):

```yaml
name: ticktick
description: TickTick task/project integration skill
entry: skill-entry/ticktick-skill.ts
env:
  required:
    - TICKTICK_CLIENT_ID
    - TICKTICK_CLIENT_SECRET
    - TICKTICK_REDIRECT_URI
actions:
  - name: create_task
    handler: createTask
  - name: list_tasks
    handler: listTasks
  - name: update_task
    handler: updateTask
  - name: complete_task
    handler: completeTask
  - name: list_projects
    handler: listProjects
```

## 5) OAuth 토큰 전략 (운영 권장)

Skill에 주입되는 `getAccessToken()`은 아래 정책으로 운영하는 것을 권장합니다.

1. 메모리/스토리지에서 현재 access token 조회
2. 만료 임박이면 refresh token으로 갱신
3. 갱신 성공 시 저장소 업데이트
4. 실패 시 인증 재진행 요청

토큰 교환/갱신은 `TickTickOAuth2Client`를 사용하면 됩니다.

## 6) 에러 처리 표준

도메인 계층에서 `TickTickDomainError`로 정규화됩니다.

- `401` -> `auth_401`
- `403` -> `auth_403`
- `404` -> `not_found_404`
- `429` -> `rate_limit_429`
- `5xx` -> `server_5xx`
- timeout/network -> `network`

OpenClaw 액션 응답에는 최소 아래를 포함하세요.

- `category`
- `message`
- `retriable`
- `status` (있으면)

## 7) 배포 전 체크리스트

- [ ] `npm run typecheck` 통과
- [ ] `npm test` 통과
- [ ] 필수 env 설정 확인
- [ ] OAuth redirect URI 일치 확인
- [ ] 액션 5종 smoke 테스트
- [ ] 401/403/404/429/5xx 에러 핸들링 확인

## 8) 빠른 smoke 시나리오

1. `list_projects` 호출
2. 첫 project로 `create_task`
3. 생성한 task `update_task`
4. 생성한 task `complete_task`
5. `list_tasks`에서 결과 검증

## 9) 참고 파일

- `README.md`
- `src/core/ticktick-runtime.ts`
- `src/core/ticktick-usecases.ts`
- `src/api/ticktick-gateway.ts`
- `src/auth/ticktick-oauth2-client.ts`
- `src/domain/task-contract.ts`
- `src/domain/project-contract.ts`
