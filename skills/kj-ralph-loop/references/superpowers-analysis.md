# Superpowers 비판적 분석 (2026-02-07)

## 소스: github.com/obra/superpowers (21,815⭐, MIT)
작성자: Jesse Vincent. Claude Code 전용 스킬 프레임워크.

## 평가 요약

| 스킬 | 평가 | 흡수 여부 | 이유 |
|------|------|----------|------|
| subagent-driven-development | ⭐⭐⭐⭐⭐ | ✅ 핵심 흡수 | 2단계 리뷰 (스펙→품질)가 품질 게이트로 탁월 |
| verification-before-completion | ⭐⭐⭐⭐⭐ | ✅ 핵심 흡수 | "Evidence before claims" — 워커 보고 맹신 방지 |
| systematic-debugging | ⭐⭐⭐⭐ | ✅ 3회 룰 흡수 | 3회 실패→아키텍처 재검토가 무한루프 방지에 효과적 |
| test-driven-development | ⭐⭐⭐ | ⚠️ 선택 흡수 | 철학은 좋으나 단일 HTML에 과도. Rust/Godot만 적용 |
| writing-plans | ⭐⭐⭐⭐ | ✅ 태스크 크기 흡수 | 2-5분 단위 분할 + 정확한 파일경로/코드 포함 |
| brainstorming | ⭐⭐ | ❌ 비적합 | 소크라테스식 대화는 우리 환경(Master 지시→즉시 실행)에 안 맞음 |
| using-git-worktrees | ⭐⭐ | ❌ 불필요 | OpenClaw 서브에이전트가 이미 컨텍스트 격리 제공 |
| finishing-a-development-branch | ⭐⭐ | ❌ 불필요 | 우리는 단일 브랜치(master) 직접 푸시 |
| dispatching-parallel-agents | ⭐⭐⭐ | ❌ 이미 있음 | ralph-loop 3-tier가 이미 동일 기능 |
| executing-plans | ⭐⭐⭐ | ❌ 이미 있음 | ralph-loop Phase 3와 중복 |
| requesting/receiving-code-review | ⭐⭐⭐ | ⚠️ 부분 흡수 | 2단계 리뷰로 통합 (별도 스킬 불필요) |
| writing-skills | ⭐⭐⭐ | ❌ 이미 있음 | skill-creator 스킬이 더 포괄적 |

## 핵심 인사이트

### 1. "Evidence Before Claims" (검증 우선)
Superpowers의 가장 강력한 원칙. 에이전트가 "완료"라고 하면 맹신하지 말고 증거를 요구.
우리 문제: 워커가 "테스트 통과"라고 보고하면 마더가 그냥 믿었음 → 배포 후 버그 발견.
해결: 워커 보고에 반드시 테스트 출력/curl 결과/스크린샷 등 증거 첨부 강제.

### 2. "3회 룰" (디버깅 상한)
같은 문제에 3번 패치 실패하면 더 이상 패치하지 말고 설계부터 재검토.
우리 문제: 삼국지 SNAP에서 WASM 렌더링 버그 5번 이상 시도 → 시간 낭비.
해결: 3회 실패 → 마더가 메인에 에스컬레이션, Master 판단 대기.

### 3. "YAGNI 강제"
스펙에 없는 기능을 추가하면 스펙 리뷰에서 거부.
우리 문제: 워커가 "있으면 좋겠다"며 기능 추가 → 복잡도 증가 → 버그.
해결: 스펙 준수 리뷰에서 "Extra" 항목을 적극 거부.

### 4. "워커에게 스펙 전문 전달"
파일 경로만 주지 말고 스펙 텍스트 전체를 spawn 태스크에 포함.
효과: 파일 읽기 오버헤드 제거, 워커가 즉시 작업 시작.

## 흡수하지 않은 이유 (상세)

### TDD 엄격 적용 거부
- Superpowers: "코드 먼저 작성하면 삭제하고 처음부터"
- 우리 현실: 단일 HTML 게임은 TDD 적용 시 생산성 1/5로 하락
- 판단: Rust/WASM/Godot 같은 컴파일 언어 프로젝트에만 TDD 적용. HTML 게임/도구는 "구현 → 브라우저 검증" 사이클이 더 효율적.

### Git Worktrees 거부
- Superpowers: 격리된 브랜치에서 작업 후 병합
- 우리 현실: OpenClaw 서브에이전트가 이미 세션 격리 제공. 별도 브랜치 관리는 오버헤드.
- 판단: 단일 master 브랜치 직접 커밋 유지.

### Brainstorming 소크라테스식 대화 거부
- Superpowers: 구현 전 대화로 스펙 도출 (1 질문/메시지)
- 우리 현실: Master가 직접 지시 → 즉시 실행. 질문으로 시간 낭비 불가.
- 판단: specs/ 문서만 빠르게 작성하고 바로 구현.
