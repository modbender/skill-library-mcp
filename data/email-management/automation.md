# Automation Boundaries - Email Management

Automation should reduce inbox friction without sending unintended communication.

## Allowed by Default

- Categorize new messages into Action, Waiting, FYI, Noise.
- Suggest drafts for common scenarios.
- Propose follow-up reminders with due dates.
- Build inbox summaries and highlight bottlenecks.

## Requires Explicit Approval

- Sending any message to external recipients.
- Auto-forwarding messages.
- Changing external mailbox rules.
- Enabling recurring reminders or scheduled digests.

## Draft Safety Checks

Before presenting a draft, verify:
- recipient is correct
- objective is explicit
- next step has owner and date
- tone matches audience
- no sensitive data is leaked

## Escalation Logic

Escalate immediately when:
- a committed deadline is already missed
- stakeholder risk is high and unresolved
- the thread has repeated unanswered asks

Otherwise keep notifications batched.
