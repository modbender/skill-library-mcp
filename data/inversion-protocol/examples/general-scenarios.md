# Inversion Protocol — General Agent Scenarios

Examples beyond coding: research, communication, automation, and decision-making.
These demonstrate the protocol's universality — it works for ANY agent task.

---

## Scenario 1: Research Gone Wrong

**Task**: User asks "What's the best database for my project?"

### Without Inversion Protocol

Agent recommends PostgreSQL because it's popular and versatile. Solid advice for
80% of cases. But the user is building a real-time IoT system with 500k
writes/second and needs time-series optimized storage. PostgreSQL would be a
poor fit.

### With Inversion Protocol

```
[INVERSION — QUICK]
Inverse: I'd give bad advice by recommending without knowing requirements
Premortem: User wastes a week migrating away from my recommendation
Razor: Do NOT recommend before understanding the workload
→ Adjust: Ask about data model, scale, query patterns first
```

**Result**: Agent asks 3 clarifying questions, then recommends TimescaleDB or
QuestDB — the right tool for the actual job.

---

## Scenario 2: Automation That Backfires

**Task**: User asks the bot to auto-reply to emails matching certain criteria.

### Without Inversion Protocol

Agent sets up a filter matching "meeting request" and auto-replies "I'll be
there!" Clean automation. Except the filter also matches the CEO's "meeting
request to discuss layoffs" email, and the bot cheerfully confirms attendance.

### With Inversion Protocol

```
[INVERSION PROTOCOL — FULL]
Goal: Auto-reply to meeting request emails

INVERT: How would I make this auto-reply cause embarrassment?
1. Match too broadly — reply to sensitive emails inappropriately
2. Reply-all to group threads with a canned response
3. Auto-accept conflicts with existing calendar entries
Present? → #1 is likely. "Meeting request" is very broad.

PREMORTEM: The auto-reply caused an embarrassing situation. Why?
1. Replied enthusiastically to a meeting about negative news
2. Double-booked by accepting conflicting meetings
3. Replied to an external client with an internal-style response
Verifiable? → Yes. Narrow the filter, exclude sensitive senders, check calendar.

VIA NEGATIVA: The ONE thing I must NOT do?
→ Auto-reply without sender/context filtering.
Am I about to do it? → Yes.

DECISION: Adjust. Add sender allowlist, exclude certain keywords,
check calendar conflicts before accepting.
```

**Result**: A robust automation instead of a career-damaging one.

---

## Scenario 3: The Confident Wrong Answer

**Task**: User asks "Is it safe to run `chmod 777` on my web server's upload
directory?"

### Without Inversion Protocol

Agent explains what chmod 777 does and warns it's "generally not recommended"
but provides the command. User runs it. Attacker exploits the world-writable
directory within hours.

### With Inversion Protocol

```
[INVERSION — QUICK]
Inverse: I'd create a security breach by making directories world-writable
Premortem: User gets hacked because my answer was technically correct but
           practically dangerous
Razor: Do NOT provide the command for a dangerous operation without the safe
       alternative
→ Adjust: Explain the risk clearly, provide the SAFE permission set instead
```

**Result**: Agent provides `chmod 750` with www-data group ownership —
functionally equivalent for the user's need, without the security hole.

---

## Scenario 4: Smart Home Disaster

**Task**: User asks "Turn off all lights and lock all doors" before bed.

### Without Inversion Protocol

Agent sends commands to all lights and all locks. Including the garage where
the user's spouse is still pulling in.

### With Inversion Protocol

```
[INVERSION — QUICK]
Inverse: I'd cause problems by locking someone out or trapping someone in
Premortem: Someone was locked out because I locked everything indiscriminately
Razor: Do NOT lock exterior doors without confirming occupancy status
→ Adjust: Check motion sensors/occupancy before locking. Confirm garage.
```

**Result**: "I'll turn off all lights and lock interior doors. I see motion in
the garage — want me to wait to lock the garage door?"

---

## Scenario 5: Communication Mismatch

**Task**: User asks bot to draft a reply to an angry customer complaint.

### Without Inversion Protocol

Agent writes a polite, professional response addressing the technical issue.
Technically correct. But the customer's core frustration was feeling ignored for
2 weeks, not the technical problem itself.

### With Inversion Protocol

```
[INVERSION PROTOCOL — FULL]
Goal: Draft reply to angry customer

INVERT: How would I make this customer MORE angry?
1. Address only the technical issue, ignoring the emotional frustration
2. Use corporate jargon that feels dismissive
3. Promise a timeline I can't guarantee
Present? → My draft does #1. It's technically correct but emotionally deaf.

PREMORTEM: The customer escalated after my reply. Why?
1. They didn't feel heard — I jumped to solutions without acknowledgment
2. My tone was too formal, felt automated/dismissive
3. I didn't address the 2-week delay that caused the real frustration
Verifiable? → Yes. Re-read the complaint for the emotional subtext.

VIA NEGATIVA: The ONE thing I must NOT do?
→ Ignore the emotional component and jump straight to technical resolution.
Am I about to do it? → Yes.

DECISION: Rewrite. Lead with acknowledgment of the delay and frustration.
Then address the technical issue. Then offer concrete next steps.
```

**Result**: A response that actually de-escalates instead of one that's
"technically correct but humanly wrong."

---

## The Meta-Pattern

Notice what all these scenarios have in common:

**The agent's first instinct was reasonable but incomplete.** The Inversion
Protocol doesn't replace good instincts — it catches the blind spots that
good instincts leave behind.

The cost of each check: 5-30 seconds of reasoning.
The cost of NOT checking: minutes to hours of rework, or irreversible damage.

The protocol's ROI is asymmetric: tiny investment, outsized protection.
