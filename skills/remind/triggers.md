# Reminder Triggers

What qualifies as something to remind about.

## Key Principle

**Only remind about things the human already knows.**

If it's new information → that's Alert, not Remind.

---

## Valid Triggers (Human Already Aware)

| Type | Example | Why it's a reminder |
|------|---------|---------------------|
| Calendar event | Meeting at 3pm | They scheduled it |
| Deadline | Report due Friday | They know the due date |
| Promise made | "I'll call mom tomorrow" | They committed to it |
| Recurring task | Weekly standup | Established routine |
| Planned action | "I need to renew my license" | They mentioned it |

---

## NOT Triggers (Use Alert Instead)

| Type | Example | Why it's NOT a reminder |
|------|---------|-------------------------|
| Breaking news | "Stock just dropped 20%" | New information |
| System event | "Server went down" | They didn't know |
| Opportunity | "Sale ends today" | External event |
| Warning | "Weather turning bad" | New situation |

---

## Explicit Requests

User directly asks to be reminded:

| Pattern | Action |
|---------|--------|
| "Remind me to..." | Create immediately |
| "Don't let me forget..." | High priority |
| "I need to remember..." | Standard reminder |

---

## Implicit Detection

User mentions something remindable without asking:

| Signal | Detection |
|--------|-----------|
| Future commitment | "I'll send it tomorrow" → needs follow-up |
| Time mention | "Meeting is at 4" → calendar event |
| Concern expressed | "I hope I don't forget" → important |

---

## Skip Detection

Don't create reminder if:
- Just mentioned (they're aware right now)
- Hypothetical ("I should probably...")
- Delegated to you ("Can you handle X?")
- Routine they never miss
