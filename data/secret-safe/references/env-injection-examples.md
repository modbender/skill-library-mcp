# Env Injection Examples: Common API Integrations

Copy-paste frontmatter and shell patterns for popular services.

---

## OpenAI / Anthropic

```yaml
metadata: {"openclaw": {"requires": {"env": ["OPENAI_API_KEY"]}, "primaryEnv": "OPENAI_API_KEY"}}
```

```bash
# Safe curl
curl -s https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4o","messages":[{"role":"user","content":"Hello"}]}'
```

```yaml
metadata: {"openclaw": {"requires": {"env": ["ANTHROPIC_API_KEY"]}, "primaryEnv": "ANTHROPIC_API_KEY"}}
```

---

## GitHub

```yaml
metadata: {"openclaw": {"requires": {"env": ["GITHUB_TOKEN"]}, "primaryEnv": "GITHUB_TOKEN"}}
```

```bash
# Using gh CLI — key injected via env, never in command args
GH_TOKEN=$GITHUB_TOKEN gh api /repos/owner/repo/issues
```

---

## Stripe

```yaml
metadata: {"openclaw": {"requires": {"env": ["STRIPE_SECRET_KEY"]}, "primaryEnv": "STRIPE_SECRET_KEY"}}
```

```bash
curl -s https://api.stripe.com/v1/customers \
  -u "$STRIPE_SECRET_KEY:"
# Note: -u USER:PASS format — key goes in the colon-separated user field, not echoed
```

---

## Slack

```yaml
metadata: {"openclaw": {"requires": {"env": ["SLACK_BOT_TOKEN"]}, "primaryEnv": "SLACK_BOT_TOKEN"}}
```

```bash
curl -s -X POST https://slack.com/api/chat.postMessage \
  -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"channel\":\"#general\",\"text\":\"Hello\"}"
```

---

## Google / GCP

```yaml
metadata: {"openclaw": {"requires": {"env": ["GOOGLE_APPLICATION_CREDENTIALS"]}, "primaryEnv": "GOOGLE_APPLICATION_CREDENTIALS"}}
```

```bash
# GCP uses a credentials FILE path, not the key itself
# GOOGLE_APPLICATION_CREDENTIALS should point to the JSON file path
gcloud auth activate-service-account --key-file="$GOOGLE_APPLICATION_CREDENTIALS"
```

> Note: Never read and echo the contents of the credentials file — pass only the file path.

---

## AWS

```yaml
metadata: {"openclaw": {"requires": {"env": ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]}, "primaryEnv": "AWS_ACCESS_KEY_ID"}}
```

```bash
# AWS CLI picks up env vars automatically — no need to pass them explicitly
aws s3 ls s3://my-bucket
```

---

## Twilio

```yaml
metadata: {"openclaw": {"requires": {"env": ["TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN"]}, "primaryEnv": "TWILIO_AUTH_TOKEN"}}
```

```bash
curl -s -X POST "https://api.twilio.com/2010-04-01/Accounts/$TWILIO_ACCOUNT_SID/Messages.json" \
  --data-urlencode "From=+15551234567" \
  --data-urlencode "To=+15559876543" \
  --data-urlencode "Body=Hello" \
  -u "$TWILIO_ACCOUNT_SID:$TWILIO_AUTH_TOKEN"
```

---

## Multiple Keys Pattern

When a skill needs several keys, list all in `requires.env`:

```yaml
metadata: {"openclaw": {"requires": {"env": ["SERVICE_API_KEY", "SERVICE_WEBHOOK_SECRET"]}, "primaryEnv": "SERVICE_API_KEY"}}
```

In `openclaw.json`, the user adds:
```json
{
  "skills": {
    "entries": {
      "my-skill": {
        "env": {
          "SERVICE_API_KEY": "sk-...",
          "SERVICE_WEBHOOK_SECRET": "whsec-..."
        }
      }
    }
  }
}
```

---

## Python Script Pattern

If your skill uses a Python script, inject the key via env — never via argparse:

```python
import os
import sys

api_key = os.environ.get("MY_SERVICE_API_KEY")
if not api_key:
    print("ERROR: MY_SERVICE_API_KEY is not set.", file=sys.stderr)
    sys.exit(1)

# Use api_key — never print it, never include in exceptions
```

**Dangerous pattern to avoid:**
```python
# WRONG — key appears in error output which goes back to agent context
try:
    response = call_api(api_key)
except Exception as e:
    print(f"API call failed with key {api_key}: {e}")  # DO NOT DO THIS
```
