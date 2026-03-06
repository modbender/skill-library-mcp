# x402 Payment Flow (USDC)

Detailed steps for handling HTTP 402 Payment Required responses.

## 1. Forward the 402 to Crow

```
POST https://api.crowpay.ai/authorize
X-API-Key: crow_sk_...
Content-Type: application/json

{
  "paymentRequired": <the full 402 response body>,
  "merchant": "Name of the API/service",
  "reason": "Why you need this"
}
```

Pass the entire 402 response JSON as `paymentRequired`. Provide a clear `merchant` name and `reason` — the wallet owner sees these.

## 2. Handle the response

### 200 — Approved

You get a signed payment payload. Retry your original request with:

```
base64(JSON.stringify(response_body))
```

Put this in the `X-PAYMENT` header of your retry request.

### 202 — Pending human approval

The amount exceeded the auto-approve threshold. Poll for a decision:

```
GET https://api.crowpay.ai/authorize/status?id=<approvalId>
X-API-Key: crow_sk_...
```

Poll every 3 seconds. When the response contains a `payload` field, use it. If `status` is `"denied"`, `"timeout"`, or `"failed"`, stop.

### 403 — Denied

Spending rules blocked this payment. Do not retry with the same parameters.

## 3. After successful payment

Report the settlement:

```
POST https://api.crowpay.ai/settle
X-API-Key: crow_sk_...
Content-Type: application/json

{
  "transactionId": "...",
  "txHash": "0x..."
}
```
