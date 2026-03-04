---
name: PopUp Referrals
description: Check your PopUp referral link, track earnings, and see referred vendor status. Earn $100 per vendor who subscribes annually.
metadata: {"openclaw":{"requires":{"env":["POPUP_API_KEY"]},"primaryEnv":"POPUP_API_KEY"}}
---

# PopUp Referrals

Check your PopUp referral link, track referral earnings, and see the status of vendors you've referred. This skill is read-only — it retrieves referral data from the PopUp API. It does not send messages, contact vendors, or share links on your behalf.

## What This Skill Does

- Retrieves your unique referral code and share URL
- Shows earnings stats (signups, credits, cash earned, account balance)
- Lists referred vendors and their current status

## What This Skill Does NOT Do

- It will not proactively suggest sharing referral links
- It will not contact vendors or send DMs on your behalf
- It will not post on social media or comment on posts
- It only responds when you explicitly ask about your referrals

---

## Reward Structure

- **$100 cash** when a referred vendor subscribes to an annual plan (paid 31 days after subscription start) or stays on monthly billing for 6+ consecutive months
- **No cap** on total referral earnings
- Referred vendors receive **$100 off** their first annual subscription ($399 instead of $499)

> The $5 account credit for profile publication is only available to vendor-type accounts. Organizer accounts earn the $100 cash reward only.

---

## Authentication

All requests require a Bearer token:

```
Authorization: Bearer pk_live_...
```

The token is the `POPUP_API_KEY` environment variable.

**Base URL:** `https://usepopup.com/api/v1/organizer`

**Rate limit:** 60 requests per minute. HTTP 429 returned with `Retry-After: 60` if exceeded.

---

## Endpoints

### Get Referral Dashboard

`GET /referrals`

Returns your referral code, share URL, reward structure, earnings stats, and list of referred users.

**Response fields:**

| Field | Type | Description |
|-------|------|-------------|
| `referralCode` | string | Your unique referral code |
| `shareUrl` | string | Your referral link |
| `rewardStructure` | object | Current reward tiers |
| `stats.totalSignups` | number | Total vendors who signed up via your link |
| `stats.totalAnnualSubscriptions` | number | Vendors who subscribed annually |
| `stats.totalCreditsEarned` | number | Total credits earned (cents) |
| `stats.totalCashEarned` | number | Total cash earned (cents) |
| `accountBalance` | number | Current account balance (cents) |
| `referrals` | array | List of referred users with name, signup date, and reward status |

**Example output:**

```
PopUp Referral Dashboard
────────────────────────────────
  Referral Code:      ABC123
  Share URL:          https://usepopup.com/r/ABC123
  Total Signups:      12
  Credits Earned:     $25.00
  Cash Earned:        $300.00
  Account Balance:    $125.00
────────────────────────────────

Recent Referrals:
  - Jane's Food Truck — signed up Jan 15 — subscribed (annual)
  - DJ Mike — signed up Jan 22 — free tier
  - Sweet Treats Bakery — signed up Feb 1 — trial active
```

---

## Response Format

All endpoints return JSON with `{ "data": ... }` wrapper.

Error responses: `{ "error": "message" }` with HTTP status 400, 401, 404, 429, or 500.
