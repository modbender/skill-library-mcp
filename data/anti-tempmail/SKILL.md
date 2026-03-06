---
name: antitempmail
description: "Validate email addresses against temporary/disposable email providers using AntiTempMail API. Detect throwaway emails to protect your services."
metadata:
  {
    "openclaw":
      {
        "emoji": "📧",
        "requires": { "bins": ["curl"] },
      },
  }
---

# AntiTempMail Skill

Validate email addresses to detect temporary/disposable email providers. Protect your services from throwaway accounts.

## Setup

Set your API key as an environment variable:

```bash
export ANTITEMPMAIL_API_KEY="your_api_key_here"
```

Get your API key from: https://antitempmail.com/dashboard

## Commands

### Check Single Email

```bash
curl -X POST https://antitempmail.com/api/v1/email/check \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $ANTITEMPMAIL_API_KEY" \
  -d '{"email": "test@tempmail.com"}'
```

Response:
```json
{
  "email": "test@tempmail.com",
  "isTemporary": true,
  "domain": "tempmail.com",
  "provider": "TempMail",
  "risk": "high"
}
```

### Check Multiple Emails (Bulk)

```bash
curl -X POST https://antitempmail.com/api/v1/email/check/bulk \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $ANTITEMPMAIL_API_KEY" \
  -d '{
    "emails": [
      "user1@gmail.com",
      "user2@tempmail.com",
      "user3@10minutemail.com"
    ]
  }'
```

Response:
```json
{
  "results": [
    {
      "email": "user1@gmail.com",
      "isTemporary": false,
      "domain": "gmail.com",
      "risk": "low"
    },
    {
      "email": "user2@tempmail.com",
      "isTemporary": true,
      "domain": "tempmail.com",
      "provider": "TempMail",
      "risk": "high"
    },
    {
      "email": "user3@10minutemail.com",
      "isTemporary": true,
      "domain": "10minutemail.com",
      "provider": "10MinuteMail",
      "risk": "high"
    }
  ],
  "summary": {
    "total": 3,
    "temporary": 2,
    "legitimate": 1
  }
}
```

## Usage Examples

### Validate User Registration

When a user signs up, check if their email is temporary:

```bash
EMAIL="newuser@example.com"
RESULT=$(curl -s -X POST https://antitempmail.com/api/v1/email/check \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $ANTITEMPMAIL_API_KEY" \
  -d "{\"email\": \"$EMAIL\"}")

IS_TEMP=$(echo $RESULT | jq -r '.isTemporary')

if [ "$IS_TEMP" = "true" ]; then
  echo "⚠️  Temporary email detected! Registration blocked."
else
  echo "✅ Valid email. Proceeding with registration."
fi
```

### Clean Email List

Filter out temporary emails from a list:

```bash
# Read emails from file (one per line)
EMAILS=$(cat email_list.txt | jq -R . | jq -s .)

curl -X POST https://antitempmail.com/api/v1/email/check/bulk \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $ANTITEMPMAIL_API_KEY" \
  -d "{\"emails\": $EMAILS}" | \
  jq '.results[] | select(.isTemporary == false) | .email'
```

## Response Fields

- `email`: The validated email address
- `isTemporary`: Boolean indicating if it's a temporary email
- `domain`: Email domain
- `provider`: Name of the temporary email provider (if detected)
- `risk`: Risk level (`low`, `medium`, `high`)
- `confidence`: Detection confidence score (0-100)

## Error Handling

Common errors:

- `401 Unauthorized`: Invalid or missing API key
- `429 Too Many Requests`: Rate limit exceeded
- `400 Bad Request`: Invalid email format

## Rate Limits

- Free tier: 100 requests/day
- Pro tier: 10,000 requests/day
- Enterprise: Custom limits

Check your usage at: https://antitempmail.com/dashboard/credits

## Notes

- API responses are cached for 24 hours
- Bulk endpoint supports up to 100 emails per request
- All requests are logged for security and analytics
