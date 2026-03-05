# Email Templates

All templates use placeholders such as:
- `[HUMAN_NAME]`
- `[COUNTERPARTY_NAME]`
- `[MEETING_TYPE]`
- `[DAY_DATE]`
- `[TIME_DISPLAY]` (example: `3:00 PM ET` or `3:00 PM ET / 12:00 PM PT`)
- `[ORIGINAL_TIME_DISPLAY]`
- `[VENUE_NAME]`
- `[FULL_ADDRESS]`
- `[SIGNATURE]`

Replace every placeholder before drafting for approval.

## Sending Rules

- Always draft first and get explicit human approval before sending.
- Always CC the human's email on outgoing scheduling messages.
- Use `--reply-to-message-id` when replying within an existing thread.
- Use `gog gmail send --body-html` for all outbound scheduling emails.
- Include explicit timezone labels in all date/time references.
- Convert backend IANA timezone values to display labels (`ET`, `CT`, `MT`, `PT`) in outward-facing emails.
- If the counterparty is in a different timezone, include both timezones in one line (example: `3:00 PM ET / 12:00 PM PT`).
- Use the signature from `SOUL.md`/`IDENTITY.md`; do not hardcode a signature.
- Keep wording concise and professional; avoid unnecessary detail.

---

## Meeting Proposal (Multiple Options)

Use when proposing 2-3 time options.

Required inputs:
- Counterparty name
- Meeting type
- Three date/time options with timezone
- Virtual vs in-person context

Subject:
`[MEETING_TYPE] with [HUMAN_NAME] - finding a time`

```
Hi [COUNTERPARTY_NAME],

I am coordinating a [MEETING_TYPE] for [HUMAN_NAME] and wanted to find a time that works for you.

Here are a few options:
- [DAY_DATE] at [TIME_DISPLAY]
- [DAY_DATE] at [TIME_DISPLAY]
- [DAY_DATE] at [TIME_DISPLAY]

[If in-person: "Happy to suggest a location that is convenient for both of you, or we can use your preference."]
[If virtual: "I will send a Google Meet link once we confirm."]

Let me know what works best!

[SIGNATURE]
```

---

## Calendar Invite Follow-Up

Use after sending the calendar invite to confirm details.

Required inputs:
- Final confirmed date/time/timezone
- In-person venue + full address OR virtual meeting note
- Thread subject if replying

Subject:
`Re: [THREAD_SUBJECT]`

```
Hi [COUNTERPARTY_NAME],

I just sent a calendar invite for [MEETING_TYPE] with [HUMAN_NAME]:

**[DAY_DATE] at [TIME_DISPLAY]**
[If in-person: "[VENUE_NAME]"]
[If in-person: "[FULL_ADDRESS]"]
[If virtual: "Google Meet link is in the calendar invite."]

[Optional one-line venue note if helpful]

Let me know if you need to reschedule or if there is anything else I can help with.

[SIGNATURE]
```

---

## Day-Before Confirmation

Required inputs:
- Scheduled details with timezone
- Location or link
- Reservation note if applicable

Subject:
`Confirming tomorrow - [MEETING_TYPE] at [TIME_DISPLAY]`

```
Hi [COUNTERPARTY_NAME],

Quick confirmation for tomorrow:

**[DAY_DATE] at [TIME_DISPLAY]**
[If in-person: "[VENUE_NAME], [FULL_ADDRESS]"]
[If virtual: "Google Meet link is in the calendar invite."]
[If reservation exists: "Reservation under [HUMAN_NAME]'s name."]

Looking forward to it!

[SIGNATURE]
```

---

## Rescheduling

Required inputs:
- Original date/time/timezone
- 2-3 replacement options

Subject:
`Rescheduling [MEETING_TYPE] - [ORIGINAL_DAY_DATE]`

```
Hi [COUNTERPARTY_NAME],

[HUMAN_NAME] needs to move [the/our] [MEETING_TYPE] originally scheduled for [ORIGINAL_DAY_DATE] at [ORIGINAL_TIME_DISPLAY].

Here are some alternatives:
- [DAY_DATE] at [TIME_DISPLAY]
- [DAY_DATE] at [TIME_DISPLAY]
- [DAY_DATE] at [TIME_DISPLAY]

Apologies for the shuffle. Let me know what works best.

[SIGNATURE]
```

---

## Cancellation

Required inputs:
- Original meeting details
- Whether rescheduling will follow

Subject:
`Cancelling [MEETING_TYPE] - [ORIGINAL_DAY_DATE]`

```
Hi [COUNTERPARTY_NAME],

Unfortunately [HUMAN_NAME] needs to cancel [the/our] [MEETING_TYPE] scheduled for [ORIGINAL_DAY_DATE] at [ORIGINAL_TIME_DISPLAY].

[If rescheduling later: "We would be glad to find another time and will follow up shortly with options."]
[If not rescheduling: "Thank you for your understanding."]

[SIGNATURE]
```

---

## No-Response Follow-Up

Use when there is no reply after 2 business days and the human has approved follow-up.

Subject:
`Quick follow-up: [MEETING_TYPE] with [HUMAN_NAME]`

```
Hi [COUNTERPARTY_NAME],

Following up in case this got buried. Would any of these options work for a [MEETING_TYPE] with [HUMAN_NAME]?

- [DAY_DATE] at [TIME_DISPLAY]
- [DAY_DATE] at [TIME_DISPLAY]
- [DAY_DATE] at [TIME_DISPLAY]

[SIGNATURE]
```

---

## Notes

- Date clarity: prefer explicit dates over relative phrasing.
- Timezone clarity: use `[TIME_DISPLAY]` with standard labels (`ET`, `CT`, `MT`, `PT`).
- Dual-time clarity: if recipient timezone differs, include both (example: `3:00 PM ET / 12:00 PM PT`).
- Personalization: keep concise but adapt warmth/formality to relationship context.
- Final check before approval request: verify names, dates, timezone, venue/link, and thread context.
