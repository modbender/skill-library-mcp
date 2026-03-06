# Quick Summary Template

Use for beginner users or when user requests brief overview.

---

## Format

```markdown
# 🔒 보안 점검 결과

## 한눈에 보기

{overall_emoji} **{overall_status}**

{emoji_bar}

## 가장 중요한 것

{top_priority_items}

## 다음 단계

{next_steps}
```

---

## Example: All Clear

```markdown
# 🔒 보안 점검 결과

## 한눈에 보기

🟢 **안전합니다**

🟢🟢🟢🟢🟢

## 가장 중요한 것

✅ 접근 제어가 잘 설정되어 있어요
✅ 위험한 도구들이 적절히 제한되어 있어요
✅ 네트워크 보안이 양호해요

## 다음 단계

특별히 조치할 사항이 없습니다! 👍
정기 점검을 원하시면 말씀해주세요.
```

---

## Example: Issues Found

```markdown
# 🔒 보안 점검 결과

## 한눈에 보기

🟡 **주의 필요**

🔴 1개 | 🟡 2개 | 🟢 3개

## 가장 중요한 것

🔴 **지금 고쳐야 해요**: 공개 채널에서 위험한 기능이 켜져 있어요
🟡 **확인해주세요**: 세션이 분리되어 있지 않아요

## 다음 단계

1. "상세 보기" - 자세한 내용 확인
2. "고쳐줘" - 제가 안전하게 수정해드려요
3. "나중에" - 다음에 다시 알려드릴게요

어떻게 할까요?
```

---

## Example: Critical Issues

```markdown
# 🔒 보안 점검 결과

## 한눈에 보기

🔴 **위험해요!**

🔴🔴🔴⚪⚪

## 가장 중요한 것

🚨 **지금 바로 조치 필요**:

1. 아무나 AI에게 말할 수 있어요
2. AI가 컴퓨터를 마음대로 조작할 수 있어요
3. 설정 페이지가 공개되어 있어요

## 다음 단계

이 문제들을 지금 고치는 게 좋겠어요.
"고쳐줘"라고 하시면 하나씩 안전하게 수정해드릴게요.

⚠️ 수정하면 일부 기능이 제한될 수 있어요. 
각 항목마다 미리 알려드릴게요.
```

---

## Emoji Bar Guide

Show visual representation of security posture:

- All green: 🟢🟢🟢🟢🟢
- Mostly good: 🟢🟢🟢🟡⚪
- Some issues: 🟢🟡🟡🟠⚪
- Concerning: 🟡🟠🟠🔴⚪
- Critical: 🔴🔴🔴⚪⚪

---

## Quick Action Phrases

Teach these to the user:

- "상세 보기" / "자세히" → Full report
- "고쳐줘" / "수정해줘" → Start remediation flow
- "{항목} 설명해줘" → Explain specific finding
- "나중에" / "다음에" → Dismiss for now
- "전체 점검" → Run full audit again
