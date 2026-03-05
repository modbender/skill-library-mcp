# Operations

## Write path (real-time)

Use:
- `scripts/capture_event.py`

Properties:
- deterministic
- append-only
- no network calls
- suitable for high-frequency updates

## Consolidation path (daily)

Use:
- `scripts/dream_cycle_budgeted.py --root <memory> --max-events 200 --max-semantic 20 --max-procedural 10 --max-self 5`

Budget knobs:
- `--max-events`
- `--max-semantic`
- `--max-procedural`
- `--max-self`

## Read path (fast first)

1) Read local files by priority (self/procedural/semantic/events)
2) Only query on-chain when auditing proofs

## Scheduling recommendation

- dream cycle: daily at off-peak time
- anchor: immediately after dream cycle
- optional midday mini-cycle: reduced caps

## Idempotency

Skip anchoring if same date + same ledger tip already anchored.
