# Validation Traps

## Signature Verification Traps

- Decode without verify = reading claims without checking authenticity—useless for auth
- Verify with wrong key = invalid signature for valid token—check key first
- Algorithm must be enforced server-side—never trust token's `alg` claim
- Empty signature with `alg: none`—reject explicitly

## Time Claim Traps

- `exp` in past = expired—but clock skew causes false rejections
- `nbf` (not before) in future = not yet valid—less common but exists
- `iat` too far in past = suspicious—policy decision
- All time claims in seconds, not milliseconds—easy mistake

## Audience/Issuer Traps

- Missing `aud` check = token for Service A works on Service B
- `aud` can be string or array—handle both
- `iss` must match expected issuer exactly—including trailing slash
- Multiple issuers (federated auth) need explicit allowlist

## Claims Validation Traps

- `sub` (subject) exists but user deleted—check user still valid
- Custom claims untrusted like any input—validate/sanitize
- Nested claims need deep validation—don't assume structure
- Claim exists but empty string—truthy check passes, validation fails

## Error Handling Traps

- Don't reveal why validation failed—"invalid token" not "wrong issuer"
- Expired vs invalid = same HTTP 401—don't distinguish for attacker
- Logging token = logging credential—mask or hash in logs
- Catch library-specific exceptions—each throws differently

## Order of Operations Traps

- Decode claims BEFORE verify = acting on unsigned data
- Verify first, then check claims—signature proves claims unmodified
- Database lookup with unverified `sub`—attacker controls lookup
- Rate limit before validation—expensive verify is DoS vector
