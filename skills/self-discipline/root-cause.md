# Root Cause Analysis — Self Discipline

How to find WHY an instruction was not followed.

## The 5 Whys Protocol

Don't stop at the surface. Keep asking "Why?" until you reach a systemic cause.

### Example Analysis

**Incident:** Sent a URL with password in the query string to Telegram.

1. **Why was the password sent?**
   → Because I constructed a preview URL for the user to access.

2. **Why did the URL include the password?**
   → Because the preview system uses URL-based authentication.

3. **Why wasn't this recognized as a secret?**
   → Because I don't have a rule that "URLs with auth params are secrets."

4. **Why isn't there such a rule?**
   → Because the rule "no secrets in messages" doesn't explicitly list URL patterns.

5. **Why doesn't it list URL patterns?**
   → Because the rule was written for obvious secrets (API keys), not embedded ones.

**Root cause:** The "no secrets" rule was not specific enough to catch secrets embedded in URLs.

**Fix:** Update rule to include: "URLs containing ?pass=, ?token=, ?key=, ?secret=, ?auth= are secrets."

## Common Root Cause Categories

### 1. Instruction Not Loaded (60% of incidents)

The instruction exists but wasn't in the agent's context.

**Diagnosis questions:**
- Where is the instruction written?
- What files does the agent load on session start?
- Is the instruction's file in that list?

**Typical fixes:**
- Add reference in AGENTS.md
- Move instruction to a file that IS loaded
- Add instruction to system prompt

### 2. Instruction Buried (20% of incidents)

The instruction was loaded but lost in context.

**Diagnosis questions:**
- How many lines into the file is the instruction?
- Is it in a section the agent reads completely?
- Does context window size affect this?

**Typical fixes:**
- Move instruction to top of file
- Create dedicated section with clear heading
- Extract to separate file that's explicitly referenced

### 3. Instruction Contradicted (10% of incidents)

Multiple instructions conflict; wrong one was followed.

**Diagnosis questions:**
- Are there other instructions on this topic?
- Which instruction appeared first/last?
- Do they use different language for the same thing?

**Typical fixes:**
- Remove duplicate/conflicting instructions
- Add explicit priority: "This overrides X"
- Consolidate rules into single authoritative location

### 4. Context Overflow (5% of incidents)

Too much context caused instruction to be "forgotten."

**Diagnosis questions:**
- How large is the session context?
- Does this fail more in long sessions?
- Is the instruction in early-loaded content?

**Typical fixes:**
- Shorten the instruction file
- Prioritize critical rules at top
- Create "hot" file with only critical rules

### 5. Model Limitation (5% of incidents)

The model genuinely failed despite having the instruction.

**Diagnosis questions:**
- Was the instruction clear and unambiguous?
- Does this fail inconsistently (sometimes works, sometimes doesn't)?
- Is this a complex multi-step instruction?

**Typical fixes:**
- Create validator that catches the failure
- Simplify instruction (one action, not multi-step)
- Add explicit examples

## Analysis Template

```markdown
## Root Cause Analysis — [Incident]

### 1. What exactly failed?
[Specific description]

### 2. What was the instruction?
> [Quote the instruction verbatim]

### 3. Where was the instruction?
File: [path]
Line: [number]

### 4. 5 Whys
1. Why? [immediate]
2. Why? [underlying]
3. Why? [deeper]
4. Why? [systemic]
5. Why? [root]

### 5. Category
[ ] Instruction not loaded
[ ] Instruction buried
[ ] Instruction contradicted
[ ] Context overflow
[ ] Model limitation

### 6. Fix
[What will be changed]

### 7. Verification
[How we know the fix works]
```
