# 개선안 템플릿

> 이 파일은 `generate-proposal.sh`가 참조하는 리포트 형식 템플릿입니다.
> 직접 수정하면 리포트 형식이 변경됩니다.

---

## 🧠 Self-Evolving Agent 주간 분석 리포트

**분석 기간:** {DATE_FROM} ~ {DATE_TO}
**분석된 세션:** {SESSION_COUNT}개
**불만 패턴 감지:** {COMPLAINT_HITS}건
**개선 제안:** {PROPOSAL_COUNT}개

---

### 제안 #{NUMBER}: {TITLE}

**심각도:** {SEVERITY_EMOJI} {SEVERITY}
**근거:** {EVIDENCE}
**대상 섹션:** AGENTS.md > {SECTION}

**Before:**
```
{BEFORE_TEXT}
```

**After:**
```
{AFTER_TEXT}
```

---

### 📋 승인 방법

- **✅ 전체 승인:** `개선안 적용해줘` 또는 `모두 승인`
- **✅ 부분 승인:** `제안 #1만 적용`
- **❌ 거부:** `거부: [이유]` — 이유가 다음 분석에 반영됩니다
- **💬 수정 요청:** `제안 #2를 이렇게 바꿔줘: [내용]`

> 승인 시 AGENTS.md에 자동 반영 + git commit 됩니다.

---

## 심각도 기준

| 심각도 | 이모지 | 설명 |
|--------|--------|------|
| HIGH | 🔴 | 즉각 수정 필요 (반복 실패, 규칙 위반) |
| MEDIUM | 🟡 | 이번 주 내 수정 권장 |
| LOW | 🟢 | 개선 여지 있음, 선택적 |
| INFO | ℹ️ | 참고 사항 |

## 근거(Evidence) 작성 기준

모든 제안에는 **측정 가능한 근거**가 필수입니다:

- ✅ `최근 7일간 "다시" 패턴 3회 감지`
- ✅ `consecutiveErrors > 0인 크론 2개 발견`
- ✅ `git pull 직접 호출 transcript 5회`
- ❌ `사용자가 불편해할 것 같음`
- ❌ `더 나을 것 같아서`

## 거부 이유 기록 형식

거부된 제안은 `data/rejected-proposals.json`에 저장됩니다:

```json
{
  "rejected_at": "2026-02-17T22:00:00",
  "proposal_id": "complaint-pattern-01",
  "title": "반복 불만 패턴 대응 규칙 강화",
  "rejection_reason": "이미 SESSION-STATE.md에서 처리 중",
  "applied_to_next_analysis": true
}
```
