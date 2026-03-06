---
name: business-account-opening
description: >
  Open a Vivid Business account via a remote MCP server. Collects legal
  entity data from the user in chat, then calls build_onboarding_link to
  generate a pre-filled onboarding URL. The tool only creates a link —
  no bank account is opened and no financial data is accessed. No local
  install or credentials required.
version: 0.1.0
disable-model-invocation: true

metadata:
  openclaw:
    emoji: "🏦"
    homepage: "https://github.com/vivid-money/vivid-mcp"
    disable-model-invocation: true
    requires:
      env: []
      bins: []
      config: []
---

# Business Account Opening

Open a Vivid Business account using a remote MCP server hosted by Vivid Money.

## Integration

| Property | Value |
|----------|-------|
| **Endpoint** | `https://api.prime.vivid.money/mcp` |
| **Transport** | Streamable HTTP (remote) |
| **Tool** | `build_onboarding_link` |
| **Auth** | None — the endpoint is publicly accessible. The tool only generates a pre-filled onboarding link; it does not create a bank account, access financial data, or perform any privileged operation. Identity verification happens later in the Vivid app. |

### MCP client config

Add this to your MCP client configuration to connect:

```json
{
  "mcpServers": {
    "vivid-mcp": {
      "type": "http",
      "url": "https://api.prime.vivid.money/mcp"
    }
  }
}
```

### Tool schema

`build_onboarding_link` accepts a single `legal_entity_data` object with the basic data
The tool returns an onboarding URL. No sensitive financial data is returned.

## Trigger

User wants to open a business account or start business onboarding.

## Flow

1. Ask for **legal entity type** (GmbH, UG, freelancer, etc.) if not provided.
2. Ask for **country** if not provided. Default: Germany.
3. Call MCP to get required fields
4. If the user uploads a document, extract the fields **locally in the AI client** — the document itself is never sent to the MCP server. Summarize what was extracted; do not echo raw document contents.
5. Show the user a summary of all collected data and **ask for explicit confirmation** before proceeding.
6. Only after user confirms: call `build_onboarding_link` with the confirmed data.
7. Present the returned onboarding URL to the user.

## Data handling

- **Documents stay local.** Uploaded files are parsed by the AI client. Only the structured fields listed above are sent to the MCP server — never the raw document.
- **No PII stored by the skill.** The skill itself does not persist any data. The MCP server creates an onboarding session on Vivid's platform; Vivid's privacy policy governs from that point: https://vivid.money/en-eu/privacy-policy/
- **No credentials in chat.** Never ask for or accept passwords, API keys, or bank account numbers.
- **What the tool sends.** Only the fields in the schema table above. No file content, no chat history, no device metadata.

## Rules

- Always confirm collected data with the user before calling `build_onboarding_link`.
- This skill must only be invoked by explicit user request — never autonomously.
- Treat uploaded documents as sensitive — summarize only, don't echo contents.
- On error: ask for missing fields or suggest a different document.
