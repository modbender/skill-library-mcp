# Token Lifecycle Traps

## Expiration Traps

- No `exp` claim = token valid forever—always set expiration
- `exp` is seconds since epoch, not milliseconds—common mistake
- Clock skew between servers—allow 30-60s tolerance
- Token valid until `exp` even after password change—revocation needed

## Refresh Token Traps

- Long-lived refresh token = high value target—store more securely than access token
- Refresh token rotation: issue new on each use, invalidate old
- Stolen refresh token without rotation = unlimited access
- Refresh endpoint should be rate-limited—attacker tries stolen token

## Revocation Traps

- JWTs are stateless—can't truly revoke without server-side state
- Blacklist approach: check token ID against revoked list—adds latency
- Short expiry + refresh mitigates—but gap between revoke and expiry exists
- User logout should invalidate refresh token—not just delete client-side

## Issuance Traps

- `iat` claim for issued-at—useful for "tokens before this date invalid"
- Replay attack: captured token reused—short expiry limits window
- Token per device vs single token—security vs UX tradeoff
- Re-authentication for sensitive ops—don't rely on old token

## Session Management Traps

- Multiple devices = multiple tokens—revoking one shouldn't revoke all (or should it?)
- "Log out everywhere" needs server-side tracking
- Session identifier in token vs token ID—different revocation granularity
- Background refresh before expiry—or user sees expiration mid-action

## Storage Lifecycle Traps

- httpOnly cookie survives page refresh—localStorage too but XSS-vulnerable
- Memory-only = lost on refresh—re-auth or use refresh token
- Cookie expiry independent of JWT expiry—can mismatch
- Clear on logout: cookie + localStorage + memory—all three
