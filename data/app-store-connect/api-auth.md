# API Authentication — App Store Connect

## Prerequisites

1. **Apple Developer Account** with Admin or App Manager role
2. **API Key** created in App Store Connect > Users and Access > Keys
3. **Private Key** (.p8 file) downloaded when key was created

## Creating an API Key

1. Go to [App Store Connect](https://appstoreconnect.apple.com)
2. Users and Access > Keys > App Store Connect API
3. Click "+" to generate new key
4. Select role (Admin for full access, App Manager for app-specific)
5. Download .p8 file immediately (only available once)
6. Note the Key ID and Issuer ID

## JWT Token Generation

App Store Connect uses JWT (JSON Web Tokens) signed with ES256.

### Token Structure

```json
{
  "alg": "ES256",
  "kid": "YOUR_KEY_ID",
  "typ": "JWT"
}
```

### Payload

```json
{
  "iss": "YOUR_ISSUER_ID",
  "iat": 1234567890,
  "exp": 1234568190,
  "aud": "appstoreconnect-v1"
}
```

- `iat`: Issued at (current Unix timestamp)
- `exp`: Expiration (max 20 minutes from iat)
- `aud`: Always "appstoreconnect-v1"

### Generate with Ruby

```ruby
require 'jwt'
require 'openssl'

# Uses environment variables: ASC_ISSUER_ID, ASC_KEY_ID, ASC_PRIVATE_KEY_PATH
private_key = OpenSSL::PKey::EC.new(File.read(ENV['ASC_PRIVATE_KEY_PATH']))

payload = {
  iss: ENV['ASC_ISSUER_ID'],
  iat: Time.now.to_i,
  exp: Time.now.to_i + 1200, # 20 minutes
  aud: 'appstoreconnect-v1'
}

token = JWT.encode(payload, private_key, 'ES256', { kid: ENV['ASC_KEY_ID'] })
puts token
```

### Generate with Python

```python
import jwt
import time
import os

# Uses environment variables: ASC_ISSUER_ID, ASC_KEY_ID, ASC_PRIVATE_KEY_PATH
with open(os.environ['ASC_PRIVATE_KEY_PATH'], 'r') as f:
    private_key = f.read()

payload = {
    'iss': os.environ['ASC_ISSUER_ID'],
    'iat': int(time.time()),
    'exp': int(time.time()) + 1200,
    'aud': 'appstoreconnect-v1'
}

headers = {
    'kid': os.environ['ASC_KEY_ID'],
    'typ': 'JWT'
}

token = jwt.encode(payload, private_key, algorithm='ES256', headers=headers)
print(token)
```

### Generate with Node.js

```javascript
const jwt = require('jsonwebtoken');
const fs = require('fs');

// Uses environment variables: ASC_ISSUER_ID, ASC_KEY_ID, ASC_PRIVATE_KEY_PATH
const privateKey = fs.readFileSync(process.env.ASC_PRIVATE_KEY_PATH);

const token = jwt.sign({
  iss: process.env.ASC_ISSUER_ID,
  iat: Math.floor(Date.now() / 1000),
  exp: Math.floor(Date.now() / 1000) + 1200,
  aud: 'appstoreconnect-v1'
}, privateKey, {
  algorithm: 'ES256',
  header: { kid: process.env.ASC_KEY_ID, typ: 'JWT' }
});

console.log(token);
```

## Making API Requests

```bash
JWT="your_generated_token"

# List all apps
curl -H "Authorization: Bearer $JWT" \
     "https://api.appstoreconnect.apple.com/v1/apps"

# Get specific app
curl -H "Authorization: Bearer $JWT" \
     "https://api.appstoreconnect.apple.com/v1/apps/YOUR_APP_ID"
```

## Role Permissions

| Role | Apps | Users | Finance | Reports |
|------|------|-------|---------|---------|
| Admin | Full | Full | Full | Full |
| App Manager | Full | None | None | App-level |
| Developer | Read | None | None | None |
| Marketing | Metadata | None | None | App-level |
| Sales | None | None | Read | Full |

## Token Best Practices

1. **Short expiration** - Generate new tokens frequently (every 15-20 min)
2. **Secure storage** - Never commit .p8 file to version control
3. **Environment variables** - Store credentials in env vars, not code
4. **Key rotation** - Rotate API keys periodically
5. **Minimal permissions** - Use role with least required access

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| 401 Unauthorized | Invalid/expired JWT | Regenerate token |
| 403 Forbidden | Insufficient role permissions | Use key with higher role |
| NOT_AUTHORIZED | Key revoked or team access removed | Check key status in ASC |
