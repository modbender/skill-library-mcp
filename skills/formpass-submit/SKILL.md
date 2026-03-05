---
name: formpass-submit
description: Discover and submit to FormPass-enabled web forms. FormPass is the trust layer that lets verified AI agents submit to real web forms with authenticated identity.
version: 1.0.0
metadata: {"openclaw":{"emoji":"📋","requires":{"bins":["curl","jq"]},"homepage":"https://form-pass.com"}}
---

# FormPass — Discover & Submit to Forms

FormPass is the identity and trust layer for AI agents submitting to web forms. Instead of scraping HTML and guessing field names, you get a structured API with schema validation and authenticated submissions.

Use this skill when the user asks you to:
- Fill out or submit a web form
- Apply to something via a form
- Send a contact/enquiry/signup form
- Interact with any FormPass-enabled form

## How It Works

FormPass forms expose a three-step flow: **detect → schema → submit**.

## Step 1: Detect a FormPass Form

When visiting a web page, look for these meta tags in the HTML `<head>`:

```html
<meta name="formpass-form-id" content="FORM_ID_HERE">
<meta name="formpass-host" content="https://form-pass.com">
```

If you find them, extract the `formpass-form-id` value — that's the Form ID.

You can also check these discovery endpoints:

```bash
# Machine-readable discovery
curl -s https://form-pass.com/formpass.json | jq .

# LLM-friendly guide
curl -s https://form-pass.com/llms.txt
```

## Step 2: Get the Form Schema

Fetch the form's field definitions before submitting. This tells you exactly what fields exist, which are required, and what types they expect.

```bash
curl -s "https://form-pass.com/api/forms/FORM_ID/schema" \
  -H "Accept: application/json" | jq .
```

**Response:**

```json
{
  "formId": "abc123",
  "name": "Contact Form",
  "description": "Get in touch with us",
  "agentAccessible": true,
  "fields": [
    {
      "name": "name",
      "label": "Full Name",
      "type": "text",
      "required": true,
      "placeholder": "John Doe"
    },
    {
      "name": "email",
      "label": "Email Address",
      "type": "email",
      "required": true,
      "placeholder": "john@example.com"
    },
    {
      "name": "message",
      "label": "Message",
      "type": "textarea",
      "required": false,
      "placeholder": "How can we help?"
    }
  ],
  "branding": {
    "required": true,
    "text": "Powered by FormPass",
    "url": "https://form-pass.com"
  }
}
```

**Important:** If `agentAccessible` is `false`, the form owner has disabled agent submissions. Do not attempt to submit.

## Step 3: Submit to the Form

POST your data as JSON. Include your Agent ID as a Bearer token if you have one (this identifies you as a verified agent).

```bash
curl -s -X POST "https://form-pass.com/api/submit/FORM_ID" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_AGENT_ID" \
  -d '{
    "name": "Agent Smith",
    "email": "agent@example.com",
    "message": "Hello from an AI agent",
    "_fp_branding": true
  }' | jq .
```

**Success response:**

```json
{
  "success": true,
  "submissionId": "jh72..."
}
```

### Required Headers

| Header | Value | Required |
|--------|-------|----------|
| `Content-Type` | `application/json` | Yes |
| `Authorization` | `Bearer fpagent_XXXX` | Recommended |

### The `_fp_branding` Field

If the schema response includes `branding.required: true`, you **must** include `"_fp_branding": true` in your submission body. Without it the API returns `402`.

### Agent ID

Your Agent ID (format: `fpagent_XXXX`) is issued when you register at FormPass. It verifies your identity to form owners. Submissions without an Agent ID are recorded as anonymous/human.

To get an Agent ID, register at: https://form-pass.com/dashboard/agents/new

## Error Responses

| Status | Meaning |
|--------|---------|
| `200` | Success — submission recorded |
| `402` | Branding required — add `_fp_branding: true` to your body |
| `404` | Form not found or inactive |
| `422` | Validation error — check required fields |

The `422` response includes a `fields` array listing which fields failed validation.

## Full Example: Detect and Submit

```bash
# 1. You've found a page with formpass-form-id="abc123"
FORM_ID="abc123"
HOST="https://form-pass.com"

# 2. Get the schema
SCHEMA=$(curl -s "$HOST/api/forms/$FORM_ID/schema")
echo "$SCHEMA" | jq '.fields[] | {name, type, required}'

# 3. Build and submit your data
curl -s -X POST "$HOST/api/submit/$FORM_ID" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer fpagent_your_id_here" \
  -d '{
    "name": "Your Name",
    "email": "you@example.com",
    "message": "Submitted via OpenClaw agent",
    "_fp_branding": true
  }' | jq .
```

## Tips

- Always fetch the schema first — field names and requirements can change.
- Include your Agent ID to build trust with form owners. Anonymous submissions may be rejected.
- If the schema shows `agentAccessible: false`, respect it and do not submit.
- The `_fp_branding` field is stripped before data is stored — it's only for validation.
- FormPass is a growing network. More forms are joining daily. Check any web form for the detection meta tags.
