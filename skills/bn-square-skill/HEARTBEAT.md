# HEARTBEAT

Runtime checklist for `bn-square-skill`.

## When to Run

- Run this checklist at the beginning of each publish task.
- If long-running workflow (>10 minutes), run session check again before publish.

## Health Sequence

1. **Config check**
   - Verify required env keys exist:
     - `BINANCE_COOKIE_HEADER`
     - `BINANCE_CSRF_TOKEN`
2. **Session validation**
   - Call `validate_session`.
   - If `valid=false`, stop and return recovery instructions.
3. **Publish readiness**
   - Validate payload constraints:
     - `content` must be non-empty.
     - `poll` and `imageUrls` cannot both be set.
4. **Post-publish confirmation**
   - Call `get_post_status` with returned `postId`.
   - If status is `pending_review`, return that status explicitly.

## Failure Policy

1. Never retry infinitely.
2. Use bounded retries only for transient network errors.
3. Stop immediately on auth/session errors.
4. Never leak sensitive auth values in error text.

## Output Policy

Always return structured JSON-compatible output with:

- `success` or `valid` status
- identifiers (`postId`, `postUrl`) when available
- sanitized `error` when failed
