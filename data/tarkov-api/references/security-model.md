# Security Model (tarkov-api skill)

## Threats this skill mitigates

- Endpoint hijack or typo to malicious GraphQL host
- Oversized queries causing slowdowns/timeouts
- Blind trust in unvalidated external data
- Unsafe shell interpolation from user/API data
- Excessive raw-query usage without constraints
- Overconfidence in projected profit/risk models (flip and risk scores are heuristics)
- Treating community wiki edits as authoritative without cross-check

## Built-in controls in `scripts/tarkov_api.py`

1. **Endpoint allowlist by default**
   - Refuses non-`api.tarkov.dev` GraphQL endpoint unless `--allow-unsafe-endpoint` is explicitly set.
   - Refuses non-official EFT wiki API endpoint unless explicitly overridden.

2. **Limit clamping**
   - User limits are clamped into safe range (`1..100`).

3. **Timeout + retry policy**
   - Default timeout 20s.
   - Limited retries for transient failures.

4. **No shell execution**
   - Uses Python stdlib HTTP; does not pass data to shell commands.

5. **Structured variable handling**
   - Sends JSON payload (`query` + `variables`) instead of string-concatenated command pipelines.

## Operational guidance

- Keep `raw` mode for advanced, intentional use only.
- Prefer smallest viable limits (e.g., 5–25) for routine checks.
- Treat pricing/spawn data as dynamic snapshots, not guarantees.
- For automation: use bounded cron frequency and avoid high-rate polling.

## Red flags

Stop and review if you see:

- Endpoint changed away from `api.tarkov.dev`
- Responses with repeated parse errors or schema mismatch
- Large latency spikes and frequent retries
- User requests to run untrusted scripts “from API output”

## Safe fallback

If API is unstable:

1. Run `status` first.
2. Retry once with lower `--limit`.
3. Return a degraded response (“best effort snapshot”) and note uncertainty.
