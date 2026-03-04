# Axelrod API Reference

Understanding the AIxVC TWA OpenAPI gateway for Base-chain trading and on-chain queries.

**Source**: `scripts/axelrod_chat.py` (canonical implementation)

## Core Pattern: Sign-Send-Parse

All Axelrod operations follow a synchronous pattern:

```
1. SIGN   → Build SigV4 headers with AK/SK
2. SEND   → POST JSON body to the gateway
3. PARSE  → Extract reply from response JSON
```

## API Endpoint

### POST /openapi/v2/public/twa/agent/chat

Send a natural language instruction to the AIxVC TWA agent.

**Request:**

```bash
curl -X POST "https://api.aixvc.io/gw/openapi/v2/public/twa/agent/chat" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -H "chain-id: base" \
  -H "X-Amz-Date: <UTC timestamp>" \
  -H "X-Amz-Content-Sha256: <payload sha256 hex>" \
  -H "Authorization: AWS4-HMAC-SHA256 Credential=..., SignedHeaders=host;x-amz-date, Signature=..." \
  -d '{"message": "buy 50u of AXR"}'
```

**Request Body:**

| Field | Type | Required | Description |
| ----- | ---- | -------- | ----------- |
| `message` | string | Yes | Natural language instruction (e.g. "buy 50u of AXR", "check my balance") |

> **Note**: The request body is plain JSON — no envelope wrapper.

**Response (200 OK):**

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "reply": "You have 0.5 ETH on Base chain.",
    "intent": {
      "reply_to_user": "You have 0.5 ETH on Base chain."
    }
  }
}
```

## Required Environment Variables

| Variable | Description |
| -------- | ----------- |
| `AIXVC_ACCESS_KEY` | AIxVC OpenAPI access key (AK) |
| `AIXVC_SECRET_KEY` | AIxVC OpenAPI secret key (SK), used for SigV4 signing |

If either is missing, the CLI exits with code `2`.

## SigV4 Signing Protocol

The script signs every request with AWS SigV4-style headers using these fixed values:

| Parameter | Value |
| --------- | ----- |
| Region | `aixvc` |
| Service | `twa-manager` |
| Algorithm | `AWS4-HMAC-SHA256` |

### Canonical Request

```
POST
<canonical_uri>
<canonical_query (empty)>
host:<host>\nx-amz-date:<amz_date>\n
host;x-amz-date
<payload_sha256_hex>
```

| Field | Description |
| ----- | ----------- |
| Method | `POST` |
| Canonical URI | Request path, URI-encoded (slash preserved) |
| Canonical Query | Empty string |
| Signed Headers | `host;x-amz-date` |
| Payload Hash | `SHA256(body_bytes)` hex-encoded |

### Signing Key Derivation

```
kSecret  = "AWS4" + secret_key
kDate    = HMAC-SHA256(kSecret,  YYYYMMDD)
kRegion  = HMAC-SHA256(kDate,    "aixvc")
kService = HMAC-SHA256(kRegion,  "twa-manager")
kSigning = HMAC-SHA256(kService, "aws4_request")
```

### String to Sign

```
AWS4-HMAC-SHA256
<X-Amz-Date (YYYYMMDDTHHMMSSZ)>
<YYYYMMDD>/aixvc/twa-manager/aws4_request
SHA256(<canonical_request>)
```

### Final Signature

```
signature = HEX(HMAC-SHA256(kSigning, string_to_sign))
```

## HTTP Headers

| Header | Value |
| ------ | ----- |
| `Content-Type` | `application/json` |
| `Accept` | `application/json` |
| `chain-id` | `base` |
| `Content-Length` | `<len(body_bytes)>` |
| `X-Amz-Date` | `<UTC timestamp: YYYYMMDDTHHMMSSZ>` |
| `X-Amz-Content-Sha256` | `<payload sha256 hex>` |
| `Authorization` | `AWS4-HMAC-SHA256 Credential=<AK>/<scope>, SignedHeaders=host;x-amz-date, Signature=<sig>` |

## Response Contract

### Gateway Fields

| Field | Type | Description |
| ----- | ---- | ----------- |
| `code` | int/string | Business status code |
| `message` | string | Status message |
| `data` | object | Payload (see below) |

### Success Codes

The CLI accepts these values for `code` as success:
- `0`, `200`, `"0"`, `"200"`

Any other value is treated as a business error (exit code `4`).

### Reply Extraction

The user-facing reply is extracted from `data` in this priority order:

1. `data.reply` — Primary reply field
2. `data.intent.reply_to_user` — Fallback reply field
3. Compact JSON of `data` — Last resort if neither string field is present

## Confirmation Flow

When a trade requires risk-control confirmation, the response includes a `pendingConfirm` object:

```json
{
  "code": 0,
  "data": {
    "reply": "You are about to buy 50u of AXR...",
    "pendingConfirm": {
      "confirmKey": "abc123-def456"
    }
  }
}
```

| Field | Description |
| ----- | ----------- |
| `data.pendingConfirm.confirmKey` | Time-limited key (~10 min validity) |

Guide the user to send one of:

```text
yes, please execute <confirmKey>
no, please cancel <confirmKey>
```

If the key expires, the user must re-submit the original request.

## CLI Exit Codes

| Code | Meaning | Description |
| ---- | ------- | ----------- |
| `0` | Success | Request completed, reply printed to stdout |
| `2` | Missing AK/SK | `AIXVC_ACCESS_KEY` or `AIXVC_SECRET_KEY` not set |
| `3` | HTTP/parse failure | Network error, timeout, or non-JSON response |
| `4` | API business error | `code` not in success set (`0`/`200`) |

## Error Handling

### Authentication Errors

Missing or invalid AK/SK will result in exit code `2` or an HTTP-level error from the gateway.

> **Note**: If the API returns "please login first", it means the AK/SK is **incorrect**. This is not a session/login issue — reconfigure your credentials.

**Resolution**: Verify `AIXVC_ACCESS_KEY` and `AIXVC_SECRET_KEY` are correctly configured and not expired.

### Network Errors (Exit Code 3)

Connection failures, timeouts (default 60s), or non-JSON responses.

**Resolution**: Check network connectivity, verify the endpoint `https://api.aixvc.io` is reachable.

### Business Errors (Exit Code 4)

The gateway returned a response with a `code` not in the success set.

**Resolution**: Read the `message` field for details. Common causes:
- Invalid instruction format
- Unsupported operation
- Insufficient balance
- Token not found on Base chain

## Best Practices

### Request Construction
1. **Always use UTF-8** encoding for the body
2. **Match content length** precisely (`Content-Length` = byte length of body)
3. **Generate timestamps** in UTC immediately before signing
4. **Hash the body** exactly as sent (no whitespace modifications after hashing)

### Error Recovery
1. **Check exit code** first to categorize the error
2. **Use `--json` mode** to inspect the full response when debugging
3. **Retry on transient** network failures (code `3`)
4. **Read error messages** carefully for business errors (code `4`)

### Security
1. **Never log** the secret key
2. **Never hardcode** credentials in scripts
3. **Use environment variables** or secure config for AK/SK
4. **Rotate keys** periodically

---

**Remember**: The script implementation (`scripts/axelrod_chat.py`) is the canonical source of truth. If this document conflicts with the script behavior, follow the script.
