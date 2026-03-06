# Algorithm Traps

## Algorithm Confusion Attack

- Token says `alg: HS256`, server uses RS256 key as HMAC secret—forged token validates
- NEVER use token's `alg` header to select algorithm—server must enforce
- `algorithms: ['RS256']` in verify options—explicit allowlist
- Some libraries default to trusting header—check your library

## HS256 Traps

- Same secret for sign and verify—if verify key leaks, attacker can forge
- Secret must be 256+ bits—short secrets brute-forceable
- Secret in environment variable—not in code
- Rotating secret invalidates ALL existing tokens instantly

## RS256/ES256 Traps

- Private key signs, public key verifies—don't swap
- Public key can be shared—but attackers knowing it doesn't help them forge
- Key length matters: RSA 2048 minimum, 4096 recommended
- ECDSA (ES256) has smaller signatures—better for size-constrained cases

## `none` Algorithm Attack

- `alg: none` + no signature = unsigned token accepted by vulnerable libraries
- Most modern libraries reject by default—but verify yours
- Never allow `none` in algorithm allowlist
- Test by sending `alg: none` token to your service

## Key ID Traps

- `kid` header identifies which key—useful for rotation
- `kid` is untrusted input—validate against known key IDs
- Missing `kid` should use default—not error for backwards compatibility
- JWKS endpoint must be over HTTPS—attacker could inject keys

## Key Confusion

- Using private key for verification—different behavior than expected
- RSA vs ECDSA key format different—loading wrong type fails silently or oddly
- PEM vs JWK format—libraries handle both but not interchangeably
