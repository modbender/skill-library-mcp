---
name: tdd-discipline
description: Test-Driven Development methodology. Use when implementing features or fixing bugs. Write the test first, watch it fail, write minimal code to pass, then refactor. Prevents untested code from shipping.
metadata:
  author: misskim
  version: "1.0"
  origin: Concept from obra/superpowers test-driven-development, condensed for practical use
---

# TDD Discipline

## 핵심 사이클

```
RED → GREEN → REFACTOR → 반복
```

### RED: 실패하는 테스트 작성
- 하나의 동작만 테스트
- 명확한 이름 ("rejects empty email" ✅, "test1" ❌)
- 실제 코드 사용 (mock 최소화)

### 검증: 실패 확인 (필수! 건너뛰기 금지)
```bash
npm test path/to/test.test.ts
```
- 테스트가 실패하는가? (에러가 아닌 실패)
- 실패 메시지가 예상대로인가?
- 기능 미구현 때문에 실패하는가? (오타 아닌지 확인)

### GREEN: 최소한의 코드
- 테스트를 통과하는 가장 간단한 코드
- 기능 추가 금지, 리팩토링 금지
- YAGNI (You Ain't Gonna Need It)

### REFACTOR: 정리
- 중복 제거, 이름 개선, 헬퍼 추출
- 테스트는 계속 GREEN 유지
- 동작 추가 금지

## 위반 시 규칙

```
테스트 전에 코드 작성했으면? → 삭제. 처음부터.
```

- "참고용으로 남기자" ❌
- "테스트 쓰면서 적용하자" ❌
- "보지도 말자" ✅

## 적용 시점

**항상:**
- 새 기능 구현
- 버그 수정 (버그 재현 테스트 먼저!)
- 동작 변경

**예외 (주인님 판단):**
- 일회성 프로토타입
- 설정 파일
- 생성된 코드

## 흔한 합리화

| 핑계 | 현실 |
|------|------|
| "너무 간단해서 테스트 불필요" | 간단한 코드도 깨짐. 테스트 30초 |
| "나중에 테스트 쓸게" | 나중 = 즉시 통과 = 아무것도 증명 못함 |
| "TDD가 느려" | TDD가 디버깅보다 빠름 |
| "수동으로 테스트했어" | 수동 = 기록 없음, 재실행 불가 |
| "X시간 작업 삭제가 아까워" | 매몰비용. 검증 안 된 코드가 진짜 낭비 |

## 버그 수정 시 TDD

1. 버그 재현하는 테스트 작성
2. RED 확인 (테스트가 버그를 잡는지)
3. 수정 코드 작성
4. GREEN 확인
5. 회귀 테스트로 영구 보존
