# Common Attacks and Mitigations

## Algorithm Confusion

- **Attack:** Change `alg` from RS256 to HS256, sign with public key
- **Why it works:** Server uses public key as HMAC secret
- **Mitigation:** Never trust `alg` header—enforce expected algorithm server-side

## None Algorithm

- **Attack:** Set `alg: none`, remove signature entirely
- **Why it works:** Some libraries accept unsigned tokens
- **Mitigation:** Reject `none` explicitly, test your library

## Token Theft via XSS

- **Attack:** XSS steals token from localStorage or JavaScript variable
- **Why it works:** JavaScript can read non-httpOnly storage
- **Mitigation:** httpOnly cookie, or accept risk with short expiry + refresh rotation

## Token Theft via MITM

- **Attack:** Intercept token over non-HTTPS connection
- **Why it works:** Token sent in clear text
- **Mitigation:** HTTPS only, HSTS, never send token over HTTP

## Replay Attack

- **Attack:** Captured valid token reused by attacker
- **Why it works:** JWT valid until expiry, no way to detect replay
- **Mitigation:** Short expiry, bind to client (IP/fingerprint), one-time tokens for critical ops

## CSRF with Cookie

- **Attack:** Malicious site triggers request, browser sends cookie automatically
- **Why it works:** Cookies attach to requests regardless of origin
- **Mitigation:** SameSite=Strict, CSRF token in header, verify Origin

## Brute Force Secret

- **Attack:** Try common passwords as HS256 secret
- **Why it works:** Weak secrets are guessable
- **Mitigation:** 256+ bit random secret, rate limit, monitor for attempts

## Payload Tampering

- **Attack:** Modify payload, hope server doesn't verify
- **Why it works:** Only if server decodes without verify
- **Mitigation:** Always verify signature BEFORE trusting claims

## Key Confusion in JWKS

- **Attack:** Register malicious public key in JWKS endpoint
- **Why it works:** Server accepts attacker's key
- **Mitigation:** JWKS over HTTPS only, validate `kid` against allowlist
