---
name: subagent-dev
description: Execute implementation plans using fresh subagents per task with two-stage review (spec compliance + code quality). Use when executing multi-task plans with independent work units. Enhances ralph-loop methodology.
metadata:
  author: misskim
  version: "1.0"
  origin: Concept from obra/superpowers subagent-driven-development, adapted for Clawdbot sessions_spawn
---

# Subagent-Driven Development

구현 계획을 서브에이전트 단위로 실행, 2단계 리뷰.

## ralph-loop와의 관계

이 스킬은 ralph-loop의 "서브에이전트로 1태스크씩" 원칙을 강화한다:
- ralph-loop = 전체 프로세스 (specs → plan → implement → test)
- subagent-dev = implement 단계의 실행 패턴

## 프로세스

```
계획 읽기 → 태스크 전체 추출
  ↓
[태스크마다 반복]
  1. 구현 서브에이전트 디스패치 (태스크 전문 + 맥락)
     ├─ 질문 있으면? → 답변 후 재디스패치
     └─ 구현 + 테스트 + 커밋 + 셀프리뷰
  2. 스펙 검증 서브에이전트 디스패치
     ├─ 스펙 불일치? → 구현자가 수정 → 재검증
     └─ 통과
  3. 코드 품질 리뷰 서브에이전트 디스패치
     ├─ 품질 이슈? → 구현자가 수정 → 재리뷰
     └─ 승인
  4. 태스크 완료 표시
  ↓
전체 완료 → 최종 코드 리뷰 → 브랜치 마무리
```

## 2단계 리뷰의 핵심

### Stage 1: 스펙 검증
- 코드가 요구사항과 일치하는가?
- 빠진 기능은? 추가된 불필요 기능은?
- 스펙에 명시된 모든 항목이 구현됐는가?

### Stage 2: 코드 품질
- 중복 코드? 네이밍? 타입 커버리지?
- 에러 처리? 엣지 케이스?
- 성능 이슈? 보안 이슈?

**왜 2단계?**
- 스펙 검증 = "맞는 것을 만들었는가?" (What)
- 코드 품질 = "잘 만들었는가?" (How)
- 하나의 리뷰에 합치면 둘 다 놓치기 쉬움

## 서브에이전트 프롬프트 구조

### 구현자 프롬프트
```markdown
## 태스크
[계획에서 추출한 태스크 전문]

## 맥락
[관련 파일, 아키텍처, 제약 조건]

## 제약
- 이 태스크 범위만 수정
- TDD: 테스트 먼저, 구현 후
- 커밋 메시지 작성
- 셀프리뷰 결과 포함

## 출력
- 구현 요약
- 테스트 결과
- 셀프리뷰 발견사항
```

### 스펙 리뷰어 프롬프트
```markdown
## 원본 스펙
[태스크 요구사항 전문]

## 검증 대상
[구현된 코드의 git diff 또는 파일 목록]

## 체크리스트
- 모든 요구사항 구현됐는가?
- 불필요한 추가 기능은?
- 엣지 케이스 처리?
```

## 장점

- **신선한 컨텍스트:** 태스크별 새 서브에이전트 = 오염 없음
- **품질 게이트:** 2단계 리뷰로 이중 검증
- **속도:** 컨트롤러가 태스크 맥락을 사전 준비
- **질문 가능:** 서브에이전트가 모호한 점을 질문

## 비용

- 태스크당 3회 서브에이전트 (구현 + 스펙리뷰 + 품질리뷰)
- 컨트롤러의 준비 작업 필요
- 리뷰 루프 시 추가 호출

**결론:** 비용 대비 품질 이득이 크다. 특히 중요한 기능 구현 시 필수.
