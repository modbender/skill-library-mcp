# Task Contract Templates

## Purpose
Formalize delegation with clear specs so output can be auto-verified.

---

## Contract Schema

```markdown
### Contract: [TASK_ID]
- **Delegatee:** agent tier/name
- **Objective:** One-sentence description
- **Input:** What the agent receives
- **Expected Output:**
  - **Type:** file | json | markdown | code | message
  - **Location:** Where output should be written
  - **Format:** Structure requirements
- **Success Criteria:** (machine-checkable)
  - [ ] Output file exists
  - [ ] Output is valid (parseable, non-empty)
  - [ ] Output meets spec
- **Constraints:**
  - **Timeout:** Max runtime
  - **Scope:** What agent should NOT do
  - **Data sensitivity:** Privacy requirements
- **Autonomy:** atomic | bounded | open-ended
- **Fallback:** retry_same | retry_different | escalate | script
- **Verification:** auto | manual | both
```

---

## Example Contracts

### Quick Check Task
- **Delegatee:** Cheap tier
- **Expected Output:** Message returned to session
- **Success Criteria:** Reports findings or "nothing found"
- **Autonomy:** atomic
- **Fallback:** retry once, then skip

### Build/Code Task
- **Delegatee:** Capable tier
- **Expected Output:** Code files at specified path
- **Success Criteria:**
  - [ ] Main file exists and >50 lines
  - [ ] App runs without errors
- **Autonomy:** bounded
- **Fallback:** retry with error context, then escalate

### Research Task
- **Delegatee:** Balanced tier
- **Expected Output:** Markdown file
- **Success Criteria:**
  - [ ] File exists, >500 words
  - [ ] Contains required sections
- **Autonomy:** bounded
- **Fallback:** try different agent, then escalate
