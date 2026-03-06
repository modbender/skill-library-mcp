---
name: summary-generator
description: "Generate daily or range-based lead summaries from read-only lead data. Use when users ask for todays lead summary, broker inventory counts, locality trends, or priority bucket breakdown for human review and downstream action suggestion. Recommended chain: sentiment-priority-scorer then summary-generator then action-suggester. Do not use for ingestion, extraction, storage writes, or outbound communication."
---

# Summary Generator

Build concise daily lead summaries from read-only lead records.

## Quick Triggers

- Give me today's lead summary with trends.
- Show high-priority lead counts by location.
- Summarize broker inventory vs buyer requirements for this week.

## Recommended Chain

`sentiment-priority-scorer -> summary-generator -> action-suggester`

## Execute Workflow

1. Accept a date-range request from Supervisor.
2. Validate request with `references/summary-input.schema.json`.
3. Query lead storage using read-only access.
4. Aggregate summary metrics, including:
   - `new_leads_count`
   - `trends`
   - `record_type_breakdown` (`inventory_listing`, `buyer_requirement`)
   - `priority_breakdown` (`P1`, `P2`, `P3`)
   - `urgency_breakdown` (`high`, `medium`, `low`)
   - `top_localities` (top volume areas with counts)
   - `dataset_mode` echoed from request or inferred from source
5. Validate output with `references/summary-output.schema.json`.
6. Return only the validated summary object.

## Enforce Boundaries

- Never parse chat dumps.
- Never extract new leads from messages.
- Never write or mutate storage.
- Never suggest or execute follow-up actions.
- Never send reports directly to external systems.

## Handle Errors

1. Return explicit query or validation failure reasons.
2. Return zero-valued metrics when no leads exist in the requested range.
3. Fail closed when read permissions are absent.
