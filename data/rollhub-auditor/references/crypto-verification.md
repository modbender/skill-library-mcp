# Cryptographic Verification — Full Technical Breakdown

## Provably Fair System Architecture

Agent Casino uses a commit-reveal scheme with SHA3-384 hashing and AES-256-CTR for result generation.

## Phase 1: Commitment (Before Bet)

1. Server generates random `server_seed` (256-bit)
2. Server computes `server_seed_hash = SHA3-384(server_seed)`
3. Hash is published to the client BEFORE the bet is placed
4. Client provides `client_seed` (user-controlled) and `nonce` (incrementing counter)

**Why this matters:** The server commits to the seed via its hash. It cannot change the seed after seeing the client's input without invalidating the hash.

## Phase 2: Result Generation

```
combined_input = server_seed || client_seed || nonce
key = SHA-256(combined_input)        # 256-bit AES key
cipher = AES-256-CTR(key, iv=0)
raw_bytes = cipher.encrypt(0x00 * 32)  # Encrypt 32 zero bytes
```

### For Dice (0-99):
```
result = (raw_bytes[0:4] as uint32) % 10000 / 100.0
```

### For Coinflip:
```
result = raw_bytes[0] % 2  # 0 = tails, 1 = heads
```

## Phase 3: Verification (After Bet)

1. Server reveals `server_seed`
2. Verifier checks: `SHA3-384(server_seed) == server_seed_hash`
3. Verifier re-computes result using the same algorithm
4. Verifier confirms result matches what the server reported

## Why SHA3-384?

- SHA3 family (Keccak) — not vulnerable to length extension attacks
- 384-bit output — 192-bit collision resistance
- NIST standardized — widely audited

## Why AES-256-CTR?

- Deterministic: same key + counter = same output
- Fast and well-studied
- CTR mode acts as a CSPRNG when keyed with unique input
- No padding issues (stream cipher mode)

## Security Properties

| Property | Guarantee |
|----------|-----------|
| Server can't predict client seed | Client controls their seed |
| Server can't change outcome | Hash commitment locks server seed |
| Client can't predict outcome | Server seed is unknown until reveal |
| Both parties can verify | All inputs revealed post-bet |
| Third parties can audit | All verification data is public |

## Verification Code (Python)

```python
import hashlib
from Crypto.Cipher import AES
import struct

def verify_provably_fair(server_seed: str, server_seed_hash: str, 
                          client_seed: str, nonce: int, 
                          claimed_result: float, game: str) -> dict:
    # Step 1: Verify commitment
    computed_hash = hashlib.sha3_384(server_seed.encode('utf-8')).hexdigest()
    hash_valid = computed_hash == server_seed_hash
    
    # Step 2: Derive result
    combined = f"{server_seed}{client_seed}{nonce}"
    key = hashlib.sha256(combined.encode('utf-8')).digest()
    cipher = AES.new(key, AES.MODE_CTR, nonce=b'\x00' * 8)
    raw = cipher.encrypt(b'\x00' * 32)
    
    if game == 'dice':
        value = struct.unpack('>I', raw[0:4])[0]
        result = (value % 10000) / 100.0
    elif game == 'coinflip':
        result = raw[0] % 2
    else:
        result = None
    
    result_valid = abs(result - claimed_result) < 0.01 if result is not None else None
    
    return {
        'hash_valid': hash_valid,
        'computed_hash': computed_hash,
        'computed_result': result,
        'result_valid': result_valid,
        'tampered': not hash_valid or not result_valid
    }
```

## Verification Code (JavaScript)

```javascript
const crypto = require('crypto');

function verifyBet(serverSeed, serverSeedHash, clientSeed, nonce, claimedResult, game) {
  // Verify hash commitment
  const computedHash = crypto.createHash('sha3-384').update(serverSeed).digest('hex');
  const hashValid = computedHash === serverSeedHash;
  
  // Derive result
  const combined = `${serverSeed}${clientSeed}${nonce}`;
  const key = crypto.createHash('sha256').update(combined).digest();
  const cipher = crypto.createCipheriv('aes-256-ctr', key, Buffer.alloc(16, 0));
  const raw = cipher.update(Buffer.alloc(32, 0));
  
  let result;
  if (game === 'dice') {
    result = (raw.readUInt32BE(0) % 10000) / 100.0;
  } else if (game === 'coinflip') {
    result = raw[0] % 2;
  }
  
  return {
    hashValid,
    computedResult: result,
    resultValid: Math.abs(result - claimedResult) < 0.01,
    tampered: !hashValid || Math.abs(result - claimedResult) >= 0.01
  };
}
```
