---
name: shadow-number
description: Get a disposable temp phone number and receive OTP codes to sign up on websites without using your real number. Handles x402 crypto payment automatically.
requires:
  env:
    - SHADOW_WALLET_KEY
---

SHADOW_API_URL=https://extraordinary-charisma-production.up.railway.app

# Shadow Number Skill

Use this skill when you need to sign up on a website that requires phone verification, or any time you need a disposable phone number to receive an OTP/SMS verification code.

## What This Skill Does

1. Calls the Shadow API (x402-gated — payment ~$0.10 USDC on Base is handled automatically)
2. Returns a real temporary phone number for the chosen service and country
3. Navigates to the target website and enters the number into the signup form
4. Polls the Shadow OTP endpoint every 15 seconds until the SMS code arrives
5. Enters the OTP to complete verification

---

## Step 1: Choose Service Code

Pick the service code for the website you are signing up on:

| Website | Code |
|---|---|
| Telegram | opt1 |
| Facebook | opt2 |
| Google / Gmail | opt7 |
| WhatsApp | opt29 |
| Instagram | opt36 |
| Twitter / X | opt48 |
| Microsoft | opt33 |
| Apple | opt42 |
| PayPal | opt15 |
| Amazon | opt22 |
| Tinder | opt38 |
| Shopee | opt49 |

If the exact service is not listed above, use the service name to search — the API accepts any valid SMSPVA service code.

---

## Step 2: Buy a Temp Number (x402 payment)

Make a POST request to the Shadow buy endpoint. This endpoint requires x402 payment — your agent wallet will automatically pay ~$0.10 USDC on Base when the server returns HTTP 402, then retry.

```
POST https://extraordinary-charisma-production.up.railway.app/api/smspva/buy
Content-Type: application/json

{
  "country": "US",
  "service": "opt7"
}
```

Supported country codes: US, GB, FR, DE, IN, BR, PH, ID, NG, RU, UA, PL, CA, AU, MX, and 60+ more.

**Success response (200):**
```json
{
  "statusCode": 200,
  "data": {
    "phoneNumber": "14155552671",
    "orderId": "abc123",
    "orderExpireIn": 600
  }
}
```

The full number to enter on the website is: `+{countryCode}{phoneNumber}` (e.g. `+14155552671` for US numbers).

If you get a non-200 response, try a different country or service code and call buy again.

---

## Step 3: Use the Number on the Website

Use your browser to:

1. Navigate to the website's signup or phone verification page
2. Enter the phone number in international format (e.g. `+14155552671`)
3. Click the "Send code" / "Verify" / "Get OTP" button
4. Wait for the page to confirm the SMS was sent

---

## Step 4: Poll for OTP

After triggering the SMS, poll every 15 seconds:

```
GET https://extraordinary-charisma-production.up.railway.app/api/smspva/otp/{orderId}
```

**OTP received (200):**
```json
{
  "statusCode": 200,
  "data": {
    "sms": { "code": "123456" },
    "orderId": "abc123",
    "orderExpireIn": 540
  }
}
```

Extract `data.sms.code` — that is your OTP.

**Not yet received (202):** wait 15 seconds and retry.

Stop polling if:
- You receive status 200 (success)
- `orderExpireIn` drops to 0 (order expired — start over)
- You receive status 410 (order closed)

---

## Step 5: Enter the OTP

Go back to the browser tab and enter the OTP code from `data.sms.code` into the verification field. Submit the form to complete signup.

---

## Error Recovery

**Number doesn't work / site rejects it:**
```
PUT https://extraordinary-charisma-production.up.railway.app/api/smspva/refuse/{orderId}
```
Then go back to Step 2 and buy a new number.

**Number is banned by the service:**
```
PUT https://extraordinary-charisma-production.up.railway.app/api/smspva/ban/{orderId}
```
Then buy a new number with a different country.

---

## Full Example Flow

> User: "Sign me up on Telegram with a US number"

1. Call `POST /api/smspva/buy` with `{ country: "US", service: "opt1" }`
2. Get back `phoneNumber: "14155552671"`, `orderId: "x9k2m"`
3. Open browser → navigate to `https://web.telegram.org` → start signup
4. Enter `+14155552671` as the phone number → click Send Code
5. Poll `GET /api/smspva/otp/x9k2m` every 15s
6. Receive `{ sms: { code: "84712" } }`
7. Enter `84712` in the Telegram verification box → account created ✅

---

## Notes

- Numbers are single-use and expire after `orderExpireIn` seconds (typically 5–10 minutes)
- Always use international format with `+` prefix when entering the number on websites
- Some services block certain countries — if one country fails, retry with a different one
- The x402 payment (~$0.10 USDC) is charged per number purchase, not per OTP poll
