# Adapter: Tracker Generic

Use for non-GitHub task trackers (kanban, ticketing, docs trackers).

## Capabilities
- Create/update task status records.
- Sync phase state, owners, blockers, and due checkpoints.
- Attach evidence links to tracker items.

## Auth
- Require valid account/session/token for selected tracker.
- Require minimum read/write permission to target board/project.
- Detect missing auth by failed create/update/read checks.
- On auth failure: continue local hub tracking and request tracker authorization path.

## Inputs
- Tracker type and project/board identifier.
- Mapping between phase tasks and tracker entities.
- Status and owner conventions.

## Outputs
```yaml
adapter_result:
  capability: tracker_generic
  status: ok|partial|failed
  references: [ticket_or_card_refs]
  notes: string
```

## Failure and Fallback
- If tracker write fails: keep local hub as source of truth and queue sync operations.
- If tracker unavailable: run without external tracker and include sync debt in closeout.
