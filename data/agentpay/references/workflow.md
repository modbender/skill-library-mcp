# AgentPay Purchase Workflow

## Full Purchase Flow

```
Agent finds product → Agent proposes purchase (buy command)
→ Human reviews pending mandate → Human approves (approve command)
→ Headless browser opens merchant site → Navigates to product
→ Adds to cart → Fills checkout form → Injects credentials from vault
→ Submits order → Captures confirmation → Logs receipt
```

## Step-by-step

### 1. Agent proposes
The agent runs `agentpay buy` with merchant, description, URL, and amount. This creates a **purchase mandate** — a structured record of what the agent wants to buy.

### 2. Human reviews
The human runs `agentpay pending` to see all proposals. Each shows: merchant, item, amount, URL, timestamp, and the agent that proposed it.

### 3. Human approves
The human runs `agentpay approve <txId>`. This cryptographically signs the mandate with Ed25519, binding the approval to the specific purchase details.

### 4. Checkout executes
A headless browser (Stagehand/Browserbase):
1. Navigates to the merchant URL
2. Handles product selection and cart
3. Fills shipping/contact information
4. Injects payment credentials from the encrypted vault
5. Submits the order
6. Captures confirmation details

**The raw card number exists in the browser DOM only during form submission. Recording is disabled during credential injection.**

### 5. Receipt logged
A cryptographic receipt is written to disk: merchant, amount, items, timestamp, confirmation number, human signature. This survives context loss and reboots.

## Error Handling

| Error | Cause | Recovery |
|-------|-------|----------|
| Vault locked | Wrong passphrase or vault not set up | Human runs `agentpay setup` |
| Budget exceeded | Purchase exceeds remaining budget | Inform human, ask to increase budget |
| Per-tx limit exceeded | Single purchase too large | Inform human, ask to raise limit |
| Checkout failed | Bot detection, page changed, timeout | Check `agentpay status`, report error to human |
| Mandate expired | Human didn't approve in time | Re-propose the purchase |
| Merchant unavailable | Site down or URL invalid | Verify URL, try again later |

## Security Model

- **AES-256-GCM** encrypted vault — credentials at rest
- **Ed25519** signed mandates — human approval is cryptographic, not just "yes"
- **Local-first** — no servers, no cloud, nothing leaves the machine
- **Audit trail** — every transaction logged with verifiable receipts
- **Spending limits** — budget cap and per-transaction cap
- **Zero-knowledge agent** — the agent never sees raw credentials
