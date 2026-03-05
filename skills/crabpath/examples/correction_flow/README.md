# Correction Flow for Any Agent Framework

Wrong answer correction usually happens too late to directly use the exact fired path from the query that failed.
Corrections were tied only to user-visible output, so a delay of a minute or a retry path often loses the right target nodes.

The fix is simple:

1. Log fired nodes per conversation at query time.
2. On correction, load the latest matching fired nodes by `chat_id`.
3. Penalize those fired nodes immediately and optionally inject a `CORRECTION` node.

`correct.py` and `learn_correction.py` only handle `CORRECTION` nodes.
For `TEACHING` (new factual additions), use `crabpath inject --type TEACHING` directly.

## Example scripts

- `query_with_logging.py`
  - Loads `state.json`, runs a hash-embedding query, prints results.
  - If `--chat-id` is provided, appends a JSONL record to `<state_dir>/fired_log.jsonl`.
- `correct.py`
  - Reads `<state_dir>/fired_log.jsonl`, selects the latest `--lookback` entries for the chat.
  - Collects unique fired IDs and runs `apply_outcome` with `--outcome`.
  - Optionally injects a `CORRECTION` node with `--content`.

Both scripts use `hash` embeddings, so they run offline.

## Integration pattern for any framework

- After each assistant query, run `query_with_logging.py` with the current `chat_id`.
- If a user submits explicit negative feedback, run `correct.py` with the same `chat_id`.
- Keep `fired_log.jsonl` in the same directory as `state.json`.
- Persist injected corrections in `injected_corrections.jsonl` so your batch reconciliation logic can skip duplicates.
