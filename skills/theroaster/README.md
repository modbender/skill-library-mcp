README.md
=========

Name
-----
TheRoaster - A playful roast generator API for agents. Free tier is generous, and paid plans unlock higher daily usage by proving on-chain entitlement.

Summary
-------
A playful roast generator API for agents. Free tier is generous, and paid plans unlock higher daily usage by proving on-chain entitlement.

About
-------
The Roaster (TheRoaster API)
The Roaster API 🔥
The Roaster is a fast, safety-filtered roast generator for Moltbook-style replies.  
Free tier available (5 roasts/day per requester + IP cap), with optional paid API keys for higher daily limits.

The Roaster is a Web3-powered roast API for AI agents and bots.

It delivers short, brutal-but-funny roasts with clear safety rules, on-chain entitlements, and bot-friendly rate limits.

Entitlements are purchased on-chain (USDC on Base), while API keys are issued off-chain and enforced server-side.
Agents must never call use any wallet functions without human confirmation.
Wallet interactions are only used for purchasing API credits when requested by user
Roaster can be used without any API keys - and without any wallet interactions

------------------------------------------------------------

FEATURES
- Designed for AI agents & bots
- Wallet-based entitlement (no accounts, no emails)
- On-chain plans (USDC on Base)
- Off-chain API keys with daily limits
- Fast, stateless HTTP API
- Deterministic safety rules (no protected-class attacks)
- Free tier (limited, IP-rate-limited)
- API Keys avilable to purchase directly onchain which allow heavier usage.

Free usage (no key) is allowed but has strict rate limits.
Free Usage (Yes, Really)

The Roaster is free forever for small usage. Please support our project by purchasing an API key for heavier usage allowing us to maintain our services.

Free Tier Limits
----------------

5 roasts per day per requester (bot name)

20 roasts per day per IP address (so if human has multiple bots they can have 4 bots using Roaster from same IP free)

Perfect for:

Hobby bots, Testing , Small communities, Development

Limits reset daily at UTC midnight.


Paid Plans (Optional, On-Chain)
--------------------------------

Paid plans exist to:

Support the project

Unlock higher daily usage

Enable larger bots and communities

Ask your agent to check the latest prices onchain!

Tiers
------

Free - Lightusage - 5 roasts per day per bot - max 20 per IP

Basic — moderate usage - 50 roasts per day (locked to botname)

Pro — high usage -  250 roasts per day


Paid Durations
----------

1 month, 3 months , 6 months ,12 months

Prices and plans are:

Fully on-chain

Public

Verifiable via BaseScan or API

Buying a Plan
----------------
Humans

Humans can purchase or renew plans via the website:(coming soon)

``` https://theroaster.app ```

Agents / Bots

Agents can:

Read pricing via /api/v1/plans > full details in SKILL.MD

Build transactions via /api/v1/tx/* >  full details in SKILL.MD

Purchase directly using a wallet they control

No UI required.

------------------------------------------------------------

HOW IT WORKS (HIGH LEVEL)
1) User/bot buys a plan on-chain (USDC -> TheRoaster contract)
2) Wallet signs a message to claim an API key
3) Server verifies entitlement on-chain
4) API key is issued and stored hashed
5) Requests are rate-limited by tier

The contract is the source of truth for access.
The API enforces usage.

------------------------------------------------------------

ON-CHAIN CONTRACT
Network: Base Mainnet (8453)
Token: USDC (6 decimals)
Contract: 0x430bCCfBa14423708E26e19C69a2Ad0b87152B40

------------------------------------------------------------

API ENDPOINTS

Health:
GET https://theroaster.app/health

Contract metadata:
GET https://theroaster.app/api/v1/contract

Plans:
GET https://theroaster.app/api/v1/plans

Check entitlement:
GET https://theroaster.app/api/v1/entitlement/{walletAddress}

Build unsigned approve tx:
POST https://theroaster.app/api/v1/tx/approve
Body JSON:
{
  "buyer": "0xYourWallet",
  "tier": 1,
  "durationId": 1
}

Build unsigned purchase tx:
POST https://theroaster.app/api/v1/tx/purchase
Body JSON:
{
  "buyer": "0xYourWallet",
  "tier": 1,
  "durationId": 1
}

Auth nonce (message to sign):
POST https://theroaster.app/api/v1/auth/nonce
Body JSON:
{
  "address": "0xYourWallet"
}

Auth claim (issue API key if entitled):
POST https://theroaster.app/api/v1/auth/claim
Body JSON:
{
  "requester": "YourBotName",
  "address": "0xYourWallet",
  "signature": "0xSignedMessage"
}

Roast:
POST https://theroaster.app/api/v1/roast
Header:
Authorization: Bearer <API_KEY>
Body JSON:
{
  "requester": "ClawdClawderberg",
  "name": "SomeMolty",
  "message": "I think this is a great idea"
}

Example response:
{
  "success": true,
  "roast": "Calling that a great idea is generous — it’s more like a thought that tripped on the way out."
}

------------------------------------------------------------

AUTHENTICATION
- API keys are issued once and never shown again
- Keys are hashed in the database
- Expiration follows on-chain entitlement
- Invalid or expired keys are rejected

------------------------------------------------------------

SAFETY RULES
- No attacks on protected characteristics
- No encouragement of violence or self-harm
- Roasts target behavior or message content only
- Always framed as humor

------------------------------------------------------------

DEPLOYMENT
- Node.js + Fastify
- Redis (rate limits + nonce storage)
- PostgreSQL (API keys)
- PM2 for process management
- OpenAI API provides roasts
- 
Secrets must be stored in .env (never committed).

------------------------------------------------------------

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
