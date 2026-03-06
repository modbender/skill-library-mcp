# ClawTime — Device Authentication Deep Dive

The gateway handshake is where most ClawTime installs fail. This doc explains exactly how it works.

## How It Works

ClawTime authenticates with the OpenClaw gateway using an Ed25519 keypair:

1. On first run, `~/.clawtime/device-key.json` is auto-generated (contains public + private key)
2. On every gateway connection, ClawTime signs a payload and sends it with the WebSocket handshake
3. The gateway verifies the signature and grants access

## Device ID

Device ID = **SHA-256 hash of the raw 32-byte Ed25519 public key** (hex encoded).

⚠️ Common mistake: Node.js `crypto.generateKeyPairSync('ed25519')` returns SPKI-encoded keys (DER format). You must strip the SPKI prefix before hashing.

SPKI prefix to strip: `302a300506032b6570032100` (12 bytes)

```js
// Correct device ID derivation
const { publicKey } = crypto.generateKeyPairSync('ed25519', {
  publicKeyEncoding: { type: 'spki', format: 'der' }
});
const rawPubKey = publicKey.slice(12); // strip SPKI prefix → 32 raw bytes
const deviceId = crypto.createHash('sha256').update(rawPubKey).digest('hex');
```

## Signature Payload Format

The signed payload must follow this exact format (v2):

```
v2|{deviceId}|{clientId}|{clientMode}|{role}|{scopes}|{signedAtMs}|{token}|{nonce}
```

Example:
```
v2|a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2|webchat-ui|webchat|operator|operator.write,operator.read|1740000000000|your-gateway-token|3888df6c-uuid-here
```

Fields:
- `deviceId` — SHA-256 of raw pubkey (hex)
- `clientId` — typically `"webchat-ui"`
- `clientMode` — typically `"webchat"`
- `role` — typically `"operator"`
- `scopes` — `"operator.write,operator.read"`
- `signedAtMs` — Unix timestamp in milliseconds (`Date.now()`)
- `token` — your `GATEWAY_TOKEN` env var value
- `nonce` — a UUID v4 generated fresh each connection

## Encoding

- Public key sent as **base64url** encoded raw 32-byte key (NOT base64, NOT SPKI DER)
- Signature is **base64url** encoded
- The gateway verifies with: `crypto.verify(null, payload, publicKey, signature)`

```js
const sig = crypto.sign(null, Buffer.from(payload), privateKeyObj);
const sigBase64url = sig.toString('base64url');
const pubBase64url = rawPubKey.toString('base64url');
```

## WebSocket Handshake

The `device` object sent during connection:

```json
{
  "deviceId": "<sha256-hex>",
  "publicKey": "<base64url-raw-32-bytes>",
  "signature": "<base64url>",
  "payload": "v2|deviceId|clientId|...|nonce"
}
```

## Debugging Auth Issues

### "device signature invalid"
→ Payload format doesn't match. Verify the exact format above.
→ Check that `signedAtMs` isn't too old (gateway may have a time window).

### "device identity mismatch"
→ `deviceId` doesn't match the hash of the provided `publicKey`.
→ You're hashing the SPKI-encoded key instead of the raw 32 bytes.
→ Fix: strip the 12-byte SPKI prefix before hashing.

### New device, needs approval
→ First time a keypair is seen, the gateway may require manual approval.
→ Check OpenClaw gateway device management panel.

### Nuclear reset
```bash
rm ~/.clawtime/device-key.json
pkill -f "node server.js"; sleep 2
# Restart — fresh keypair generated
```
