# Memory model

## Files

Store under `<workspace>/memory/`:

- `events.jsonl` — episodic events (append-only)
- `semantic.jsonl` — durable facts/preferences
- `procedural.jsonl` — workflows/checklists
- `self_model.jsonl` — stable identity and behavior constraints
- `consolidation-log.jsonl` — promotion/contradiction logs
- `ledger.jsonl` — integrity receipts (`prev_hash`, `entry_hash`, `chain_hash`)
- `onchain-anchors.jsonl` — optional date-to-tx mapping

## Entry envelope

Use this minimum structure for all layer entries:

```json
{
  "id": "uuid",
  "ts": "ISO-8601 UTC",
  "type": "events|semantic|procedural|self_model",
  "source": "agent|tool|manual|cron",
  "importance": 0.0,
  "tags": ["..."],
  "content": "...",
  "status": "active"
}
```

## Integrity receipts

For each appended entry:

- `entry_hash = sha256(canonical_json(entry_without_hash_fields))`
- `prev_hash = previous ledger chain_hash` (or `GENESIS`)
- `chain_hash = sha256(prev_hash + entry_hash)`

Append this to `ledger.jsonl`:

```json
{
  "ts": "ISO-8601 UTC",
  "entry_id": "uuid",
  "layer": "events",
  "entry_hash": "...",
  "prev_hash": "...",
  "chain_hash": "..."
}
```

## Consolidation policy

Run at least daily:

- Promote repeated events to semantic facts.
- Promote repeated actionable sequences to procedural entries.
- Promote stable behavior constraints to self_model.
- Never remove original events.
- Log contradictions with `status: flagged` in `consolidation-log.jsonl`.

## Consistency policy

- Append-only is mandatory.
- If an update is superseded, append a new row (`status: superseded`) and reference old `id`.
- Keep user-visible summaries short; keep evidence in memory files.
