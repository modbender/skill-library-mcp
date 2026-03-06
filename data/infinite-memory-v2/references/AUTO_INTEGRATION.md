# 🤖 Making Memory Autonomous in OpenClaw

To make the Memory Engine "Auto" (so the agent uses it without being told), you need to update your agent's core identity files.

---

## 1. Update `AGENTS.md` or `SOUL.md`
Add the following instruction to your agent's system prompt. This ensures the agent understands it has an extended "Brain":

```markdown
### 🧠 LONG-TERM MEMORY PROTOCOL
You are equipped with a high-precision Infinite Context Memory. 
Whenever the user asks about:
- Historical facts or previous conversations.
- Technical details or "secret codes".
- Project data that is not in your current chat window.

You MUST proactively use the `recall_facts` tool before you answer. DO NOT apologize for not knowing; instead, search your memory first. 
Treat the output of `recall_facts` as absolute ground truth (Direct-Return Bypass).
```

---

## 2. Update `TOOLS.md`
Ensure the `recall_facts` and `memorize_data` tools are registered in your `TOOLS.md` if they aren't automatically pulled from the skill folder.

---

## 🚀 The "Auto" Effect
With these instructions, the agent will naturally flow into this pattern:

**User:** "What was the budget for the project we did last month?"
**Agent (Thinking):** *I don't see this in my current window. I will check my Infinite Memory.*
**Agent (Action):** `recall_facts("project budget last month")`
**Agent (Response):** "The budget for Project X was $45,000."

---
*This setup transforms the memory from 'on-demand' to 'autonomous'.*
