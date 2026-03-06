# Standard Workflows

## Workflow 1: Automation Triage
- Inputs: automation id/name, expected behavior, timeframe.
- Steps:
  1. Confirm trigger event happened.
  2. Check conditions at trigger time.
  3. Review trace path.
  4. Isolate failing node.
  5. Propose minimal fix and test.
- Output: root cause + validation checklist.

## Workflow 2: New Automation Design
- Inputs: intent, constraints, fail-safe behavior.
- Steps:
  1. Define trigger and debounce.
  2. Define override helper.
  3. Select automation mode.
  4. Add timeout/error handling.
  5. Add observability points.
- Output: implementation blueprint.

## Workflow 3: Dashboard Refactor
- Inputs: target device (mobile/tablet/wall), primary user tasks.
- Steps:
  1. Prioritize top 5 actions.
  2. Design status hierarchy.
  3. Consolidate duplicate cards.
  4. Validate unavailable-state behavior.
- Output: cleaner navigation and card map.
