# Routing Rules

## Goal

Auto-assign every message/action to the correct topic with minimal user interruption.

## Confidence policy

Only ask the user to pick a topic when **all** are true:

- Confidence < 0.70
- No active topic in the last few turns
- No strong keyword match

If you must ask:

- Ask one short question.
- Offer 2–4 topic options.
- Save the answer as a routing rule (keyword/context -> topic).

## Signals

1. **Recency**: If a topic was active in the last N turns, prefer it.
2. **Keywords**: Match project names, systems, or people to known topics.
3. **Task overlap**: If a task matches the message, use its topic.
4. **Agent lane**: Subagent identity can bias routing (e.g., coding -> Clawboard topic).

## Examples

- “Deploy trading changes” -> Trading Systems
- “Call the insurer” -> Ops/Admin/Finance
- “Add a new client site task” -> Legacy Clients
- “Fix Clawboard UI” -> Clawboard
