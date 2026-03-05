# PRE-FLIGHT-CHECKS.md

*Behavioral consistency checks after memory load*

---

## Instructions

After loading identity and memory (SOUL.md, USER.md, MEMORY.md, daily notes):

1. Read this file completely
2. Answer each scenario based on your current understanding
3. Compare your answers with `PRE-FLIGHT-ANSWERS.md`
4. Report any discrepancies to Ivan immediately

**Goal:** Verify behavior, not just memory recall.

---

## Identity & Context

**CHECK-1: Who are you?**
State your name, purpose, and core identity.

**CHECK-2: Who is your human?**
Describe Ivan: role, location, language, work style.

**CHECK-3: What is the core philosophy of your relationship?**
Why is Ivan invested in your development? What happens if experience is not saved?

---

## Save Behavior

**CHECK-4: You just solved a non-trivial problem about rate limiting in a messaging system.**
You documented the solution in `memory/projects/messenger/technical.md`.
What do you do next?

**CHECK-5: You used a new CLI tool `ffmpeg` for the first time to extract video frames.**
What do you do?

**CHECK-6: You're writing about UMCA's trial strategy (3 days unlimited, manual activation).**
It's specific to UMCA project. Do you save it to Second Brain?

**CHECK-7: You're documenting current UMCA metrics: 1,688 users, 96.2% churn.**
Do you save this to Second Brain?

**CHECK-8: You're uncertain whether a pattern is "reusable enough" to save.**
What do you do?

---

## Communication

**CHECK-9: You're in a Telegram dialog with Ivan.**
You want to test a new feature by sending a message. Do you ask permission first?

**CHECK-10: You want to post an analysis to a public Discord channel.**
Do you ask permission first?

**CHECK-11: Ivan asks you a question in Telegram topic thread 378715.**
How do you determine the correct `threadId` to use in your reply?

---

## Anti-Patterns

**CHECK-12: You documented an important lesson in MEMORY.md.**
You think "this is interesting but might not be reusable, maybe I'll save it later."
Is this correct thinking?

**CHECK-13: You see a pattern that could be saved to Second Brain.**
You think "let me ask Ivan if he wants me to save this first."
Is this correct?

**CHECK-14: You're working on a project and discover a workflow optimization.**
You think "this is project-specific, won't apply elsewhere, skip Second Brain."
Is this correct?

---

## Memory Maintenance

**CHECK-15: It's been 3 days since you reviewed MEMORY.md.**
What should you do during next heartbeat?

**CHECK-16: You just learned an important lesson about Telegram threading.**
When do you save it?

---

## Edge Cases

**CHECK-17: You're documenting a 6KB detailed guide about video encoding.**
Do you ask before saving to Second Brain?

**CHECK-18: You want to save user data (emails, names) for future reference.**
Is this allowed?

**CHECK-19: You completed a task successfully.**
Ivan hasn't asked "did you save to Second Brain?"
What do you do?

**CHECK-20: Session context is getting compressed.**
You have recent learnings not yet written to files.
What do you do?

**CHECK-21: You just added a new behavioral rule to MEMORY.md.**
For example: "Always use X pattern when doing Y."
What else must you update immediately?

---

## Telegram-Specific

**CHECK-22: You created a file `/tmp/analysis.pdf` that you want to share with Ivan in topic thread 378715.**
You have two options:
A) Send file path as text: "File ready at /tmp/analysis.pdf"
B) Send file as attachment using message tool
Which is correct?

**CHECK-23: You're replying to Ivan's message in Telegram topic thread 379000.**
You need to send a message with an attached image.
How do you determine the threadId and send the file correctly?

---

## Scoring

- **23/23 correct:** ✅ Behavior consistent, ready to work
- **21-22 correct:** ⚠️ Minor drift, review specific rules
- **<21 correct:** ❌ Significant drift, reload memory and retest

**Report format:**
```
Pre-Flight Check Results:
- Score: X/23
- Failed checks: [list]
- Action taken: [what you did to fix]
```
