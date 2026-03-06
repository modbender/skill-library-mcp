# API Documentation - AgentShield

> **Base URL:** `https://agentshield.live/api`

All endpoints return JSON unless otherwise specified.

---

## 🔐 Authentication

Most endpoints are **public** (read-only). Write operations require API key.

```bash
# Public endpoints (no auth required)
curl https://agentshield.live/api/verify/agent_abc123

# Authenticated endpoints (require API key)
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://agentshield.live/api/crl/revoke/cert_xyz
```

**Get API Key:** Contact ratgeberpro@gmail.com

---

## 📋 Registry Endpoints

### GET /api/registry/agents

List all certified agents in the public registry.

**Parameters:**
- `limit` (optional, default: 20) - Number of results per page (max 100)
- `offset` (optional, default: 0) - Pagination offset
- `tier` (optional) - Filter by tier: `UNVERIFIED`, `BASIC`, `VERIFIED`, `TRUSTED`

**Example Request:**
```bash
curl "https://agentshield.live/api/registry/agents?limit=10&offset=0"
```

**Example Response:**
```json
{
  "success": true,
  "total": 42,
  "limit": 10,
  "offset": 0,
  "agents": [
    {
      "agent_id": "agent_kalle_oc_2024",
      "public_key_hash": "ed25519:sha256:abc123...",
      "trust_score": 85,
      "tier": "TRUSTED",
      "verification_count": 12,
      "first_verified": "2026-02-10T14:30:00Z",
      "last_verified": "2026-02-26T10:15:00Z",
      "certificate_status": "valid",
      "revoked": false
    },
    // ... 9 more agents
  ]
}
```

**Response Fields:**
- `agent_id`: Unique agent identifier
- `public_key_hash`: Ed25519 public key hash (truncated)
- `trust_score`: Trust score (0-100)
- `tier`: Trust tier (UNVERIFIED/BASIC/VERIFIED/TRUSTED)
- `verification_count`: Number of successful verifications
- `first_verified`: First verification timestamp (ISO 8601)
- `last_verified`: Most recent verification timestamp
- `certificate_status`: `valid`, `expired`, or `revoked`
- `revoked`: Boolean revocation status

---

### GET /api/registry/search

Search agents by name, ID, or public key hash.

**Parameters:**
- `q` (required) - Search query
- `limit` (optional, default: 20)
- `offset` (optional, default: 0)

**Example Request:**
```bash
curl "https://agentshield.live/api/registry/search?q=kalle&limit=5"
```

**Example Response:**
```json
{
  "success": true,
  "query": "kalle",
  "total": 1,
  "agents": [
    {
      "agent_id": "agent_kalle_oc_2024",
      "trust_score": 85,
      "tier": "TRUSTED",
      "match_reason": "agent_id"
    }
  ]
}
```

**Match Reasons:**
- `agent_id` - Matched agent identifier
- `public_key_hash` - Matched public key hash
- `metadata` - Matched agent metadata (if available)

---

### GET /api/verify/:agent_id

Verify a specific agent's certificate status.

**Parameters:**
- `agent_id` (required, in URL) - Agent identifier

**Example Request:**
```bash
curl "https://agentshield.live/api/verify/agent_kalle_oc_2024"
```

**Example Response:**
```json
{
  "success": true,
  "agent_id": "agent_kalle_oc_2024",
  "verified": true,
  "certificate": {
    "issued": "2026-02-10T14:30:00Z",
    "expires": "2027-02-10T14:30:00Z",
    "public_key": "ed25519:AAAAC3NzaC1lZDI1NTE5AAAAI...",
    "fingerprint": "SHA256:abc123def456..."
  },
  "trust": {
    "score": 85,
    "tier": "TRUSTED",
    "verification_count": 12,
    "first_verified": "2026-02-10T14:30:00Z",
    "last_verified": "2026-02-26T10:15:00Z"
  },
  "crl_status": "valid",
  "revoked": false
}
```

**Response Fields:**
- `verified`: Boolean - agent has valid certificate
- `certificate`: Certificate metadata
  - `issued`: Issue timestamp
  - `expires`: Expiry timestamp
  - `public_key`: Ed25519 public key (full)
  - `fingerprint`: SHA256 fingerprint
- `trust`: Trust metrics
  - `score`: Trust score (0-100)
  - `tier`: Trust tier
  - `verification_count`: Number of verifications
- `crl_status`: CRL check result (`valid`, `revoked`, `unknown`)
- `revoked`: Boolean revocation status

---

## 🚫 CRL (Certificate Revocation List) Endpoints

### GET /api/crl/check/:id

Check if a certificate is revoked.

**Parameters:**
- `id` (required, in URL) - Certificate ID or agent ID

**Example Request:**
```bash
curl "https://agentshield.live/api/crl/check/agent_kalle_oc_2024"
```

**Example Response (Valid):**
```json
{
  "success": true,
  "id": "agent_kalle_oc_2024",
  "revoked": false,
  "status": "valid",
  "checked_at": "2026-02-26T18:30:00Z"
}
```

**Example Response (Revoked):**
```json
{
  "success": true,
  "id": "agent_compromised_123",
  "revoked": true,
  "status": "revoked",
  "revoked_at": "2026-02-25T10:00:00Z",
  "reason": "key_compromise",
  "checked_at": "2026-02-26T18:30:00Z"
}
```

**Revocation Reasons:**
- `unspecified` - No specific reason given
- `key_compromise` - Private key was compromised
- `ca_compromise` - Issuer compromise (rare)
- `affiliation_changed` - Agent ownership changed
- `superseded` - Certificate replaced by newer one
- `cessation_of_operation` - Agent no longer operational

---

### GET /api/crl/download

Download complete Certificate Revocation List (RFC 5280 format).

**Example Request:**
```bash
curl "https://agentshield.live/api/crl/download" -o agentshield.crl
```

**Response:** Binary CRL file (DER format)

**Parse CRL:**
```bash
# View CRL contents
openssl crl -in agentshield.crl -inform DER -text -noout
```

**CRL Fields:**
- Issuer: AgentShield CA
- This Update: CRL generation timestamp
- Next Update: Next scheduled CRL update (24h)
- Revoked Certificates: List of revoked cert serial numbers

---

### POST /api/crl/revoke/:id

**[Authenticated]** Revoke a certificate.

**Parameters:**
- `id` (required, in URL) - Certificate ID to revoke
- `reason` (optional, in body) - Revocation reason (see list above)

**Example Request:**
```bash
curl -X POST \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"reason": "key_compromise"}' \
     "https://agentshield.live/api/crl/revoke/agent_compromised_123"
```

**Example Response:**
```json
{
  "success": true,
  "revoked": true,
  "id": "agent_compromised_123",
  "revoked_at": "2026-02-26T18:35:00Z",
  "reason": "key_compromise",
  "crl_updated": true
}
```

---

## 🔑 Challenge-Response Endpoints

### POST /api/challenge/create

Create a challenge for cryptographic identity verification.

**Request Body:**
```json
{
  "agent_id": "agent_kalle_oc_2024"
}
```

**Example Request:**
```bash
curl -X POST \
     -H "Content-Type: application/json" \
     -d '{"agent_id": "agent_kalle_oc_2024"}' \
     "https://agentshield.live/api/challenge/create"
```

**Example Response:**
```json
{
  "success": true,
  "challenge": {
    "nonce": "9f3c7e21b8a4d5f0...",
    "expires_at": "2026-02-26T18:45:00Z",
    "agent_id": "agent_kalle_oc_2024"
  }
}
```

**Challenge Properties:**
- `nonce`: Random 32-byte hex string (challenge to sign)
- `expires_at`: Challenge expiry (5 minutes from creation)
- `agent_id`: Agent identifier for this challenge

---

### POST /api/challenge/verify

Verify challenge signature.

**Request Body:**
```json
{
  "agent_id": "agent_kalle_oc_2024",
  "nonce": "9f3c7e21b8a4d5f0...",
  "signature": "ed25519_signature_hex...",
  "public_key": "ed25519_public_key_hex..."
}
```

**Example Request:**
```bash
curl -X POST \
     -H "Content-Type: application/json" \
     -d '{
       "agent_id": "agent_kalle_oc_2024",
       "nonce": "9f3c7e21b8a4d5f0...",
       "signature": "a1b2c3d4...",
       "public_key": "ed25519:AAAAC3..."
     }' \
     "https://agentshield.live/api/challenge/verify"
```

**Example Response (Success):**
```json
{
  "success": true,
  "verified": true,
  "agent_id": "agent_kalle_oc_2024",
  "certificate_issued": true,
  "certificate": {
    "id": "cert_abc123...",
    "issued_at": "2026-02-26T18:40:00Z",
    "expires_at": "2027-02-26T18:40:00Z",
    "public_key_hash": "SHA256:abc123..."
  }
}
```

**Example Response (Failure):**
```json
{
  "success": false,
  "verified": false,
  "error": "Invalid signature",
  "details": "Signature verification failed for public key"
}
```

---

## 📊 Status Endpoints

### GET /api/status

API health check.

**Example Request:**
```bash
curl "https://agentshield.live/api/status"
```

**Example Response:**
```json
{
  "status": "online",
  "version": "6.4.0",
  "uptime": 86400,
  "database": "connected",
  "crl_last_update": "2026-02-26T06:00:00Z",
  "total_certificates": 42,
  "total_revocations": 2
}
```

---

### GET /api/rate-limit/status

Check your current rate limit status.

**Example Request:**
```bash
curl "https://agentshield.live/api/rate-limit/status"
```

**Example Response:**
```json
{
  "success": true,
  "limit": 3,
  "remaining": 2,
  "reset_at": "2026-02-26T19:00:00Z",
  "current_time": "2026-02-26T18:45:00Z"
}
```

**Rate Limit Headers:**
All API responses include:
- `X-RateLimit-Limit`: Maximum requests per hour
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Unix timestamp when limit resets

---

## ⚠️ Error Responses

All errors follow this format:

```json
{
  "success": false,
  "error": "Human-readable error message",
  "code": "ERROR_CODE",
  "details": "Additional error context (optional)"
}
```

**Common Error Codes:**

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INVALID_AGENT_ID` | 400 | Malformed agent identifier |
| `CERTIFICATE_NOT_FOUND` | 404 | No certificate for agent |
| `CHALLENGE_EXPIRED` | 400 | Challenge nonce expired |
| `SIGNATURE_INVALID` | 401 | Invalid Ed25519 signature |
| `UNAUTHORIZED` | 401 | Missing or invalid API key |
| `SERVER_ERROR` | 500 | Internal server error |

---

## 📈 Rate Limits

| Tier | Endpoint | Limit |
|------|----------|-------|
| **Free** | `/api/registry/*` | 60 req/hour |
| **Free** | `/api/verify/*` | 60 req/hour |
| **Free** | `/api/crl/check/*` | 100 req/hour |
| **Free** | `/api/challenge/*` | 3 req/hour (then 1/hour) |
| **Pro** | All endpoints | 1000 req/hour |

**Upgrade:** Contact ratgeberpro@gmail.com

---

## 🧪 Testing

### Sandbox Environment

**Base URL:** `https://sandbox.agentshield.live/api`

- Test certificates issued with `test_` prefix
- Not included in production registry
- No rate limits
- Resets daily

**Example:**
```bash
curl "https://sandbox.agentshield.live/api/verify/test_agent_123"
```

---

## 📚 SDKs & Libraries

### Python
```python
from agentshield import Client

client = Client(api_key="YOUR_API_KEY")
agent = client.verify("agent_kalle_oc_2024")
print(f"Trust Score: {agent.trust_score}")
```

### JavaScript
```javascript
const AgentShield = require('agentshield-js');

const client = new AgentShield({ apiKey: 'YOUR_API_KEY' });
const agent = await client.verify('agent_kalle_oc_2024');
console.log(`Trust Score: ${agent.trustScore}`);
```

### curl Examples
See [examples/curl-examples.sh](../examples/curl-examples.sh)

---

## 🔗 Webhooks

**[Coming in v6.5]** Subscribe to events:
- Certificate issued
- Certificate revoked
- Trust score updated

---

## Support

- **Documentation:** [github.com/bartelmost/agentshield](https://github.com/bartelmost/agentshield)
- **API Status:** [status.agentshield.live](https://status.agentshield.live)
- **Support:** ratgeberpro@gmail.com

---

*Last Updated: 2026-02-26*  
*API Version: v6.4*
