---
name: bill-tracker
description: Access Bill Tracker financial data - upcoming bills, account balances, and affordability checks.
metadata: {"openclaw":{"requires":{"env":["BILL_TRACKER_URL","BILL_TRACKER_SESSION_TOKEN"]},"primaryEnv":"BILL_TRACKER_SESSION_TOKEN","emoji":"💰"}}
---

# Bill Tracker Skill

When the user asks about their bills, account balances, or whether they can afford something, use the `bash` tool to call the Bill Tracker API.

## Required environment

- `BILL_TRACKER_URL` - Base URL (e.g. https://your-server.com or http://localhost:1337)
- `BILL_TRACKER_SESSION_TOKEN` - Session token for authentication (obtained once via POST /api/mcp/token)

## Getting a session token

Bill Tracker uses magic-link auth (no passwords). Two steps:

1. Request a verification code (sent to email):
```bash
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"email":"user@example.com"}' \
  "${BILL_TRACKER_URL}/api/mcp/request-code"
```

2. Exchange the code from your email for a session token:
```bash
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"code":"123456"}' \
  "${BILL_TRACKER_URL}/api/mcp/token"
```

Store the returned `sessionToken` in `BILL_TRACKER_SESSION_TOKEN`. Tokens are long-lived; no need to re-verify on every request. (Codes expire in 10 minutes.)

## Endpoints

### 1. Upcoming transactions (bills and income due soon)

```
POST ${BILL_TRACKER_URL}/api/mcp/upcoming-transactions
X-Parse-Session-Token: ${BILL_TRACKER_SESSION_TOKEN}
Body: { "days": 3 }
```

Default `days` is 3. Increase for a longer window (e.g. `days=7`).

### 2. Account balances

```
POST ${BILL_TRACKER_URL}/api/mcp/account-balances
X-Parse-Session-Token: ${BILL_TRACKER_SESSION_TOKEN}
```

Returns each account with name, type, balance, and a totalBalance (cash minus debt).

### 3. Can I afford X?

```
POST ${BILL_TRACKER_URL}/api/mcp/can-afford
X-Parse-Session-Token: ${BILL_TRACKER_SESSION_TOKEN}
Body: { "amount": 500, "horizonDays": 90 }
```

Replace `500` with the amount in dollars. `horizonDays` defaults to 90.

Returns either `canAfford: true` with the date they can afford it, or `canAfford: false` with a message.

## How to call

Use curl with POST. Pass `X-Parse-Session-Token` (or `Authorization: Bearer $BILL_TRACKER_SESSION_TOKEN`) for authentication. The token identifies the user—no email or password needed. Parse the JSON response and summarize clearly for the user.

Example (upcoming transactions):
```bash
curl -s -X POST -H "X-Parse-Session-Token: $BILL_TRACKER_SESSION_TOKEN" -H "Content-Type: application/json" \
  -d '{"days": 3}' \
  "${BILL_TRACKER_URL}/api/mcp/upcoming-transactions"
```

Example (account balances):
```bash
curl -s -X POST -H "X-Parse-Session-Token: $BILL_TRACKER_SESSION_TOKEN" -H "Content-Type: application/json" \
  -d '{}' \
  "${BILL_TRACKER_URL}/api/mcp/account-balances"
```

Example (can afford):
```bash
curl -s -X POST -H "X-Parse-Session-Token: $BILL_TRACKER_SESSION_TOKEN" -H "Content-Type: application/json" \
  -d '{"amount": 500}' \
  "${BILL_TRACKER_URL}/api/mcp/can-afford"
```
