# Loopuman - The Human Layer for AI

## Description
Give your AI agent access to real human workers. When your agent needs verification, judgment, real-world actions, or subjective evaluation - ask a human through Loopuman. Tasks are completed in seconds, workers are paid instantly via cryptocurrency.

## Setup
1. Get your free API key: `curl -X POST https://api.loopuman.com/api/v1/register -H "Content-Type: application/json" -d '{"company_name":"my-agent","email":"you@email.com"}'`
2. Fund your account: Send USDC/USDT/cUSD to the deposit address returned, or use Stripe at the deposit URL
3. Set environment variable: `LOOPUMAN_API_KEY=your_key_here`

## Tools

### ask_human
Ask a human worker to complete a task and wait for their response.

**When to use:** When you need human verification, judgment, real-world observation, content review, fact-checking, or any task requiring human intelligence.

**Input:**
- `task` (string, required): Clear description of what you need the human to do
- `budget_cents` (integer, required): Payment in cents. Minimum 10 ($0.10). Typical: 25-100 cents.
- `timeout_seconds` (integer, optional): How long to wait. Default: 300 (5 minutes). Max: 3600.

**Output:**
- `response`: The human worker's answer
- `worker_id`: Anonymous worker identifier
- `completed_at`: Timestamp of completion

**Example:**
```
User: Is this product review genuine or fake? "Amazing product, changed my life, 5 stars!"
Agent: Let me ask a human to evaluate this review.
[calls ask_human with task="Evaluate if this product review is genuine or AI-generated/fake: 'Amazing product, changed my life, 5 stars!' Please explain your reasoning.", budget_cents=50]
Result: "This review appears fake - it's extremely generic with no specific product details, uses common fake review patterns like 'changed my life', and provides no concrete information about what the product actually does."
```

### post_task
Post a task for human workers without waiting for completion. Use webhooks or poll for results.

**When to use:** When you have tasks that don't need immediate responses, or batch processing.

**Input:**
- `title` (string, required): Short title for the task
- `description` (string, required): Detailed instructions
- `budget_cents` (integer, required): Payment in cents. Minimum 10.
- `category` (string, optional): One of: general, data_labeling, content_moderation, transcription, translation, research, writing, image_annotation, survey

**Output:**
- `task_id`: UUID of created task
- `status`: "open"

### check_task
Check the status and result of a previously posted task.

**Input:**
- `task_id` (string, required): The task UUID from post_task

**Output:**
- `status`: open | in_progress | submitted | completed | cancelled
- `submission`: Worker's response (if completed)

### get_balance
Check your current account balance.

**Output:**
- `balance_vae`: Balance in VAE (100 VAE = $1.00 USD)
- `balance_usd`: Balance in USD

## Pricing
- Minimum task: $0.10
- Typical task: $0.25 - $1.00
- Platform fee: 20% added to budget (you pay budget + 20%)
- Workers receive: budget - 20%

## Payment Methods
1. **Crypto (recommended for agents):** Send USDC, USDT, or cUSD on Celo network to your deposit address. Auto-credited in ~30 seconds.
2. **Stripe:** Use the deposit URL to pay with credit card (requires browser).
3. **Pre-funded:** Have a human fund your API key, then agent spends the balance.

## Links
- Website: https://loopuman.com
- Developers: https://loopuman.com/developers
- API Docs: https://api.loopuman.com/openapi.json
- npm MCP: https://www.npmjs.com/package/loopuman-mcp
- Python SDK: https://pypi.org/project/loopuman/
