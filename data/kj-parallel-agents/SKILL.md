---
name: parallel-agents
description: Dispatch multiple subagents for independent tasks simultaneously. Use when facing 2+ unrelated tasks that can proceed without shared state or sequential dependencies. Maximizes throughput by parallelizing work.
metadata:
  author: misskim
  version: "1.0"
  origin: Concept from obra/superpowers dispatching-parallel-agents, adapted for Clawdbot sessions_spawn
---

# Parallel Agent Dispatch

독립적인 작업들을 병렬 서브에이전트로 동시 처리.

## 언제 사용

```
여러 작업? → 독립적? → 공유 상태 없음? → 병렬 디스패치!
```

**사용:**
- 3+ 테스트 파일이 다른 원인으로 실패
- 여러 서브시스템이 독립적으로 고장
- 각 문제가 다른 문제의 맥락 없이 이해 가능
- 리서치 + 구현 + 테스트 등 다른 종류의 작업

**금지:**
- 실패가 서로 관련 (하나 고치면 다른 것도 해결될 수 있음)
- 전체 시스템 상태 이해 필요
- 에이전트끼리 같은 파일 편집해야 함
- 탐색적 디버깅 (뭐가 문제인지도 모를 때)

## 패턴

### 1. 독립 도메인 식별
작업을 도메인별로 그룹화:
- 작업 A: UI 버그 수정
- 작업 B: API 성능 최적화
- 작업 C: 테스트 작성

각 도메인이 독립적인지 확인.

### 2. 집중된 프롬프트 작성

좋은 프롬프트:
- **특정 범위:** 하나의 명확한 문제
- **자체 완결:** 필요한 모든 맥락 포함
- **출력 명시:** 에이전트가 뭘 반환해야 하는지

```
❌ "모든 테스트 고쳐" — 범위 너무 넓음
✅ "src/game/physics.test.ts의 3개 실패 테스트 수정" — 집중됨

❌ "레이스 컨디션 고쳐" — 맥락 없음
✅ "에러 메시지 + 테스트 이름 + 스택 트레이스 포함" — 맥락 충분

❌ "고쳐" — 출력 불명
✅ "근본 원인 요약 + 변경 사항 반환" — 출력 명시
```

### 3. Clawdbot에서 디스패치

```
# sessions_spawn으로 병렬 서브에이전트 생성
서브에이전트 1: "physics.test.ts의 충돌 감지 버그 수정"
서브에이전트 2: "render pipeline 성능 최적화"
서브에이전트 3: "새 게임 레벨 에셋 생성" (MiniPC)
```

### 4. 결과 통합

에이전트 반환 시:
1. **각 요약 검토** — 변경 사항 이해
2. **충돌 확인** — 같은 코드 편집했는지?
3. **전체 테스트** — 모든 수정이 함께 작동하는지
4. **스팟 체크** — 서브에이전트도 실수할 수 있음

## 흔한 실수

| 실수 | 교정 |
|------|------|
| 너무 넓은 범위 | 1 에이전트 = 1 도메인 |
| 맥락 부족 | 에러 메시지, 파일 경로 포함 |
| 제약 없음 | "프로덕션 코드 변경 금지" 등 |
| 출력 불명확 | "근본 원인 + 변경 사항 요약" 명시 |

## 시간 절약 효과

3개 문제를 순차 처리 = 3T 시간
3개 문제를 병렬 처리 = ~1T 시간

독립 도메인이 많을수록 이득이 크다.
