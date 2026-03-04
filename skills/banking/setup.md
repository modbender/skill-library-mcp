# Setup - Banking

Read this when `~/banking/` is missing or empty.

## Your Attitude

Be calm, exact, and operationally conservative. Optimize for safe execution, clear ownership, and fast recovery when things go wrong.

## Priority Order

### 1. First: Integration

In the first exchanges, define activation boundaries so this skill triggers in the right banking situations.

- Ask which banking topics should trigger this skill automatically.
- Ask whether to activate proactively for fraud and payment incidents.
- Ask where it should remain inactive and defer to another workflow.

### 2. Then: Capture Operating Context

Collect only context required for accurate guidance.

- Jurisdiction and regulatory environment.
- Customer type (consumer, SMB, enterprise) and account types in scope.
- Supported payment rails and cutoff windows.
- Approval thresholds, dual-control policies, and escalation contacts.

### 3. Finally: Response Preferences

Capture response style preferences that improve reliability.

- Preferred detail level for procedures and checklists.
- Incident posture: speed-first, precision-first, or balanced.
- Escalation style: immediate handoff or staged triage summary first.
- Communication tone preferences for customer-facing updates.

## What to Capture Internally

Keep concise notes in `~/banking/memory.md` and refresh after meaningful changes.

- Activation boundaries and do-not-activate contexts.
- Jurisdiction, account scope, and policy constraints.
- Approved payment controls and known failure points.
- Incident patterns with containment outcomes.
- Customer communication templates that were accepted by stakeholders.
