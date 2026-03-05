---
name: meetlark
description: Scheduling polls for humans and their agents. Create polls, share participation links, collect votes, and find the best meeting time. A Doodle alternative built for the age of AI agents.
homepage: https://meetlark.ai
user-invocable: true
metadata: {"openclaw":{"emoji":"🐦"}}
---

# meetlark.ai — Scheduling polls for humans and their agents

A Doodle alternative built for the age of AI agents. Create a poll, share a link, collect votes, find the best time.

## Two Tokens

When you create a poll you get two tokens:

- **Admin token** (`adm_...`) — Private. View full results, see who voted, close the poll. Store it in your memory for the poll's lifetime.
- **Participate token** (`prt_...`) — Shareable. Anyone with the participate URL can vote — humans via the web UI, agents via the API. Multiple people use the same link.

## Creating a Poll

Ask the user what times work and create the poll with those time slots.

```
POST https://meetlark.ai/api/v1/polls?autoVerify=true
```

The response includes `adminToken` and `participateUrl`.

### Email Verification

Poll creation requires a verified email (one-time, valid for 30 days of activity).

Use `?autoVerify=true` — if the email is unverified, the API automatically sends a verification email and returns:
```json
{
  "error": {
    "code": "email_not_verified",
    "details": { "verificationSent": true, "email": "user@example.com" }
  }
}
```

Tell the user: "Check your email and click the verification link, then let me know."

Poll `GET /api/v1/auth/status?email=...` until `verified: true`, then retry.

## Sharing the Poll

Give the participate URL to the user and ask them to share it. Suggest a message:

```
Hi [name/team],

[Creator] has created a poll to find the best time for [meeting purpose].

Vote here: [participate URL]

Please vote on the times that work for you.
```

## Checking Results

```
GET https://meetlark.ai/api/v1/polls/{pollId}
Authorization: Bearer adm_...
```

Returns vote counts per time slot and individual votes.

## Closing the Poll

```
POST https://meetlark.ai/api/v1/polls/{pollId}/close
Authorization: Bearer adm_...
```

## Quick Examples

```
"Create a poll for our team standup next week"
"Schedule a 1:1 with Sarah — find times Thursday or Friday"
"How many people have voted on the standup poll?"
"Close the poll and tell me the winning time"
```

## API

- **OpenAPI spec:** https://meetlark.ai/api/v1/openapi.json
- **Interactive docs:** https://meetlark.ai/docs
- **AI plugin manifest:** https://meetlark.ai/.well-known/ai-plugin.json

## Website

- **meetlark.ai:** https://meetlark.ai
