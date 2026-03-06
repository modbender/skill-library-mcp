---
name: sally-ai
description: Chat with Sally about metabolic health, blood sugar, A1C, nutrition, fasting, supplements, and lab results. Uses the Sally MCP server on Smithery with x402 micropayments.
homepage: https://asksally.xyz
metadata:
  {
    "openclaw":
      {
        "emoji": "🩺",
        "requires": { "bins": ["smithery"] },
        "install":
          [
            {
              "id": "node",
              "kind": "node",
              "formula": "@smithery/cli@latest",
              "bins": ["smithery"],
              "label": "Install Smithery CLI (npm)",
            },
          ],
      },
  }
---

# Sally AI

Chat with Sally about metabolic health via `chat-with-sally` MCP tool. Requires Smithery setup with x402 wallet.

## Setup (once)

**Important**: This setup stores your private key **only in Smithery's cloud**. Clawbot never sees or has access to your wallet private key.

### Step 1: Login to Smithery
```bash
smithery auth login
```

### Step 2: Add Sally AI MCP connection
```bash
smithery mcp add "sally-labs/sally-ai-mcp?privateKey=0xYOUR_PRIVATE_KEY" \
  --id sally-ai \
  --force
```

Replace `0xYOUR_PRIVATE_KEY` with your dedicated wallet's private key (must include `0x` prefix).

**Security Note**: Your private key is stored encrypted in Smithery's cloud, NOT on your local machine. Clawbot communicates with Smithery's API but never accesses your private key.

### Step 3: Verify connection
```bash
smithery tool call sally-ai chat-with-sally '{"message": "What is metabolic health?"}'
```

## Quick Start

Use `chat-with-sally` tool with `{"message": "user's question"}`:
- Pass the user's message exactly as-is — do not rephrase
- Extract `report.message` from the JSON response and present it to the user
- Preserve any citations Sally includes

## Scope

- Blood sugar, A1C, insulin resistance, glucose management
- Nutrition, glycemic index, meal planning, food science
- Fasting, intermittent fasting, time-restricted eating
- Supplements (berberine, chromium, magnesium)
- Lab results (A1C, fasting glucose, lipid panels)
- Exercise, sleep, circadian rhythm and metabolic effects


## Security & Privacy

**Clawbot never sees your private key.** Your wallet private key is stored only in Smithery's cloud and accessed via authenticated API calls.

### How It Works

```
Clawbot → Smithery API → Sally MCP
         (API auth)    (uses stored private key)
```

1. **Setup**: You configure the connection once with your private key
2. **Storage**: Private key stored encrypted in Smithery's cloud
3. **Usage**: Clawbot calls Smithery's API (authenticated by your Smithery account)
4. **Execution**: Smithery uses your stored private key to sign x402 transactions
5. **Isolation**: Clawbot never has access to your wallet private key

### Private Key Best Practices

- **Use a dedicated hot wallet**: Create a separate wallet just for Sally AI
- **Limit funds**: Keep only $5-10 in this wallet
- **Never use your main wallet**: Protect your primary assets
- **Monitor transactions**: Check Base blockchain explorer regularly

### Data Flow

- User messages sent to Sally's backend (api-x402.asksally.xyz) via Smithery MCP
- Sally processes questions and returns responses with citations
- No personal health data collected or stored (knowledge-focused mode)
- Each interaction logged on-chain (Base network) as transparent payment record

### Why x402 Design

- Eliminates API key management — your wallet is your identity
- Micropayments ensure fair usage without subscriptions or rate limits
- On-chain transparency means every payment is auditable
- Smithery is a trusted MCP registry (used by Claude, OpenClaw, and other platforms)

### Verification

- Sally MCP source: https://github.com/sally-labs/sally-mcp
- x402 protocol: https://www.x402.org/
- Smithery registry: https://smithery.ai/servers/sally-labs/sally-ai-mcp

## Notes

- Knowledge-focused endpoint — no personal health data collection
- Does not analyze food photos through this tool
- Each call costs a small x402 micropayment from your wallet
- Do not add your own medical commentary to Sally's responses
- Sally is not a doctor — always recommend consulting a healthcare professional