# Safety Checklist - Apple Maps (MacOS)

Apply this checklist before search, route, and share actions.

## Pre-Action Checks

1. Confirm exact query intent (place, category, or route).
2. Confirm location context for ambiguous queries.
3. Confirm whether generated URL contains sensitive text.
4. For routes, confirm origin, destination, and route mode.
5. For multiple link launches, show count and collect explicit confirmation.
6. For external sharing, require explicit user approval.

## Post-Action Checks

1. Confirm the launched URL matches the intended query.
2. Confirm expected result state (search term, destination, route mode).
3. If mismatch occurs, stop and present corrected URL options.

## Bulk Action Guardrails

- Default to opening one result at a time.
- Require a second explicit confirmation before opening more than one map link.
- Record high-impact confirmations in local safety notes.
