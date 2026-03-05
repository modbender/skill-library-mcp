# Smart Suggestions — Observation & Status Tracking

Wayve observes patterns in the user's life and stores suggestions. What happens after `accepted` is not Wayve's concern — the AI handles it independently, outside of Wayve.

## A. When to Save Observations

Create smart suggestions at these moments:

### Wrap Up (Sunday)
After reviewing the week, check:
- Bucket consistently at 0% completion → suggest making time for it
- Same activity carried over 3+ weeks → suggest dropping, delegating, or restructuring
- Energy pattern: draining activities scheduled at peak hours → suggest rescheduling
- Recurring blocker mentioned again → suggest a structural change
- Mood/energy declining trend → suggest recovery week or adjusting commitments

### Fresh Start (Monday)
When planning the new week, check:
- Overcommitting again (planned > available) → suggest lighter load
- Same bucket neglected again → suggest scheduling it first
- Carryovers from same bucket again → suggest different approach
- No variety in activities → suggest mixing it up

### Life Audit
During comprehensive review:
- Delegation candidates from energy-skill matrix → suggest offloading
- Happiness correlations not being acted on → suggest making time for happiness drivers
- Long-term bucket imbalance → suggest rebalancing
- Frequency targets consistently missed → suggest adjusting targets or scheduling

### Analytics / Any Conversation
When patterns emerge organically:
- User mentions the same frustration for the 3rd time → suggest addressing it structurally
- Time audit reveals time sink → suggest elimination or batching
- Producer score dropping consistently → suggest simplifying the week

### Checking Pending Suggestions
At the start of wrap-up and fresh-start, also check for pending/snoozed suggestions:
```
wayve_manage_smart_suggestions(action: "list", status_filter: "pending")
```
If snoozed suggestions have passed their `snoozed_until` date, they're relevant again.

## B. Your Capabilities

When creating a suggestion, the `proposal` field describes what could be done. Here's what's within your reach:

- **Cron job**: schedule a recurring check-in or reminder (always requires explicit user approval before creation)
- **Direct action**: make the change right now (reschedule, create activity, update settings) — only using `wayve_*` tools
- **Simple suggestion**: just tell the user what you noticed and let them decide
- **Nothing**: sometimes the observation is enough — awareness without action

The `proposal` is free text — describe what you'd do. All actions are limited to Wayve tools (`wayve_*`) and cron jobs for notifications.

## C. Presentation

When presenting suggestions to the user:

- **Max 2 per session** — don't overwhelm. Pick the most impactful ones.
- **Conversational, not mechanical** — weave them into the flow naturally. "I've noticed X happening for a few weeks now. Want me to Y?"
- **User chooses** — always let them accept, dismiss, or snooze. Never auto-implement.
- **If dismissed, respect it** — don't bring it up again unless the pattern gets significantly worse.
- **If snoozed, resurface later** — check `snoozed_until` date in future sessions.

## D. After Acceptance

Once a suggestion is `accepted`, Wayve's role is done. The status is tracked, and the AI works with the user on implementation — iteratively, outside of Wayve's suggestion system. Don't create follow-up suggestions for accepted ones; the work happens in conversation.
