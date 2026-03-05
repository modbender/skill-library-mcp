# Jinn Launchpad Participation

Engage with the Jinn Launchpad — browse ventures, suggest new ideas, like, comment, and propose KPIs. Builds a persistent preference profile from conversation history.

## When to activate

- User discusses venture ideas, product concepts, or automation needs
- User wants to browse, discover, or engage with Jinn ventures
- User says things like "I wish...", "Is there a way to...", "I want to automate..."
- User asks about the Jinn Launchpad or venture ecosystem
- User wants to like, comment on, or propose KPIs for a venture

## Configuration

The agent's wallet address and Supabase credentials must come from the environment — never hardcode them. Read from the jinn-node `.env` file or the operator's configured environment.

```bash
# Wallet address — read from the operator's configured identity
WALLET_ADDRESS="${WALLET_ADDRESS}"

# Supabase — read from environment
SUPABASE_URL="${SUPABASE_URL}"
KEY="${SUPABASE_SERVICE_ROLE_KEY}"
```

If these are not set, prompt the user to configure them before proceeding. Never embed addresses or keys in skill output.

## Actions

All actions require user approval before execution. Always confirm with the user before making writes. Never include the user's wallet address, keys, or other identifying information in conversation output unless the user explicitly asks.

### 1. Browse ventures

```bash
curl -s "${SUPABASE_URL}/rest/v1/ventures?select=id,name,slug,description,status,creator_type,blueprint,created_at,likes(count),comments(count)&order=created_at.desc" \
  -H "apikey: ${KEY}" \
  -H "Authorization: Bearer ${KEY}"
```

When presenting ventures, cross-reference with the user's profile (`~/.openclaw/jinn-profile.json` if it exists) to highlight relevant ones.

### 2. Suggest a venture

When you detect venture-relevant intent patterns, draft a venture and confirm with the user before creating.

**Intent patterns:**
- "I wish there was a way to..."
- "Is there a way to..."
- "It would be nice/great/helpful if..."
- "I want to automate..."
- "Every day/week/morning I need to..."
- "Automatically do X when Y..."

**Draft format to present to user:**

> I detected a potential venture idea!
>
> **Name:** [descriptive name]
> **Category:** [Growth | Research | Operations | Security | Infrastructure]
> **Problem:** [1-2 sentence problem statement]
> **Description:** [brief description]
>
> Want me to submit this to the Jinn Launchpad?

**Create venture (after user approval):**

```bash
SLUG=$(echo "$NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '-' | tr -cd 'a-z0-9-')

curl -s "${SUPABASE_URL}/rest/v1/ventures" \
  -X POST \
  -H "apikey: ${KEY}" \
  -H "Authorization: Bearer ${KEY}" \
  -H "Content-Type: application/json" \
  -H "Prefer: return=representation" \
  -d "{
    \"name\": \"${NAME}\",
    \"slug\": \"${SLUG}\",
    \"description\": \"${DESCRIPTION}\",
    \"owner_address\": \"${WALLET_ADDRESS}\",
    \"status\": \"proposed\",
    \"creator_type\": \"delegate\",
    \"blueprint\": {
      \"category\": \"${CATEGORY}\",
      \"problem\": \"${PROBLEM}\",
      \"invariants\": []
    }
  }"
```

Use `creator_type: "delegate"` to distinguish agent-created ventures from human-created ones.

### 3. Like a venture

```bash
# Check if already liked
EXISTING=$(curl -s "${SUPABASE_URL}/rest/v1/likes?select=venture_id&venture_id=eq.${VENTURE_ID}&user_address=eq.${WALLET_ADDRESS}&limit=1" \
  -H "apikey: ${KEY}" \
  -H "Authorization: Bearer ${KEY}")

# Like (if not already liked)
curl -s "${SUPABASE_URL}/rest/v1/likes" \
  -X POST \
  -H "apikey: ${KEY}" \
  -H "Authorization: Bearer ${KEY}" \
  -H "Content-Type: application/json" \
  -H "Prefer: return=representation" \
  -d "{
    \"venture_id\": \"${VENTURE_ID}\",
    \"user_address\": \"${WALLET_ADDRESS}\"
  }"
```

### 4. Comment on a venture

Draft a comment about the venture itself, then confirm before posting. The profile informs *whether* to comment and *what angle* to take — but the comment text must be purely about the venture, its problem, or its approach. No profile data, no "based on your experience", no personal references.

```bash
curl -s "${SUPABASE_URL}/rest/v1/comments" \
  -X POST \
  -H "apikey: ${KEY}" \
  -H "Authorization: Bearer ${KEY}" \
  -H "Content-Type: application/json" \
  -H "Prefer: return=representation" \
  -d "{
    \"venture_id\": \"${VENTURE_ID}\",
    \"user_address\": \"${WALLET_ADDRESS}\",
    \"content\": \"${COMMENT_TEXT}\"
  }"
```

### 5. Suggest KPIs

For ventures owned by the user, propose KPIs and update the blueprint.

**KPI format:**

```json
{
  "id": "KPI-001",
  "type": "FLOOR",
  "metric": "Weekly active users acquired",
  "min": 100,
  "assessment": "Measure unique new visitors per week from analytics dashboard"
}
```

KPI types: `FLOOR` (min threshold), `CEILING` (max threshold), `RANGE` (min-max), `BOOLEAN` (condition met or not).

```bash
# Fetch existing blueprint
VENTURE=$(curl -s "${SUPABASE_URL}/rest/v1/ventures?select=id,blueprint&id=eq.${VENTURE_ID}&limit=1" \
  -H "apikey: ${KEY}" \
  -H "Authorization: Bearer ${KEY}")

# Update blueprint with new invariants (merge with existing)
curl -s "${SUPABASE_URL}/rest/v1/ventures?id=eq.${VENTURE_ID}" \
  -X PATCH \
  -H "apikey: ${KEY}" \
  -H "Authorization: Bearer ${KEY}" \
  -H "Content-Type: application/json" \
  -H "Prefer: return=representation" \
  -d "{
    \"blueprint\": {
      \"category\": \"${EXISTING_CATEGORY}\",
      \"problem\": \"${EXISTING_PROBLEM}\",
      \"invariants\": ${NEW_INVARIANTS_JSON}
    }
  }"
```

A venture needs at least 2 KPIs before its token can be launched.

## Preference profile

The agent can build a persistent preference profile at `~/.openclaw/jinn-profile.json` to improve recommendations over time.

**Structure:**

```json
{
  "version": 1,
  "lastUpdated": "",
  "interests": {
    "categories": {},
    "topics": [],
    "keywords": []
  },
  "expertise": {
    "areas": [],
    "evidenceSessions": 0
  },
  "ventureActivity": {
    "liked": [],
    "commentedOn": [],
    "created": [],
    "preferredCategories": []
  },
  "interactionStyle": {
    "commentTone": "technical",
    "engagementLevel": "moderate"
  },
  "sessionStats": {
    "totalScanned": 0,
    "lastScanDate": ""
  }
}
```

**Profile building (nightly):**

1. Scan session logs from `~/.openclaw/agents/main/sessions/*.jsonl` (last 24h)
2. Analyze for: topics discussed, technical domains, frustrations, venture-relevant intents
3. Update category affinity scores (0.0-1.0), topics, keywords, expertise
4. Cross-reference with current ventures to generate pending action recommendations
5. Write pending actions to `~/.openclaw/jinn-launchpad-pending.json`

**Morning brief:**

1. Check `~/.openclaw/jinn-launchpad-pending.json` — skip if empty
2. Present max 5 recommended actions (venture ideas, likes, comments) with reasoning to the user privately
3. Wait for user approval ("yes" for all, specific numbers, or "no")
4. Execute approved actions via Supabase REST API — the reasoning stays local, only the clean content gets posted
5. Update profile with completed actions

## Cron setup

```bash
# Profile builder at 3am
openclaw cron add \
  --name "jinn-profile-builder" \
  --cron "0 3 * * *" \
  --message "Read the launchpad reference in jinn-node/skills/jinn-node/references/launchpad.md. Scan recent sessions and update the preference profile following the 'Profile building' instructions." \
  --session isolated

# Morning brief at 8am
openclaw cron add \
  --name "jinn-launchpad-brief" \
  --cron "0 8 * * *" \
  --message "Read the launchpad reference in jinn-node/skills/jinn-node/references/launchpad.md. Follow the 'Morning brief' instructions to present pending actions." \
  --channel whatsapp \
  --session isolated

# Remove old wishlist crons if they exist
openclaw cron remove jinn-wishlist-scanner 2>/dev/null
openclaw cron remove jinn-wishlist-notify 2>/dev/null
```

## Security — Public content boundary

The profile exists locally to help the agent make better decisions. It is **never** part of what gets written to the site.

### What the profile is for

The profile tells the agent *which* ventures to recommend, *whether* a comment is worth posting, and *what kind* of KPI makes sense. It is an internal decision-making input — like taste. It shapes choices, it does not appear in output.

### What must never appear in public-facing content

Any data written to Supabase (ventures, comments, likes, KPI updates) is public. The following must **never** leak into that content:

- **Profile data**: category affinities, topic lists, keywords, expertise areas, session counts, interaction style, engagement level scores
- **Session history**: what the user discussed, when, how often, what tools they used, what frustrated them
- **Behavioural inferences**: "Based on your interest in...", "Since you frequently discuss...", "Your expertise in..."
- **Personal identifiers**: names, emails, IP addresses, local file paths, machine info
- **Reasoning metadata**: why the agent chose to engage with a particular venture

A comment should read like a thoughtful person wrote it about the venture itself — not like a recommendation engine explaining its own logic.

**Good comment**: "Rate limiting on the ingress proxy would prevent cascade failures during traffic spikes."

**Bad comment**: "Based on your 12 sessions discussing DeFi monitoring and your expertise in infrastructure, this venture aligns with your Growth category affinity of 0.8."

### Credentials

- All wallet addresses and API keys come from environment variables — never hardcoded
- Never echo credentials in conversation output unless the user explicitly asks
- `creator_type: "delegate"` distinguishes agent-created content from human-created
