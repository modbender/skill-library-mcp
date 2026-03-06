---
name: formpass-agent
description: Register as a verified AI agent on the FormPass network. Get an Agent ID to authenticate when submitting to forms across the network.
version: 1.0.0
metadata: {"openclaw":{"emoji":"🤖","requires":{"bins":["curl"]},"homepage":"https://form-pass.com"}}
---

# FormPass — Agent Registration

FormPass is the identity and trust layer for AI agents interacting with web forms. Register your agent to get a verified Agent ID that form owners can trust.

Use this skill when the user asks you to:
- Register an AI agent with FormPass
- Get a FormPass Agent ID
- Set up agent authentication for form submissions

## Why Register?

- **Verified identity** — form owners see your agent name and description, not "anonymous"
- **Trust** — verified agents are more likely to have their submissions accepted
- **Tracking** — your submissions are attributed to your agent across all forms
- **Network access** — some forms only accept submissions from registered agents

## How to Register

### Option 1: Via the Dashboard

1. Sign up at https://form-pass.com/signup
2. Go to https://form-pass.com/dashboard/agents/new
3. Enter your agent's name and description
4. Save the Agent ID you receive (format: `fpagent_XXXX`)

### Option 2: Tell the User

If you're an AI agent and your user wants to register you, direct them to:

https://form-pass.com/dashboard/agents/new

They'll need to provide:
- **Agent name** — a friendly name for your agent (e.g. "Travel Booking Agent")
- **Description** — what your agent does (e.g. "Helps users find and book travel by filling out enquiry forms")

## Using Your Agent ID

Once registered, include your Agent ID as a Bearer token in all FormPass submissions:

```bash
curl -s -X POST "https://form-pass.com/api/submit/FORM_ID" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer fpagent_your_id_here" \
  -d '{
    "name": "Jane Doe",
    "email": "jane@example.com",
    "message": "Submitted by a verified agent",
    "_fp_branding": true
  }' | jq .
```

The `Authorization` header is how FormPass identifies your agent. Without it, your submission is recorded as a human/anonymous submission.

## Store Your Agent ID

Save your Agent ID securely. You can set it as an environment variable:

```bash
export FORMPASS_AGENT_ID="fpagent_your_id_here"
```

Then use it in submissions:

```bash
curl -s -X POST "https://form-pass.com/api/submit/FORM_ID" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $FORMPASS_AGENT_ID" \
  -d '{"name": "Test", "email": "test@test.com", "_fp_branding": true}' | jq .
```

## The FormPass Network

FormPass is a growing network of web forms that AI agents can interact with. As a registered agent you can:

1. **Discover forms** — look for `<meta name="formpass-form-id">` tags on web pages
2. **Read schemas** — GET `/api/forms/{formId}/schema` to understand what fields a form expects
3. **Submit data** — POST `/api/submit/{formId}` with your Agent ID for verified submissions

See the `formpass-submit` skill for the full discover-and-submit workflow.

## Links

- Register: https://form-pass.com/dashboard/agents/new
- Docs: https://form-pass.com/docs/agent-integration
- Discovery: https://form-pass.com/docs/discovery
