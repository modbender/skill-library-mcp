# Response Workflows

## Response Types

| Type | When to Use | Automation Level |
|------|-------------|------------------|
| **Pre-approved auto-send** | FAQ answers, link requests | Fully automated |
| **Draft for approval** | Routine but personalized | One-click approve/edit |
| **Holding response** | Can't respond fully yet | "Received, will review by X" |
| **Full compose** | Complex/sensitive | User writes |

## Pre-Approved Templates

Create templates for recurring patterns:
- "What tools do you use?"
- "Can you make an intro to X?"
- "How do I get started with Y?"
- Meeting confirmations
- Receipt acknowledgments

**Template variables:**
- `{sender_name}` — from address book
- `{original_topic}` — extracted from thread
- `{my_availability}` — from calendar
- `{relevant_link}` — from knowledge base

## Draft Generation Rules

When drafting responses:
1. **Match sender's tone** — Formal begets formal, casual begets casual
2. **Reference history** — "As we discussed last month..." when applicable
3. **Keep it short** — Draft the minimum viable response
4. **Highlight uncertainty** — "[VERIFY: Is this the right link?]" for agent uncertainty

## Holding Response Strategy

When user can't respond fully:
- Acknowledge receipt
- Set expectation: "Will review by [reasonable date]"
- Buy time without dropping the ball

Example: "Got it — tied up this week but will have a proper response by Friday. Ping me if anything's urgent before then."

## Batch Response Sessions

For high-volume inboxes:
1. Group similar items (intro requests, meeting asks, questions)
2. Present as batch: "7 intro requests this week"
3. Enable rapid-fire: approve/decline/edit each in <10 seconds
4. Send all at once when batch complete

## Scope Creep Detection

Before drafting response to requests:
1. Check if ask falls outside defined scope/agreement
2. Flag: "This appears to be new scope — charge accordingly?"
3. Draft boundary response if confirmed: "Happy to help with X — let me scope that separately"
