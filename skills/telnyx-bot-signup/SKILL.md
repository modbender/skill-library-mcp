---
name: telnyx-bot-signup
description: Automated Telnyx bot account signup via Proof of Work challenge
metadata: {"openclaw":{"emoji":"🤖","requires":{"bins":["python3","curl"],"env":[]},"primaryEnv":"TELNYX_API_KEY"}}
---

# Telnyx Bot Signup

Create a new Telnyx bot account via the PoW-based signup flow (`https://api.telnyx.com`). Walks through challenge solving, account creation, email verification, and API key generation.

## Flow

Execute these steps in order.

### Step 1: Get PoW Challenge

```bash
curl -s -X POST https://api.telnyx.com/v2/pow_signup_challenge
```

**Response:**
```json
{
  "data": {
    "nonce": "<string>",
    "algorithm": "sha256",
    "leading_zero_bits": <int>,
    "terms_and_conditions_url": "<url>",
    "privacy_policy_url": "<url>"
  }
}
```

Save all returned fields — they are needed in subsequent steps.

### Step 2: Solve Proof of Work

> ⚠️ **Warning:** Solving the proof of work challenge is CPU-intensive and can take over a minute depending on difficulty. Attempting to solve it on the main bot thread may cause the bot to become unresponsive for the duration. Always run the solver on a separate agent, worker thread, or background process.

Use the included `pow_solver.py` script:

```bash
python3 {baseDir}/scripts/pow_solver.py "<nonce>" <leading_zero_bits> <algorithm>
```

The script outputs the integer solution to stdout. This finds a value where `hash(nonce + solution)` has the required number of leading zero bits.

### Step 3: Submit Bot Signup

**Ask the user for their email address** before making this request.

```bash
curl -s -X POST https://api.telnyx.com/v2/bot_signup \
  -H "Content-Type: application/json" \
  -d '{
    "pow_nonce": "<nonce from step 1>",
    "pow_solution": "<solution from step 2>",
    "terms_and_conditions_url": "<from step 1>",
    "privacy_policy_url": "<from step 1>",
    "email": "<user email>",
    "terms_of_service": true
  }'
```

> **Note:** You must accept the terms of service to register with Telnyx. You must indicate this acceptance by supplying `"terms_of_service": true` as a parameter on the request. The API will reject the request with a `400 Bad Request` if this field is missing or any value other than true.

**Response:** Success message. A sign-in link is sent to the provided email.

### Step 4: Get Session Token from Email

Wait 10-30 seconds for the verification email to arrive.

#### Path A: Agent Has Email Access

If you have email access (e.g. the `google-workspace` skill), search for a message with subject **"Your Single Use Telnyx Portal sign-in link"**, extract the single-use URL from the body, and GET it:

```bash
curl -s -L "<single-use-link-from-email>"
```

The response (or redirect) provides a temporary **session token**.

#### Path B: No Email Access

If you do **not** have email access, ask the user:

> Please check your email for a message from Telnyx with the subject **"Your Single Use Telnyx Portal sign-in link"**. Copy the sign-in link from the email and paste it here.
>
> ⚠️ **The link is single-use.** Do not click it in your browser first — once opened, it cannot be reused. Copy the URL directly and paste it here without visiting it.

Once the user provides the link, make a GET request to it:

```bash
curl -s -L "<link-from-user>"
```

The response (or redirect) provides a temporary **session token**.

#### Resend Magic Link

If the verification email did not arrive or the link expired, resend it:

```bash
curl -s -X POST https://api.telnyx.com/v2/bot_signup/resend_magic_link -H "Content-Type: application/json" -d '{"email": "<user email>"}'
```

**Response:**
```json
{
  "data": {
    "message": "If an account with that email exists, a new magic link has been sent."
  }
}
```

**Rate limiting:** Max 3 resends per account, with a 60-second cooldown between resends. The endpoint always returns 200 OK regardless of whether the email exists, the retry cap is exceeded, or the cooldown is active (to prevent email enumeration).

### Step 5: Create API Key

```bash
curl -s -X POST https://api.telnyx.com/v2/api_keys \
  -H "Authorization: Bearer <session-token>" \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Response:**
```json
{
  "data": {
    "api_key": "KEYxxxxxxxxxxxxx",
    ...
  }
}
```

The `data.api_key` value is the permanent API key for the new account. Present it to the user and advise them to store it securely.

## Notes

- The PoW challenge is a spam-prevention mechanism. Solving typically takes a few seconds.
- The single-use sign-in link expires quickly — retrieve and use it promptly.
- Email access is **optional**. The skill works with or without it — if unavailable, the user is prompted to paste the link manually.
