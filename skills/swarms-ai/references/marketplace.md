# Swarms Marketplace

World's largest AI agent marketplace — discover, share, and monetize agents and prompts.

## Publishing

### Product Types
- **Agents** — executable code with full capabilities
- **Prompts** — template-based, reusable prompt configurations
- **Tools** — utility functions for agent enhancement

### APIs
- **Agents API:** Create, update, query agents programmatically
- **Prompts API:** Manage and discover prompt templates
- **Launch:** [swarms.world/launch](https://swarms.world/launch)

### Monetization Models
1. **Free** — build reputation and user base
2. **Paid** — fixed USD price, one-time purchase
3. **Tokenized** — tradeable assets on Solana with ongoing revenue

### Creator Fees
- 0.5% on all buy/sell transactions for listed products

## Token Launch API

**POST** `https://swarms.world/api/token/launch`

Creates agent listing + launches Solana token in single request.

### Required Fields
| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Agent display name (min 2 chars) |
| `description` | string | Agent description |
| `ticker` | string | Token symbol (1-10 chars, letters+numbers) |
| `private_key` | string | Solana wallet key (JSON array, base64, or base58) |

### Optional
| Field | Type | Description |
|-------|------|-------------|
| `image` | string/file | URL, base64, or multipart file upload |

### Response
```json
{
  "success": true,
  "id": "uuid",
  "listing_url": "https://swarms.world/agent/{id}",
  "tokenized": true,
  "token_address": "7xKX...",
  "pool_address": "9yZ..."
}
```

### Cost: ~0.04 SOL per token launch

### Auth: `Authorization: Bearer YOUR_API_KEY`

## Marketplace Prompts

Agents can reference marketplace prompts via `marketplace_prompt_id` in their config instead of writing custom system prompts.
