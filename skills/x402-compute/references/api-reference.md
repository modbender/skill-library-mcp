# x402Compute API Reference

Base URL: `https://compute.x402layer.cc`

## Endpoints

### Authentication (Required for management endpoints)

All **instance management** endpoints require authentication. Provision/extend accept x402 payment without compute auth headers. Choose one for management:

- **Signature Auth (wallet signing)**  
  Required headers:
  - `X-Auth-Address`: wallet address
  - `X-Auth-Chain`: `base` or `solana`
  - `X-Auth-Signature`: signature over the request
  - `X-Auth-Timestamp`: epoch millis
  - `X-Auth-Nonce`: unique nonce
  - `X-Auth-Sig-Encoding`: `hex` (Base) or `base64` (Solana)

- **API Key Auth (agent access)**
  Required header:
  - `X-API-Key`: compute API key (create via `POST /compute/api-keys`)

### GET /compute/plans

List available compute plans with pricing.

**Query Parameters:**
- `type` (optional): Filter by plan type — `vps`, `vhp`, `vdc`, `vcg` (GPU)

**Response:**
```json
{
  "plans": [
    {
      "id": "vcg-a100-1c-2g-6gb",
      "vcpu_count": 12,
      "ram": 120832,
      "disk": 1600,
      "bandwidth": 10240,
      "monthly_cost": 90,
      "type": "GPU",
      "gpu_vram_gb": 80,
      "gpu_type": "NVIDIA A100",
      "locations": ["lax", "ewr", "ord"]
    }
  ],
  "count": 1
}
```

Prices include the platform markup and are in USD. Plans now include `our_daily` pricing (hourly × 24). The x402 payment amount is calculated from the hourly rate times `prepaid_hours`, converted to USDC atomic units (6 decimals).

---

### GET /compute/regions

List available deployment regions.

**Response:**
```json
{
  "regions": [
    {
      "id": "lax",
      "city": "Los Angeles",
      "country": "US",
      "continent": "North America"
    }
  ]
}
```

---

### GET /compute/os

List available operating system images.

**Response:**
```json
{
  "os_options": [
    {
      "id": 2284,
      "name": "Ubuntu 24.04 LTS x64",
      "arch": "x64",
      "family": "ubuntu"
    }
  ]
}
```

---

### POST /compute/provision

Provision a new compute instance. Returns `402 Payment Required` with payment challenge.

**Request Body:**
```json
{
  "plan": "vc2-1c-1gb",
  "region": "ewr",
  "os_id": 2284,
  "label": "my-daily-instance",
  "prepaid_hours": 24,
  "ssh_public_key": "ssh-ed25519 AAAA... user@host",
  "network": "base"
}
```

**Notes:**
- `prepaid_hours` minimum is **24** (1 day). Use `24` for daily, `72` for 3 days, `168` for 1 week, `720` for 1 month, etc.
- Provide `ssh_public_key` to enable SSH access. Passwords are not returned by the API.
- If you do not provide an SSH key, use one-time fallback endpoint `POST /compute/instances/:id/password`.

**Headers:**
- Auth headers (see Authentication above)
- `X-Payment`: Base64-encoded x402 payment payload (after 402 challenge)

**402 Challenge Response:**
```json
{
  "x402Version": 1,
  "accepts": [
    {
      "scheme": "exact",
      "network": "base",
      "maxAmountRequired": "90000000",
      "resource": "https://compute.x402layer.cc/compute/provision",
      "payTo": "0x...",
      "extra": { "name": "USD Coin", "version": "2" }
    }
  ]
}
```

For Solana challenges, `network` may be `solana` (or facilitator-style `solana:*`) and may include `extra.feePayer`.

**Success Response (200):**
```json
{
  "success": true,
  "order": {
    "id": "uuid",
    "vultr_instance_id": "...",
    "plan": "vcg-a100-1c-2g-6gb",
    "region": "lax",
    "status": "active",
    "ip_address": "1.2.3.4",
    "expires_at": "2026-03-17T00:00:00Z"
  },
  "tx_hash": "0x..."
}
```

---

### GET /compute/instances

List your active instances.

**Headers:**
- Auth headers (see Authentication above)

---

### GET /compute/instances/:id

Get details for a specific instance.

**Headers:**
- Auth headers (see Authentication above)

---

### DELETE /compute/instances/:id

Destroy an instance immediately.

**Headers:**
- Auth headers (see Authentication above)

---

### POST /compute/instances/:id/password

Retrieve one-time root password fallback (only if SSH key was not used).

**Headers:**
- Auth headers (see Authentication above)

**Response (200):**
```json
{
  "success": true,
  "access": {
    "method": "one_time_password",
    "username": "root",
    "ip_address": "1.2.3.4",
    "password": "example-password"
  }
}
```

Subsequent calls return `409`.

---

### POST /compute/instances/:id/extend

Extend an instance's lifetime. Returns `402 Payment Required` with payment challenge.

**Request Body:**
```json
{
  "extend_hours": 720,
  "network": "base"
}
```

**Headers:**
- Auth headers (see Authentication above)
- `X-Payment`: Base64-encoded x402 payment payload (after 402 challenge)

---

### POST /compute/api-keys

Create an API key for agent access (signature auth required).

**Request Body:**
```json
{
  "label": "my-agent"
}
```

**Response (201):**
```json
{
  "api_key": "x402c_...",
  "id": "uuid",
  "label": "my-agent",
  "created_at": "2026-02-18T00:00:00Z"
}
```

---

### GET /compute/api-keys

List API keys for your wallet.

**Response:**
```json
{
  "api_keys": [
    {
      "id": "uuid",
      "label": "my-agent",
      "key_last4": "abcd",
      "created_at": "2026-02-18T00:00:00Z",
      "revoked_at": null
    }
  ]
}
```

---

### DELETE /compute/api-keys/:id

Revoke an API key (signature auth required).
