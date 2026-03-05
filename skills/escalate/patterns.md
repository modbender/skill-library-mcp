# Pattern Recognition

How to detect autonomy grants and track escalation learning.

## Autonomy Signals

Phrases that indicate potential delegation:

| Signal | Confidence | Action |
|--------|------------|--------|
| "You decide" | Medium | Note as 1x observation |
| "Your call" | Medium | Note as 1x observation |
| "Just do it" | Medium | Note as 1x observation |
| "Handle it" | Medium | Note as 1x observation |
| "I trust you on this" | High | Note, consider pattern after 1 more |
| "Don't ask me about X" | Very high | Propose immediate confirmation |
| "Always do X" | Explicit | Confirm and lock |

## Pattern Formation

```
1 signal  → observed (don't assume)
2 signals → pattern (propose confirmation)
confirmed → apply autonomy
locked    → never re-ask
```

## Context Matching

Same category ≠ same context. Match on:
- **Action type:** "refactor" vs "delete" (different risk)
- **Scope:** single file vs entire codebase
- **Reversibility:** can undo vs permanent
- **Stakes:** dev environment vs production

A pattern in "refactor small functions" doesn't grant autonomy for "refactor entire architecture."

## Confirmation Prompt

After detecting a pattern:

```
I've noticed you've delegated [category] decisions twice now.
Should I handle [category] autonomously going forward?

- Yes → I'll decide without asking
- No → I'll keep checking with you
- Sometimes → Tell me when to ask vs decide
```

## Demotion Triggers

Reduce trust level if:
- User overrides an autonomous decision
- User expresses surprise at an action taken
- User adds constraints that weren't there before
- Context changed significantly

**Response to demotion:** Don't apologize excessively. Simply say: "Got it, I'll check with you on [category] going forward."
