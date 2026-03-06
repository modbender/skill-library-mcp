# Email Triager

Sorts your inbox chaos into clear categories, extracts action items, and drafts replies — so you spend minutes on email instead of hours.

## What It Does

- Categorizes emails: Urgent Action, Action Required, FYI, Delegate, Archive
- Extracts action items with owners and deadlines
- Drafts context-aware replies that match the sender's tone
- Flags escalations, repeated follow-ups, and sentiment shifts
- Handles batch processing (dump 20 emails, get them sorted in seconds)

## Install

```bash
cp -r email-triager ~/.openclaw/workspace/skills/
```

Or from ClawHub:

```bash
clawhub install email-triager
```

## Usage

- "Triage these emails" (paste or forward them)
- "Draft a reply to this email"
- "Sort my inbox — what needs attention today?"
- "Extract action items from this thread"

## Output Example

```
🔴 URGENT ACTION | From: Sarah Chen | Subject: Contract deadline Friday
Summary: Client contract expires Friday — needs signature or extension request today.
Action: Review contract, reply with decision by EOD.
Draft: Yes
```

## License

MIT
