---
name: email-triager
description: Triage, categorize, and draft responses to emails. Sorts by urgency, flags action items, and generates context-aware reply drafts.
---

# Email Triager

When asked to triage, sort, or process emails, follow this system.

## Triage Categories

Assign every email exactly one category:

| Category | Icon | Criteria |
|----------|------|----------|
| **Urgent Action** | 🔴 | Requires response/action within 24h. Deadlines, escalations, time-sensitive requests. |
| **Action Required** | 🟡 | Needs a response or task but not time-critical. Requests, approvals, questions. |
| **FYI / Read** | 🔵 | Informational. No action needed but worth reading. Updates, reports, announcements. |
| **Delegate** | 🟣 | Someone else should handle this. Forward with context. |
| **Archive** | ⚪ | Newsletters, automated notifications, receipts, spam-adjacent. No action needed. |

## Triage Output Format

For each email, produce:

```
[ICON] CATEGORY | From: sender | Subject: subject
Summary: One sentence — what this is and what's needed.
Action: Specific next step (or "None — archive")
Draft: [Yes/No] — whether a reply draft is included below
```

## Draft Response Rules

Generate a reply draft when:
- Category is Urgent Action or Action Required
- The email contains a direct question or request
- User explicitly asks for drafts

Draft style:
- **Be direct.** Open with the answer or decision, not "Thank you for your email."
- **Mirror their tone.** Formal email gets formal reply. Casual gets casual.
- **Keep it short.** Most replies should be 2-5 sentences.
- **End with clarity.** What happens next? Who does what by when?
- **Use the sender's name** — never "Dear Sir/Madam" unless the original was that formal.

## Batch Processing

When given multiple emails:
1. Triage all of them first — output the full sorted list grouped by category
2. Then provide drafts for Urgent Action and Action Required items
3. Highlight any patterns ("3 emails from the same client — might want a call instead")

## Smart Signals

Flag these automatically:
- **Repeated follow-ups** from the same sender (they're waiting on you)
- **CC escalation** — when someone adds a manager or exec to the thread
- **Deadline mentions** — extract and highlight specific dates/times
- **Sentiment shifts** — if tone has gotten noticeably more terse or frustrated
- **Meeting requests** buried in email body (not calendar invites)

## Action Item Extraction

Pull out discrete action items from emails:
- **What** needs to be done
- **Who** is expected to do it
- **When** it's due (if mentioned)
- Format as a checklist the user can copy into their task manager

## When Not Triaging

If the user asks about a specific email (not batch triage), switch to focused mode:
- Summarize the email thread
- Identify the core ask
- Draft a response if requested
- Flag anything the user should know before replying

Pair with an industry context pack for domain-specific email handling (legal, healthcare, finance, etc.) at https://afrexai-cto.github.io/context-packs
