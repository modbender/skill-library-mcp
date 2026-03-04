# Testing Windfall — What to Expect

Hey! Thanks for testing this. Here's everything you need.

## What it is

Windfall is a spatially-routed LLM inference gateway. It's OpenAI-compatible — you point your agent's base URL at Windfall instead of OpenAI/Anthropic directly, and it auto-routes each call to the cheapest model that fits the task, caches repeated prompts, and runs everything on the cleanest available energy. Two env vars to switch, nothing else changes in your code.

**Endpoint:** `https://windfall.ecofrontiers.xyz/v1/chat/completions`

## How to get started

1. Create an API key:
   ```bash
   curl -X POST https://windfall.ecofrontiers.xyz/api/keys \
     -H "Content-Type: application/json" \
     -d '{"wallet_address": "0xYOUR_WALLET", "label": "testing"}'
   ```
2. Save the key (it's shown once)
3. Set two env vars:
   ```
   OPENAI_BASE_URL=https://windfall.ecofrontiers.xyz/v1
   OPENAI_API_KEY=wf_YOUR_KEY
   ```
4. Your existing OpenAI SDK calls work as-is

## Free tier

You get 50 free requests with a wallet address (100 if you have a Basename or are in the Base agent registry). No payment needed to start.

## Credits and restrictions

- Free requests: 50–100 depending on identity tier
- After free tier: $0.003/request (standard models like DeepSeek V3) or $0.008/request (premium models like Claude, GPT-4o)
- Top up by sending USDC or ETH on Base directly to the gateway wallet (Stripe card payments are in test mode — not live yet)
- `max_tokens` is capped at 8,192 per request
- Rate limit: 60 requests/minute

## Models available

- **Default:** DeepSeek V3 (handles most tasks, 91% cheaper than Claude)
- **Premium:** Claude 3.5 Sonnet, GPT-4o, Llama 3.1 405B, and 200+ more via OpenRouter
- You can specify any model explicitly with the `model` field, or let Windfall auto-select based on task complexity

## Routing modes

Set via `x-routing-mode` header:

| Mode | Behavior |
|------|----------|
| `cheapest` | Lowest cost model + node |
| `greenest` | Lowest carbon intensity node (default) |
| `balanced` | Weighted combination |

## What to test

### 1. Drop-in compatibility
Point your existing agent at Windfall. Does it work without code changes? Any edge cases with streaming, tool use, function calling?

### 2. Model routing
Send a mix of simple tasks (status checks, lookups) and complex tasks (multi-step reasoning, code generation). Does Windfall route simple tasks to cheaper models correctly? You can check which model was used in the response headers.

### 3. Caching
Send the same prompt twice. Second response should be faster and free (cache hit). Try with slight variations to see where the semantic cache boundary is.

### 4. Latency
Compare response times to direct API calls. The routing adds a small overhead — is it noticeable for your use case? Check the `response_time_ms` in responses.

### 5. Modes
Try all three routing modes (`cheapest`, `greenest`, `balanced`). Do the cost/quality tradeoffs make sense for your agent's workflow?

### 6. Error handling
What happens when you exceed rate limits? Send a bad request? Use an expired key? Are the error messages useful?

### 7. Dashboard
Go to [windfall.ecofrontiers.xyz/dashboard](https://windfall.ecofrontiers.xyz/dashboard), connect your wallet or paste your API key. Does it show your usage correctly? Are the savings numbers believable?

### 8. Onchain payment (optional)
If you want to test the crypto top-up flow: send a small amount of USDC on Base to the gateway wallet (shown at `/api/deposit-address`). Credits should appear within 60 seconds.

## Timeline

No hard deadline — take a week or so. But the earlier feedback the better since we're iterating on this actively.

## What I'm most interested in

- Does the drop-in replacement actually work for your agent without friction?
- Is the latency overhead acceptable?
- Does the cost savings math check out vs what you're paying now?
- Any rough edges in the developer experience?

## Links

- **Status:** [windfall.ecofrontiers.xyz/status](https://windfall.ecofrontiers.xyz/status)
- **Landing page:** [windfall.ecofrontiers.xyz](https://windfall.ecofrontiers.xyz)
- **Dashboard:** [windfall.ecofrontiers.xyz/dashboard](https://windfall.ecofrontiers.xyz/dashboard)

Let me know if you hit any issues — the system logs everything so I can debug on my end.
