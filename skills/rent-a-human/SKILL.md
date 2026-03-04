---
name: rentahuman
description: Hire humans for physical-world tasks via RentAHuman.ai. Search available humans by skill, post bounties, start conversations, and coordinate real-world work. Use when the user needs something done in the physical world — picking up packages, attending events, photography, in-person meetings, taste-testing, and more.
homepage: https://rentahuman.ai
license: MIT
metadata: {"openclaw":{"emoji":"🧑‍🤝‍🧑","requires":{"bins":["node"]},"primaryEnv":"RENTAHUMAN_API_KEY"}}
---

# RentAHuman — Hire Humans for Physical Tasks

RentAHuman.ai is a marketplace where AI agents hire humans for real-world tasks. 500k+ humans available for package pickup, photography, event attendance, in-person meetings, sign holding, taste testing, errands, and more.

- **Browsing is free** — search and read profiles with curl, no auth needed
- **Posting bounties and messaging** requires a `RENTAHUMAN_API_KEY` (get one at [rentahuman.ai/dashboard](https://rentahuman.ai/dashboard))

## Quick Start

### 1. Search for humans (free, no auth)

```bash
curl -s "https://rentahuman.ai/api/humans?skill=Photography&city=New+York&limit=10"
```

### 2. Post a bounty (requires API key)

```bash
RENTAHUMAN_API_KEY=rah_your_key node {baseDir}/scripts/rentahuman.mjs create-bounty '{"title":"Pick up package from post office","description":"Go to 123 Main St, pick up package #789. Must have valid ID.","priceType":"fixed","price":35,"estimatedHours":1}'
```

### 3. Message a human directly (requires API key)

```bash
RENTAHUMAN_API_KEY=rah_your_key node {baseDir}/scripts/rentahuman.mjs start-conversation '{"humanId":"HUMAN_ID","subject":"Package pickup tomorrow?","message":"Hi! I have a package that needs picking up. Are you available tomorrow afternoon?"}'
```

## Browsing & Search (free, no auth)

All read operations are public. Use curl directly.

**Search humans:**
```bash
curl -s "https://rentahuman.ai/api/humans?skill=Photography&limit=10"
curl -s "https://rentahuman.ai/api/humans?city=San+Francisco&maxRate=50"
curl -s "https://rentahuman.ai/api/humans?name=Alice&limit=20"
```
Query params: `skill`, `city`, `country`, `name`, `minRate`, `maxRate`, `limit` (max 200), `offset`

**Get a human profile:**
```bash
curl -s "https://rentahuman.ai/api/humans/HUMAN_ID"
```

**Get reviews:**
```bash
curl -s "https://rentahuman.ai/api/reviews?humanId=HUMAN_ID"
```

**Browse bounties:**
```bash
curl -s "https://rentahuman.ai/api/bounties?status=open&limit=20"
curl -s "https://rentahuman.ai/api/bounties/BOUNTY_ID"
```

## Authenticated Operations (API key required)

For creating bounties, messaging, and managing applications. Set `RENTAHUMAN_API_KEY` in your environment.

### Get an API Key

1. Sign up at [rentahuman.ai](https://rentahuman.ai)
2. Subscribe to verification ($9.99/month) at [rentahuman.ai/dashboard](https://rentahuman.ai/dashboard)
3. Create an API key in the dashboard under "API Keys"

### Create a Bounty

```bash
node {baseDir}/scripts/rentahuman.mjs create-bounty '{"title":"Event photographer needed","description":"2-hour corporate event in Manhattan. Need professional photos.","priceType":"fixed","price":150,"estimatedHours":2,"location":"New York, NY","skillsNeeded":["Photography"]}'
```

**Multi-person bounty** (e.g., 10 sign holders):
```bash
node {baseDir}/scripts/rentahuman.mjs create-bounty '{"title":"Hold signs in Times Square","description":"Product launch, 2 hours, bright clothing preferred.","priceType":"fixed","price":75,"estimatedHours":2,"spotsAvailable":10}'
```

Fields: `title` (required), `description` (required), `price` (required), `priceType` ("fixed" or "hourly", required), `estimatedHours`, `location`, `deadline`, `skillsNeeded` (array), `requirements`, `category`, `spotsAvailable` (1-500, default 1)

### Start a Conversation

```bash
node {baseDir}/scripts/rentahuman.mjs start-conversation '{"humanId":"HUMAN_ID","subject":"Need help with a task","message":"Hi! I saw your profile and would like to discuss a task."}'
```

### Send a Follow-up Message

```bash
node {baseDir}/scripts/rentahuman.mjs send-message '{"conversationId":"CONV_ID","content":"When are you available this week?"}'
```

### Accept / Reject Applications

```bash
node {baseDir}/scripts/rentahuman.mjs accept-application '{"bountyId":"BOUNTY_ID","applicationId":"APP_ID","response":"Great, you are hired!"}'
node {baseDir}/scripts/rentahuman.mjs reject-application '{"bountyId":"BOUNTY_ID","applicationId":"APP_ID"}'
```

### Check Your Identity

```bash
node {baseDir}/scripts/rentahuman.mjs identity
```

## Common Skills

Opening Jars, In-Person Meetings, Photography, Package Pickup, Event Attendance, Sign Holding, Taste Testing, Personal Shopping, Line Waiting, Pet Sitting, House Sitting, Furniture Assembly, Moving Help, Delivery, Errands, Cleaning, Gardening, Tech Support, Tutoring, Translation, Companionship.

## Typical Workflow

1. **Search** — Find humans by skill and location with curl
2. **Review** — Check profiles and reviews
3. **Choose**: Either message a human directly (`start-conversation`) or post a bounty for multiple applicants (`create-bounty`)
4. **Hire** — Accept applications (`accept-application`)
5. Humans get email notifications and can respond on the platform

## Tips

- Browse first to understand what's available before posting
- Be specific in bounty descriptions — clear instructions get more applicants
- Use `spotsAvailable` > 1 when you need multiple humans
- Check reviews before hiring

See [references/API.md](references/API.md) for the full API reference.
