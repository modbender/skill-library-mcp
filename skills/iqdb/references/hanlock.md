# hanLock Encoding Reference

**Package:** `hanlock`
**Purpose:** Password-based Hangul syllabic encoding (base-11172) for lightweight data privacy
**Dependencies:** None

## Overview

hanLock converts arbitrary data into Korean Hangul syllables using a password-derived transformation. The output looks like Korean text but encodes binary data. Useful for:

- Encoding sensitive data before on-chain storage
- Lightweight obfuscation without heavy crypto dependencies
- Compact encoding (base-11172 is denser than base64)

**Not a substitute for real encryption.** Suitable for obfuscation and casual privacy, not for protecting secrets against determined attackers.

## Install

```bash
npm install hanlock
```

## API

### `encodeWithPassword(plaintext: string, password: string): string`

Encode a string using a password. Output is a string of Hangul syllables (Unicode range U+AC00–U+D7A3).

```typescript
import { encodeWithPassword } from 'hanlock';

const encoded = encodeWithPassword('player inventory: sword, shield, potion', 'secret123');
// → "깁닣뭡섣엩죝칡킩..." (Hangul syllable string)
```

### `decodeWithPassword(encoded: string, password: string): string`

Decode a hanLock-encoded string back to plaintext.

```typescript
import { decodeWithPassword } from 'hanlock';

const plaintext = decodeWithPassword('깁닣뭡섣엩죝칡킩...', 'secret123');
// → "player inventory: sword, shield, potion"
```

Wrong password returns garbage, not an error.

## How It Works

1. Password → deterministic byte sequence via simple hash
2. Plaintext → byte array
3. XOR plaintext bytes with password-derived bytes (repeating)
4. Map resulting values to Hangul syllable block range (11,172 possible syllables)
5. Output: string of Korean characters

**Base-11172** — Each Hangul syllable encodes ~13.4 bits (vs base64's 6 bits per char). More compact.

## Integration with IQDB

```javascript
const { encodeWithPassword, decodeWithPassword } = require('hanlock');
const { createIQDB } = require('@iqlabsteam/iqdb');

const iqdb = createIQDB();

// Encode before writing (keep input short — encoding expands ~3x)
const encoded = encodeWithPassword('short secret', password);
await iqdb.writeRow('private_data', JSON.stringify({ payload: encoded }));

// Decode after reading
const rows = await iqdb.readRowsByTable({ userPubkey: 'YOUR_PUBKEY', tableName: 'private_data' });
const decoded = decodeWithPassword(rows[0].payload, password);
```

## Limitations

- XOR-based — not cryptographically secure. Do not use for passwords, keys, or PII.
- Password must be shared out-of-band between encoder and decoder.
- No integrity check — wrong password silently produces garbage.
- Unicode-dependent — ensure your storage/transport preserves Unicode correctly.
