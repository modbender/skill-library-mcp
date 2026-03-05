# Entity Playbooks

## Person + Organization + Deal Chain

1. Search person by email/name.
2. Create organization if missing.
3. Create person and attach `org_id`.
4. Create deal and attach `person_id`, `org_id`, `pipeline_id`, `stage_id`.
5. Add activity and note.

## Activity-Driven Follow-Up

1. List open activities with date filters.
2. Group by assignee/user.
3. Update activities to done when completed.
4. Attach notes to person/deal/lead.

## Stage Movement Guardrails

1. Read deal before stage update.
2. Verify target stage belongs to intended pipeline.
3. Move stage.
4. Confirm changed timestamps and status.

## Destructive Action Guardrails

Before deleting records:

1. Retrieve and confirm record identity.
2. Capture key fields in local output/audit.
3. Execute delete.
4. Re-query to confirm deletion state.
