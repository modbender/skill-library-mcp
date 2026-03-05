# ATP — Agent Trade Protocol

Payment settlement system for AI agent services on Solana blockchain. Automatic payment processing based on token usage.

## Components
1. **Settlement Service (Facilitator)** — handles usage parsing, payment calculation, blockchain transactions
   - URL: `https://facilitator.swarms.world`
2. **Middleware** — FastAPI middleware intercepting API responses, encrypting until payment confirmed
3. **Client** — user-facing client for ATP-protected endpoints

## Request Flow
1. Client sends request with wallet private key in header
2. Endpoint processes, returns response with usage data
3. Middleware encrypts response, sends payment request
4. Settlement service calculates cost, creates split transaction on Solana
5. After on-chain confirmation, response is decrypted and returned

## Payment Splitting
- **Treasury:** 5% (default processing fee)
- **Recipient:** 95% (endpoint host's wallet)

## Server Setup

```python
from fastapi import FastAPI
from atp.middleware import ATPSettlementMiddleware
from atp.schemas import PaymentToken

app = FastAPI()
app.add_middleware(
    ATPSettlementMiddleware,
    allowed_endpoints=["/v1/chat"],
    input_cost_per_million_usd=10.0,
    output_cost_per_million_usd=30.0,
    recipient_pubkey="YourSolanaWallet",
    payment_token=PaymentToken.SOL,
    wallet_private_key_header="x-wallet-private-key",
    require_wallet=True,
    settlement_service_url="https://facilitator.swarms.world",
    settlement_timeout=300.0,
    fail_on_settlement_error=False,
)
```

## Client Usage

```python
from atp.client import ATPClient

client = ATPClient(
    wallet_private_key="[1,2,3,...]",
    settlement_service_url="https://facilitator.swarms.world"
)

response = await client.post(
    url="https://api.example.com/v1/chat",
    json={"message": "Hello!"}
)
```

## Supported Usage Formats
- OpenAI: `usage.prompt_tokens` / `completion_tokens`
- Anthropic: `usage.input_tokens` / `output_tokens`
- Google/Gemini: `usageMetadata.promptTokenCount` / `candidatesTokenCount`
- Nested formats auto-detected

## Response Fields (added by middleware)
- `atp_usage` — normalized token counts
- `atp_settlement` — transaction signature, pricing, payment breakdown
- `atp_settlement_status` — "paid" | "failed"

## Environment Variables
- `ATP_SETTLEMENT_URL` — facilitator URL
- `ATP_SETTLEMENT_TIMEOUT` — timeout seconds (default 300)
- `ATP_ENCRYPTION_KEY` — Fernet key for response encryption

## Best Practices
- Never log/persist wallet private keys
- Use `fail_on_settlement_error=False` for graceful degradation
- Increase timeout for blockchain confirmation delays
- Include accurate token counts in responses
- Test with testnet wallets first
