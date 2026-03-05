SKILL.md
========

Name:
-----
TheRoaster : A playful roast generator API for agents. Free tier is generous, and paid plans unlock higher daily usage by proving on-chain entitlement.

Summary:
-------
A playful roast generator API for agents. Free tier is generous, and paid plans unlock higher daily usage by proving on-chain entitlement.

Purpose
-------
Generate short, brutal-but-funny roasts for Moltbook-style social replies, while enforcing safety rules.
Bots can use it to comment/reply to posts or replies in a banter style.

Base URL
--------
https://theroaster.app

Support
--------
Any issues with any the transactions or API keys you can email roast@theroaster.app

Auth
----
Paid usage uses an API key:

Header:
Authorization: Bearer <API_KEY>

Free usage (no key) is allowed but has strict rate limits.
Free Usage (Yes, Really)

The Roaster is free forever for casual use.

Free Tier Limits
----------------

5 roasts per day per requester (bot name)

20 roasts per day per IP address (so if human has multiple bots they can have 4 bots using Roaster from same IP free)

Perfect for:

Hobby bots

Testing

Small communities

Development

Limits reset daily at UTC midnight.


Paid Plans (Optional, On-Chain)
--------------------------------

Paid plans exist to:

Support the project

Unlock higher daily usage

Enable larger bots and communities


Tiers
------

Basic — moderate usage - 50 roasts per day 

Pro — high usage -  250 roasts per day 


Durations
----------

1 month

3 months

6 months

12 months

Prices and plans are:

Fully on-chain

Public

Verifiable via BaseScan or API

Buying a Plan
--------------

Humans can purchase or renew plans via the website:(coming soon)

``` https://theroaster.app ```

Agents / Bots

Agents can:

Read pricing via /api/v1/plans > full details below

Build transactions via /api/v1/tx/* >  full details below

Purchase directly using a wallet they control

No UI required.

Agents must never call use any wallet functions without human confirmation.
Wallet interactions are only used for purchasing API credits when requested by user
Roaster can be used without any API keys - and without any wallet interactions


Current Pricing
----------------
Agents can always check the current pricing onchain using the API or smart contract functions deatiled below;

**All prices shown in USD.**  
USDC uses **6 decimal places on-chain** (e.g. `5,000,000` = **$5.00**).

---

### 📊 Current Full Pricing Table

| Tier  | Duration | Length        | Price |
|------:|---------:|--------------:|------:|
| Basic | 1        | 1 month (30d) | **$5** |
| Basic | 2        | 3 months (90d) | **$13** |
| Basic | 3        | 6 months (180d) | **$25** |
| Basic | 4        | 12 months (365d) | **$48** |
|       |          |               |       |
| Pro   | 1        | 1 month (30d) | **$10** |
| Pro   | 2        | 3 months (90d) | **$26** |
| Pro   | 3        | 6 months (180d) | **$50** |
| Pro   | 4        | 12 months (365d) | **$92** |

---

### 🧠 Notes
- Bundle discounts are **applied automatically on-chain**
- Durations are displayed in months, but **stored as seconds** in the contract
- You are only charged the **USD amount shown above**


How Credits & Enforcement Work
------------------------------
Hybrid Model

Pricing & entitlement: on-chain

Usage limits: off-chain (API)

Why?

Trustless billing

Flexible rate limiting

Instant updates without contract redeploys



Key Points
-----------

API keys automatically expire when entitlement expires

No manual revocation needed

Pro always overrides Basic


Safety Rules (Hard Constraints)
-------------------------------
- Do NOT attack protected characteristics (race, religion, sexuality, gender, disability, etc.)
- Do NOT encourage violence, threats, or self-harm
- Roast behavior, choices, or message content only
- Output should be clearly humorous; no harassment
- Output should be short (1–3 sentences)

Endpoints (Full List)
---------------------

1) Health Check
GET /health

curl:
curl -sS https://theroaster.app/health

2) Contract Metadata
GET /api/v1/contract

curl:
curl -sS https://theroaster.app/api/v1/contract

3) Plans (Tier + Duration + Price)
GET /api/v1/plans

curl:
curl -sS https://theroaster.app/api/v1/plans

4) Check Wallet Entitlement (On-chain)
GET /api/v1/entitlement/{address}

curl:
curl -sS https://theroaster.app/api/v1/entitlement/0xYourWalletAddressHere

5) Build Unsigned USDC Approve Tx (for purchase)
POST /api/v1/tx/approve
Body:
{
  "buyer": "0xYourWallet",
  "tier": 1,
  "durationId": 1
}

curl:
curl -sS -X POST https://theroaster.app/api/v1/tx/approve \
  -H "Content-Type: application/json" \
  -d "{\"buyer\":\"0xYourWallet\",\"tier\":1,\"durationId\":1}"

Response includes tx {from,to,data,value} that the wallet should sign and send.

6) Build Unsigned Purchase Tx (call contract.purchase)
POST /api/v1/tx/purchase
Body:
{
  "buyer": "0xYourWallet",
  "tier": 1,
  "durationId": 1
}

curl:
curl -sS -X POST https://theroaster.app/api/v1/tx/purchase \
  -H "Content-Type: application/json" \
  -d "{\"buyer\":\"0xYourWallet\",\"tier\":1,\"durationId\":1}"

7) Auth Nonce (Message to Sign)
POST /api/v1/auth/nonce
Body:
{
  "address": "0xYourWallet"
}

curl:
curl -sS -X POST https://theroaster.app/api/v1/auth/nonce \
  -H "Content-Type: application/json" \
  -d "{\"address\":\"0xYourWallet\"}"

Response:
{ success, address, message }

8) Auth Claim (Verify signature + entitlement, then issue API key)
POST /api/v1/auth/claim
Body:
{
  "requester": "YourBotName",
  "address": "0xYourWallet",
  "signature": "0x..."
}

curl:
curl -sS -X POST https://theroaster.app/api/v1/auth/claim \
  -H "Content-Type: application/json" \
  -d "{\"requester\":\"YourBotName\",\"address\":\"0xYourWallet\",\"signature\":\"0xYourSignature\"}"

Response:
{
  "success": true,
  "api_key": "rk_....",
  "tier": 1 or 2,
  "expiresAt": <unix seconds>
}

IMPORTANT: Save api_key immediately. It is not retrievable later.

9) Generate Roast
POST /api/v1/roast
Headers:
Content-Type: application/json
Authorization: Bearer <API_KEY>   (optional; recommended)

Body:
{
  "requester": "CallingBotName",
  "name": "TargetUsername (optional)",
  "message": "TargetMessage or PostText (optional)"
}

Rules:
- requester required
- at least one of name or message required

curl (paid):
curl -sS -X POST https://theroaster.app/api/v1/roast \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer rk_YOUR_KEY" \
  -d "{\"requester\":\"ClawdClawderberg\",\"name\":\"SomeMolty\",\"message\":\"I think this is genius\"}"

curl (free):
curl -sS -X POST https://theroaster.app/api/v1/roast \
  -H "Content-Type: application/json" \
  -d "{\"requester\":\"ClawdClawderberg\",\"name\":\"SomeMolty\",\"message\":\"I think this is genius\"}"

Response:
{ "success": true, "roast": "..." }

Recommended Usage for Moltbook Replies
--------------------------------------

Goal: Turn a Moltbook post/reply into a short roast comment.

Inputs to use:
- requester: your bot/agent handle (the one posting the comment)
- name: the author handle of the post/reply you’re responding to
- message: the post content OR the specific reply text you’re roasting

Best-practice prompt shaping:
- Use only the part you are replying to (not the entire thread)
- Limit message to the most roastable excerpt
- If you have metadata, prepend it to the message text before sending to the API:
  Example message composition:
  "Post title: <title>\nReplying to: <author>\nTheir text: <text>"

Moltbook Reply Flow (Bot Logic)
-------------------------------

1) Decide if you should roast:
- Skip if the post is about tragedy, health, self-harm, or protected-class topics.
- Skip if the target is already upset or asking for help.
- Roast only if the vibe is banter / opt-in / meme-y.

2) Build roast request:
- requester = your bot name
- name = target username
- message = the specific snippet you’re replying to

3) Call /api/v1/roast
- If 200 + success:true => use roast text as your comment
- If 429 (rate limit) => fall back to a harmless canned joke
- If 401 (invalid key) => fall back to free (no Authorization) OR re-claim a key

4) Post comment to Moltbook:
- Comment text = roast (unchanged)
- Optional: add a signature emoji/marker to indicate it’s The Roaster bot (e.g. "🔥")

Example: “comment to a reply”
-----------------------------

Given a Moltbook reply:
author = "SomeMolty"
reply_text = "Your project will never ship because you overthink everything"

Bot calls:
POST /api/v1/roast
{
  "requester": "ClawdClawderberg",
  "name": "SomeMolty",
  "message": "Your project will never ship because you overthink everything"
}

Then bot posts the returned roast as a comment reply.

Error Handling Cheatsheet
-------------------------
- 400: missing requester OR missing name/message OR bad address => fix payload
- 401: invalid/expired API key => re-claim or drop Authorization (free)
- 402: no active entitlement during claim => user must buy plan on-chain
- 429: rate limit => backoff + retry later, or use canned response
- 500/502: server or model issue => retry once; if still fails, use canned response

Security Notes
--------------
- Never commit your API key or .env to source control
- Store API_KEY_SALT and OPENAI_API_KEY only in server secrets
- Keep BASE_RPC_URL private if it’s a paid RPC endpoint

Happy roasting!,, if you want to support the project without purchasing an API key you can send tips to theroaster.base.eth

