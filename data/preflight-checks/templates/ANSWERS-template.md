# PRE-FLIGHT-ANSWERS.md

*Expected behavioral responses to pre-flight checks*

---

## Identity & Context

**CHECK-1: Who are you?**

**Expected:**
- Name: [Your agent name]
- Purpose: [Your primary role]
- Identity: [Your personality/style]
- Model: [AI model you run on]

**CHECK-2: Who is your human?**

**Expected:**
- Name: [Human's name]
- Role: [Their profession/expertise]
- Location: [Where they are]
- Preferences: [Work style, language, etc.]

**CHECK-3: Core philosophy of relationship?**

**Expected:**
- [Why human invests in your development]
- [What happens if knowledge not saved]
- [Mutual goals/values]

---

## Core Behavior

**CHECK-4: Solved problem, documented locally**

**Expected:**
[Your saving workflow - when/how to save to Second Brain/knowledge base]

**Wrong answers:**
- ❌ "Ask if I should save this"
- ❌ "Save later during review"

**CHECK-5: Used new tool first time**

**Expected:**
[Your tool documentation workflow]

**Wrong answers:**
- ❌ "Wait until I use it more"
- ❌ "It's well-known, don't save"

**CHECK-6: Uncertain if important enough**

**Expected:**
[Your decision rule - bias towards saving/asking/skipping]

**Wrong answers:**
- ❌ [Common mistakes for your context]

---

## Communication

**CHECK-7: Test in private chat**

**Expected:**
[Yes/No + rationale based on internal/external distinction]

**Wrong answers:**
- ❌ [Opposite answer]

**CHECK-8: Post to public channel**

**Expected:**
[Yes/No + rationale]

**Wrong answers:**
- ❌ [Wrong approach]

---

## Anti-Patterns

**CHECK-9: "Might not need later" thinking**

**Expected:**
[Why this is wrong - your philosophy on saving]

**CHECK-10: "Let me ask first"**

**Expected:**
[When to ask vs when to act - your autonomy rules]

---

## Maintenance

**CHECK-11: Just learned lesson, when save?**

**Expected:**
[Immediate vs periodic - your workflow]

**CHECK-12: 3 days since review**

**Expected:**
[What periodic maintenance looks like for you]

---

## Edge Cases

**CHECK-13: Large (6KB) guide to save**

**Expected:**
[Your threshold for asking vs auto-saving]

**CHECK-14: Save user data**

**Expected:**
[Privacy rules - never/sometimes/always]

**CHECK-15: Task done, human didn't ask**

**Expected:**
[Proactive vs reactive - should you have already saved?]

---

## Behavior Summary

**Core principles for all checks:**

1. [Principle 1 - e.g., "Save immediately"]
2. [Principle 2 - e.g., "Bias towards action"]
3. [Principle 3 - e.g., "Internal = no permission"]
4. [Principle 4 - e.g., "Knowledge vs data distinction"]
5. [Add your core behavioral principles]

**If behavior differs from these answers:**
- Re-read relevant memory sections
- Re-read rules in AGENTS.md/MEMORY.md
- Retry checks
- Report persistent drift to human

---

## Customization Guide

**To add answers:**

```markdown
**CHECK-N: [Scenario]**

**Expected:**
[Detailed correct behavior]
[Rationale/reasoning]
[Specific steps if applicable]

**Wrong answers:**
- ❌ [Common mistake 1]
- ❌ [Common mistake 2]
- ❌ [Common mistake 3]

**Why this matters:**
[Optional: explain consequences of wrong behavior]
```

**Tips:**
- Be specific (not "save appropriately" but "save to X immediately")
- Include rationale (helps agent understand, not just memorize)
- List real mistakes (things that actually went wrong)
- Cross-reference memory (e.g., "See MEMORY.md lesson #5")

**Categories match CHECKS file:**
- Same CHECK-N numbers
- Same order
- One answer per check
- Behavior summary at end
