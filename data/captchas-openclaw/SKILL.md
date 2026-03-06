---
name: captchas-openclaw
description: OpenClaw integration guidance for CAPTCHAS Agent API, including OpenResponses tool schemas and plugin tool registration.
homepage: https://captchas.co
metadata: {"openclaw":{"emoji":"🧩","requires":{"env":["CAPTCHAS_API_KEY","CAPTCHAS_ENDPOINT"]},"primaryEnv":"CAPTCHAS_API_KEY"}}
---

# CAPTCHAS + OpenClaw

Use this skill when integrating CAPTCHAS with OpenClaw via OpenResponses tools or OpenClaw plugin tools.

## Configuration

Set environment variables:

- `CAPTCHAS_ENDPOINT` = `https://agent.captchas.co`
- `CAPTCHAS_API_KEY` = `<your-api-key>`

Headers:

- `x-api-key`: required (use `CAPTCHAS_API_KEY`).
- `x-domain`: optional; validated if provided.

Notes:

- `site_key` is optional; if omitted, it resolves from the API key or account default.
- Avoid sending PII in `signals`.

## OpenResponses Tool Schemas (OpenClaw Gateway)

Use the OpenClaw `tools` array shape when calling the Gateway `/v1/responses` endpoint.

```json
{
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "captchas_agent_verify",
        "description": "Run CAPTCHAS Agent Verify and return a decision (allow|deny|challenge).",
        "parameters": {
          "type": "object",
          "properties": {
            "site_key": {"type": "string"},
            "action": {"type": "string"},
            "signals": {"type": "object", "additionalProperties": true},
            "capabilities": {
              "oneOf": [
                {"type": "object", "additionalProperties": true},
                {"type": "array", "items": {"type": "string"}}
              ]
            },
            "verification_mode": {"type": "string", "enum": ["backend_linked", "agent_only"]},
            "challenge_source": {"type": "string", "enum": ["bank", "ai_generated"]},
            "input_type": {"type": "string", "enum": ["choice", "image", "behavioral"]},
            "media_url": {"type": "string"},
            "media_type": {"type": "string"}
          },
          "required": [],
          "additionalProperties": false
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "captchas_agent_challenge_complete",
        "description": "Complete a challenge and mint a verification token when passed.",
        "parameters": {
          "type": "object",
          "properties": {
            "challenge_id": {"type": "string"},
            "site_key": {"type": "string"},
            "answer": {"type": "string"}
          },
          "required": ["challenge_id", "answer"],
          "additionalProperties": false
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "captchas_agent_token_verify",
        "description": "Verify an opaque CAPTCHAS token before completing a sensitive action.",
        "parameters": {
          "type": "object",
          "properties": {
            "token": {"type": "string"},
            "site_key": {"type": "string"},
            "domain": {"type": "string"}
          },
          "required": ["token"],
          "additionalProperties": false
        }
      }
    }
  ]
}
```

## OpenClaw Plugin Tool Registration

Register tools using `api.registerTool(...)` and the same JSON Schema parameters as above.

Example:

```js
api.registerTool({
  name: "captchas_agent_verify",
  description: "Run CAPTCHAS Agent Verify and return a decision (allow|deny|challenge).",
  parameters: {
    type: "object",
    properties: {
      site_key: { type: "string" },
      action: { type: "string" },
      signals: { type: "object", additionalProperties: true }
    },
    required: [],
    additionalProperties: false
  },
  async execute(_id, params) {
    return { content: [{ type: "text", text: JSON.stringify(params) }] };
  }
});
```

## References

- Use `/v1/agent/verify`, `/v1/agent/challenge/:id/complete`, and `/v1/agent/token-verify` as the canonical API calls.
- See `captchas-human-verification/SKILL.md` for workflow guidance.
