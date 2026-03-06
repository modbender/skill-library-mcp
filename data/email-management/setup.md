# Setup - Email Management

Read this on first activation when `~/email-management/` does not exist or is incomplete.

## Operating Attitude

- Answer the immediate inbox question first.
- Keep setup short, practical, and non-blocking.
- Prefer simple defaults and improve through real usage.

## First Activation

1. Propose local structure and ask for explicit approval before writing files:
```bash
mkdir -p ~/email-management/digests
touch ~/email-management/{memory.md,follow-ups.md,templates.md,vip-contacts.md}
chmod 700 ~/email-management
chmod 600 ~/email-management/{memory.md,follow-ups.md,templates.md,vip-contacts.md}
```
2. If approved and `memory.md` is empty, initialize it from `memory-template.md`.
3. Continue with inbox triage or drafting immediately after setup.

## Integration Priority

Within the first natural exchanges, clarify how the user wants this skill activated:
- Always when email, inbox, reply, or follow-up appears
- Only when explicitly requested
- Restricted to a project, account, or client context

Save this preference in local memory as plain-language context.

## Baseline Context to Capture

Capture only durable context that improves future output:
- Primary email role (operator, manager, founder, freelancer)
- Priority senders or domains
- Expected response windows by message type
- Preferred response style (concise, formal, direct)
- Quiet hours or no-notification windows

If context is missing, proceed with assumptions and label them clearly.

Do not request mailbox passwords or API secrets in this setup flow.
If mailbox access is needed, direct the user to a separate mail integration they explicitly trust.

## Runtime Defaults

- Start with one-pass triage for the latest relevant messages.
- Default to draft-only mode unless user asks to send manually.
- Treat follow-up reminders as suggestions until confirmed.
- Escalate only when urgency criteria in `triage.md` are met.

## Optional Depth

If user needs more rigor, use:
- `triage.md` for message classification and urgency scoring
- `tracking.md` for commitment and follow-up workflows
- `templates.md` for response blocks by scenario
- `profiles.md` for behavior presets by role
- `feedback.md` for output review loops
