---
name: noya-agent
description: Interact with the Noya AI agent for crypto trading, prediction markets, token analysis, and DCA strategies via curl. Use when the user wants to trade tokens, check portfolios, analyze markets, manage DCA strategies, or interact with Polymarket/Rain prediction markets.
metadata: {"openclaw":{"emoji":"🤖","homepage":"https://agent.noya.ai","requires":{"env":["NOYA_API_KEY"],"bins":["curl","jq"]},"primaryEnv":"NOYA_API_KEY"}}
---

# Noya Agent

Noya is a multi-agent AI system for crypto trading, prediction markets (Polymarket, Rain), token analysis, and DCA strategies. All transactions are gas-sponsored — users pay no gas fees.

- **Website:** [agent.noya.ai](https://agent.noya.ai)
- **API Base URL:** `https://safenet.one`

## Trust & Security

- All API calls use HTTPS. Only `NOYA_API_KEY` is read from the environment.
- All on-chain transactions require explicit user confirmation via an interrupt prompt before execution.
- Use a short-lived API key (30-day) for testing. Revoke it from Settings > API Keys if compromised.

## Setup

1. Create an account at [agent.noya.ai](https://agent.noya.ai)
2. Go to Settings > API Keys and generate a key
3. Store the key securely — it is only shown once
4. Set the environment variable:

```bash
export NOYA_API_KEY="noya_your_key_here"
```

Configure in `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "noya-agent": {
        "enabled": true,
        "apiKey": "noya_your_key_here",
        "env": {
          "NOYA_API_KEY": "noya_your_key_here"
        }
      }
    }
  }
}
```

## When to Use

Use Noya when users want to:
- Check token prices or portfolio balances
- Swap, bridge, or send tokens (cross-chain supported)
- Analyze tokens and market trends
- Trade on Polymarket or Rain prediction markets
- Set up or manage DCA (dollar-cost averaging) strategies
- View DeFi positions

**Don't use for:** Non-crypto tasks, local file operations, or general knowledge questions.

## Core Workflow

Every interaction uses the Noya REST API via curl. The main endpoint is `POST /api/messages/stream` which streams responses. A helper script is provided for this.

### 1. Discover Capabilities (first use)

```bash
curl -s -H "x-api-key: $NOYA_API_KEY" \
  "https://safenet.one/api/agents/summarize" | jq '.data'
```

Returns all available agent types (token analysis, prediction markets, DCA, etc.) and their tools. Call this once to understand what Noya can do.

### 2. Generate a Thread ID (new conversation)

Generate a UUID v4 for each new conversation topic:

```bash
python3 -c "import uuid; print(uuid.uuid4())"
```

Or on macOS/Linux:

```bash
uuidgen | tr '[:upper:]' '[:lower:]'
```

Each conversation needs a unique UUID. Generate one per topic and reuse it for follow-ups.

### 3. Send Messages (streaming)

Use the provided script to send a message and receive the parsed response:

```bash
bash {baseDir}/noya-message.sh "What tokens do I have in my portfolio?" "THREAD_ID_HERE"
```

The script handles the streaming response, parses `--breakpoint--` delimited JSON chunks, and outputs formatted text including messages, tool results, progress indicators, and interrupt prompts.

### 4. Continue the Conversation

Reuse the same thread ID for follow-ups — Noya maintains context:

```bash
bash {baseDir}/noya-message.sh "Swap 0.1 ETH to USDC" "SAME_THREAD_ID"
```

### 5. Respond to Interrupts

When the agent needs confirmation (e.g., before executing a swap), the output includes `[REQUIRES INPUT]` with options. Send the user's answer as a follow-up in the same thread:

```bash
bash {baseDir}/noya-message.sh "Yes" "SAME_THREAD_ID"
```

## API Reference (curl commands)

All endpoints require the `x-api-key` header. Base URL: `https://safenet.one`

### Send Message (streaming) — use the script

```bash
bash {baseDir}/noya-message.sh "<message>" "<threadId>"
```

If you need the raw stream for any reason:

```bash
curl -s -X POST "https://safenet.one/api/messages/stream" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $NOYA_API_KEY" \
  -H "x-timezone-name: America/New_York" \
  -d '{"message": "What is the price of ETH?", "threadId": "YOUR_UUID"}'
```

The raw response is `--breakpoint--\n` delimited JSON chunks with `keep-alive\n\n` pings. Chunk types: `message`, `tool`, `interrupt`, `progress`, `reasonForExecution`, `executionSteps`, `error`.

### List Threads

```bash
curl -s -H "x-api-key: $NOYA_API_KEY" \
  "https://safenet.one/api/threads" | jq '.data.threads'
```

### Get Thread Messages

```bash
curl -s -H "x-api-key: $NOYA_API_KEY" \
  "https://safenet.one/api/threads/THREAD_ID/messages" | jq '.data.messages'
```

### Delete Thread

```bash
curl -s -X DELETE -H "x-api-key: $NOYA_API_KEY" \
  "https://safenet.one/api/threads/THREAD_ID"
```

### Get Agent Summary

```bash
curl -s -H "x-api-key: $NOYA_API_KEY" \
  "https://safenet.one/api/agents/summarize" | jq '.data'
```

### Chat Completion (OpenAI-compatible, no agent tools)

```bash
curl -s -X POST "https://safenet.one/api/chat/completions" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $NOYA_API_KEY" \
  -d '{"sessionId": "SESSION_ID", "message": "Hello, what can you do?"}'
```

### Get Session History

```bash
curl -s -H "x-api-key: $NOYA_API_KEY" \
  "https://safenet.one/api/chat/session/SESSION_ID" | jq '.messages'
```

### Clear Session

```bash
curl -s -X DELETE -H "x-api-key: $NOYA_API_KEY" \
  "https://safenet.one/api/chat/session/SESSION_ID"
```

## Common Patterns

### Check Portfolio
```
User: "What's in my wallet?"

1. Generate a thread ID: uuidgen | tr '[:upper:]' '[:lower:]'
2. bash {baseDir}/noya-message.sh "What tokens do I have in my portfolio?" "$THREAD_ID"
→ Returns wallet address, token balances, and portfolio data
```

### Token Swap
```
User: "Swap 0.5 ETH to USDC"

1. Generate a thread ID
2. bash {baseDir}/noya-message.sh "Swap 0.5 ETH to USDC" "$THREAD_ID"
→ Noya prepares the swap, asks for confirmation (interrupt), then executes.
   All gas fees are sponsored. User must confirm before execution.
3. bash {baseDir}/noya-message.sh "Yes" "$THREAD_ID"  # after user confirms
```

### Token Analysis
```
User: "Analyze SOL for me"

1. Generate a thread ID
2. bash {baseDir}/noya-message.sh "Give me a detailed analysis of SOL" "$THREAD_ID"
→ Returns price data, market trends, and analysis
```

### DCA Strategy
```
User: "Set up a DCA for ETH"

1. Generate a thread ID
2. bash {baseDir}/noya-message.sh "Set up a weekly DCA strategy for ETH with $50" "$THREAD_ID"
→ Noya configures the DCA strategy and confirms details
```

### Prediction Markets
```
User: "What are the top Polymarket events?"

1. Generate a thread ID
2. bash {baseDir}/noya-message.sh "Show me the top trending Polymarket events" "$THREAD_ID"
→ Returns current events, markets, and trading options
```

## Important Notes

### Transaction Confirmation
Noya always asks for user confirmation before executing on-chain transactions (swaps, bridges, transfers, orders). The response will include a `[REQUIRES INPUT]` section with details and options. Always relay this to the user and send their answer as a follow-up in the same thread. Never auto-confirm transactions.

### Wallet Delegation (Website Only)
If Noya responds with a **delegation request**, the user must complete this on the website:
```
"To delegate your wallet, visit https://agent.noya.ai and click
'Delegate Wallet' in the chat. This is a one-time action."
```

### Safe Deployment (Website Only)
If Noya responds with a **Safe deployment request**, the user must complete this on the website:
```
"To deploy your Polymarket Safe, visit https://agent.noya.ai and click
'Deploy Safe Now'. This is free, takes ~30 seconds, and only needs to be done once."
```

## Error Handling

| Error | Solution |
|-------|----------|
| `401 Unauthorized` | API key is invalid, expired, or revoked. Generate a new one at agent.noya.ai |
| `400 Bad Request` | Missing `message` or `threadId` in request body |
| `429 Rate limit` | Wait a few minutes. Limit is 15 requests per 5-minute window |

## Scripts

This skill includes the following script in its directory:

| Script | Purpose |
|--------|---------|
| `noya-message.sh` | Send a message to the Noya agent and parse the streamed response. Usage: `bash {baseDir}/noya-message.sh "<message>" "<threadId>"` |

## Additional Resources

- For the complete REST API specification, see [{baseDir}/reference.md](reference.md)
