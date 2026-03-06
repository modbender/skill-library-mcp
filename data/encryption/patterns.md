# Encryption Code Patterns

## Password Hashing

### Node.js (bcrypt)
```javascript
const bcrypt = require('bcrypt');
const COST = 12;

// Hash
const hash = await bcrypt.hash(password, COST);

// Verify
const valid = await bcrypt.compare(password, hash);
```

### Python (argon2)
```python
from argon2 import PasswordHasher
ph = PasswordHasher()

# Hash
hash = ph.hash(password)

# Verify
try:
    ph.verify(hash, password)
except VerifyMismatchError:
    return False
```

## Secure Token Generation

### Node.js
```javascript
const crypto = require('crypto');
const token = crypto.randomBytes(32).toString('hex');
```

### Python
```python
import secrets
token = secrets.token_hex(32)
```

## Field-Level Database Encryption

### Envelope pattern (Node + AWS KMS)
```javascript
const { KMS } = require('@aws-sdk/client-kms');
const crypto = require('crypto');

async function encryptField(plaintext, kmsKeyId) {
  // Generate DEK
  const dek = crypto.randomBytes(32);
  const iv = crypto.randomBytes(16);
  
  // Encrypt data with DEK
  const cipher = crypto.createCipheriv('aes-256-gcm', dek, iv);
  const encrypted = Buffer.concat([cipher.update(plaintext), cipher.final()]);
  const tag = cipher.getAuthTag();
  
  // Encrypt DEK with KMS
  const kms = new KMS();
  const { CiphertextBlob } = await kms.encrypt({
    KeyId: kmsKeyId,
    Plaintext: dek
  });
  
  return {
    encryptedData: encrypted.toString('base64'),
    encryptedDek: Buffer.from(CiphertextBlob).toString('base64'),
    iv: iv.toString('base64'),
    tag: tag.toString('base64')
  };
}
```

## JWT with RS256

```javascript
const jwt = require('jsonwebtoken');
const fs = require('fs');

const privateKey = fs.readFileSync('private.pem');
const publicKey = fs.readFileSync('public.pem');

// Sign
const token = jwt.sign({ userId: 123 }, privateKey, {
  algorithm: 'RS256',
  expiresIn: '1h',
  keyid: 'key-2024-01'  // For rotation
});

// Verify
const decoded = jwt.verify(token, publicKey, {
  algorithms: ['RS256']
});
```

## Key Rotation (Zero Downtime)

```javascript
// Support multiple active keys
const KEYS = {
  'v2': { key: process.env.KEY_V2, active: true },
  'v1': { key: process.env.KEY_V1, active: false }  // Grace period
};

function encrypt(data) {
  const activeKey = Object.entries(KEYS).find(([_, v]) => v.active);
  return {
    keyVersion: activeKey[0],
    data: doEncrypt(data, activeKey[1].key)
  };
}

function decrypt({ keyVersion, data }) {
  const key = KEYS[keyVersion]?.key;
  if (!key) throw new Error('Unknown key version');
  return doDecrypt(data, key);
}
```

## Progressive Password Rehashing

```javascript
async function verifyAndUpgrade(password, hash) {
  // Try modern algorithm first
  if (hash.startsWith('$argon2')) {
    return argon2.verify(hash, password);
  }
  
  // Legacy: verify with old algorithm
  if (hash.startsWith('$2')) {  // bcrypt
    const valid = await bcrypt.compare(password, hash);
    if (valid) {
      // Upgrade to argon2 on successful login
      const newHash = await argon2.hash(password);
      await updateUserHash(userId, newHash);
    }
    return valid;
  }
  
  throw new Error('Unknown hash format');
}
```
