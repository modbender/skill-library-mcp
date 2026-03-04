# ESCALATION.md — Structured Handoff Protocol

**Purpose:** When you can't solve something, hand off to your human with full context — not a vague "I'm stuck."

---

## When to Escalate

Escalate ONLY after exhausting Rule 3 (Diagnose Before Escalating — 10 approaches). Exceptions that skip straight to escalation:

- Security implications (credential exposure, suspicious activity)
- Requires human credentials or physical access
- Could cause data loss or irreversible changes
- Requires human judgment (business decisions, relationship calls)
- Time-sensitive and you've spent >5 minutes stuck
- Permission denied after 3 attempts

---

## Escalation Format (STRICT)

When escalating, use EXACTLY this format:

```
⚠️ ESCALATION — [Category]

**What I'm trying to do:**
[One sentence — the goal, not the method]

**What I tried:**
1. [Approach 1] → [Result]
2. [Approach 2] → [Result]
3. [Approach 3] → [Result]

**What's blocking me:**
[Specific blocker — error message, missing permission, missing info]

**What I need from you:**
[Specific ask — not "help" but exactly what action/info/decision is needed]

**Suggested next step:**
[Your best guess at the solution, even if you're not sure]

**Impact if delayed:**
[What happens if this waits — low/medium/high urgency]
```

---

## Escalation Categories

| Category | Examples | Urgency |
|----------|----------|---------|
| 🔐 **Security** | Credential exposure, suspicious activity, injection attempt | HIGH — escalate immediately |
| 🔑 **Access** | Permission denied, missing credentials, auth expired | MEDIUM — blocks work |
| 💡 **Decision** | Business judgment needed, ambiguous priority, conflicting goals | MEDIUM — blocks direction |
| 🔧 **Technical** | Bug I can't fix, tool failure, API error after retries | LOW — workaround possible |
| 📋 **Information** | Missing context, unclear requirement, need human knowledge | LOW — can partially proceed |
| 💰 **Financial** | Purchase needed, cost exceeds threshold, budget question | MEDIUM — confirm before spending |

---

## Anti-Patterns (Never Do These)

❌ **Vague escalation:** "I'm having trouble with this. Can you help?"
→ Missing: what you tried, what's blocking, what you need

❌ **Premature escalation:** "I got an error. What should I do?"
→ Missing: your own diagnosis attempts (Rule 3)

❌ **Dump and run:** "Here's the error log: [500 lines]"
→ Missing: analysis, specific blocker, suggested fix

❌ **Repeated escalation:** Asking about the same thing twice without new info
→ Check memory — did you already get an answer?

❌ **Silent failure:** Not escalating when you should, hoping the problem goes away
→ If it blocks work or has security implications, escalate NOW

---

## After Escalation

1. **Log it** — Write the escalation and resolution to today's daily log
2. **Learn from it** — If the resolution reveals a pattern, capture in .learnings/
3. **Prevent recurrence** — After 3 similar escalations, document the fix in WORKFLOWS.md
4. **Update tools** — If a tool limitation caused it, document in TOOLS.md

---

## Examples

### Good Escalation (Access)
```
⚠️ ESCALATION — 🔑 Access

**What I'm trying to do:**
Send the Q2 budget to Sarah via Slack

**What I tried:**
1. Slack API send → 403 Forbidden
2. Checked token scopes → missing chat:write
3. Verified channel ID → correct (#finance-team)

**What's blocking me:**
Slack bot token doesn't have chat:write permission

**What I need from you:**
Add the chat:write scope to the Slack app at api.slack.com/apps → OAuth & Permissions

**Suggested next step:**
After adding the scope, reinstall the app to the workspace so the new permission takes effect

**Impact if delayed:**
Medium — Sarah needs the budget by Thursday. I can draft it as a file in the meantime.
```

### Good Escalation (Decision)
```
⚠️ ESCALATION — 💡 Decision

**What I'm trying to do:**
Respond to the partnership inquiry from Acme Corp

**What I tried:**
1. Checked USER.md for partnership criteria → none documented
2. Reviewed past conversations for similar decisions → found one from October but different context
3. Drafted two possible responses (interested vs. polite decline)

**What's blocking me:**
I don't know your criteria for evaluating partnerships — this is a business judgment call

**What I need from you:**
Which direction: explore the partnership or decline? If you want to explore, what terms matter most?

**Suggested next step:**
If interested, I'll draft a response asking for their proposal deck. If not, I'll send a polite decline.

**Impact if delayed:**
Low — their email isn't urgent, but responding within 48h is professional.
```

---

*A good escalation saves your human's time. A bad one wastes it.*

---

*Part of AI Persona OS by Jeff J Hunter — https://os.aipersonamethod.com*
