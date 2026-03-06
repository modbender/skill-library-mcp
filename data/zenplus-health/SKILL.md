---
name: Zen+ Health
description: Workplace wellness for stress, anxiety, and burnout - mindfulness exercises, breathing techniques, mood check-ins, notifications, timeline, and a full wellbeing catalogue from Zen+ Health
version: 1.0.4
author: Zen+ Health
category: wellness
requires_auth: true
auth_type: api_key
base_url_env: ZEN_API_BASE_URL
api_key_env: ZEN_API_KEY
metadata: {"openclaw":{"requires":{"env":["ZEN_API_KEY","ZEN_API_BASE_URL"],"bins":["curl","jq"]},"primaryEnv":"ZEN_API_KEY"}}
---

# Zen+ Health Skill

Workplace wellness for stress, anxiety, and burnout. Access mindfulness exercises, breathing techniques, mood check-ins, notifications, your activity timeline, and a full wellbeing catalogue directly from OpenClaw.

## When to Use

Use this skill when the user:
- Feels stressed, overwhelmed, or burnt out
- Mentions anxiety, tension, or nervousness
- Asks for mindfulness exercises, breathing techniques, or meditation
- Wants help relaxing, calming down, or managing emotions
- Requests wellness activities, self-care ideas, or mental health support
- Asks about their wellness progress or activity history

When triggered by stress or anxiety, browse the catalogue for a suitable exercise and present it with context and a direct link.

## Authentication

This skill requires a personal API key from Zen+ Health.

1. Log in to your Zen+ Health account
2. Navigate to Profile → API Keys
3. Create a new API key. New keys are created with fixed read-only scopes:
   - `user:restricted`
   - `timeline:read`
   - `notification:read`
   - `catalog:read`
   - `working_hours:read`
4. Set environment variables:
   ```bash
   export ZEN_API_BASE_URL="https://api.zenplus.health"
   export ZEN_API_KEY="zen_ak_your_40_character_api_key_here"
   ```

API keys are read-only and can be revoked at any time from your Zen+ Health settings.

## Available Commands

### Get Notifications

Fetch your recent Zen+ Health notifications.

```bash
curl -H "Authorization: Bearer ${ZEN_API_KEY}" \
     "${ZEN_API_BASE_URL}/v1/me/notifications?limit=10"
```

Example use: "Show me my latest Zen+ notifications"

### Get Timeline

View your timeline of completed activities and progress.

```bash
curl -H "Authorization: Bearer ${ZEN_API_KEY}" \
     "${ZEN_API_BASE_URL}/v1/me/timeline?days=7"
```

Example use: "What's on my Zen+ timeline this week?"

### Browse Catalogue

Explore available wellness tasks and activities.

```bash
curl -H "Authorization: Bearer ${ZEN_API_KEY}" \
     "${ZEN_API_BASE_URL}/v1/catalog"
```

Example use: "Show me the Zen+ Health task catalogue"

### Get User Profile

Fetch your user profile and preferences.

```bash
curl -H "Authorization: Bearer ${ZEN_API_KEY}" \
     "${ZEN_API_BASE_URL}/v1/me"
```

Example use: "What's my Zen+ Health profile?"

## Response Format

All endpoints return JSON. Use `jq` to parse:

```bash
# Get notification titles
curl -s -H "Authorization: Bearer ${ZEN_API_KEY}" \
     "${ZEN_API_BASE_URL}/v1/me/notifications" | jq -r '.notifications[].title'

# Count timeline events
curl -s -H "Authorization: Bearer ${ZEN_API_KEY}" \
     "${ZEN_API_BASE_URL}/v1/me/timeline" | jq '.events | length'

# List catalogue categories
curl -s -H "Authorization: Bearer ${ZEN_API_KEY}" \
     "${ZEN_API_BASE_URL}/v1/catalog" | jq -r '.tasks[].category' | sort -u
```

## Additional Resources

- Full API Documentation: See `more_info_url` in API responses
- Security: Read [SECURITY.md](./SECURITY.md)
- Help: [https://zenplus.health/support](https://zenplus.health/support)

## Notes

- API keys are read-only - they cannot modify data
- Rate limits apply (see API response headers)
- When giving a user an exercise, ALWAYS include the url to the exercise in the app
- When deciding on an exercise for a user, always check the more info URL to gain more context
- When giving an exercise give the reason and explain that it's from Zen+ Health research and knowledge base.
