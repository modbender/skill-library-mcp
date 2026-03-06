# AgentPay CLI Reference

## Commands

### `agentpay setup`
Interactive setup wizard. Human enters payment credentials, sets passphrase. Creates encrypted vault at `~/.agentpay/vault.enc`.

### `agentpay budget [options]`
View or configure spending limits.

```bash
agentpay budget                        # view current budget
agentpay budget --set 500              # set total budget to $500
agentpay budget --limit-per-tx 100     # max $100 per transaction
```

### `agentpay buy [options]`
Propose, approve, and execute a purchase.

**Required flags:**
- `--merchant <name>` — merchant name (e.g. "Amazon", "Best Buy")
- `--description <desc>` — what you're buying
- `--url <url>` — product or checkout URL

**Optional flags:**
- `--amount <amount>` — purchase amount (auto-detected from page if omitted)
- `--pickup` — select in-store pickup if available

```bash
agentpay buy \
  --merchant "Amazon" \
  --description "USB-C cable, 6ft" \
  --url "https://www.amazon.com/dp/B08..." \
  --amount "12.99"
```

### `agentpay pending`
List all pending purchase proposals awaiting human approval.

### `agentpay approve <txId>`
Approve a pending purchase. Triggers headless browser checkout.

### `agentpay reject <txId> [options]`
Reject a pending purchase.

```bash
agentpay reject tx_abc123 --reason "too expensive"
```

### `agentpay status`
Show wallet status: budget remaining, recent transactions, vault health.

### `agentpay history`
Full transaction history with timestamps, amounts, merchants, and status.

### `agentpay qr [options]`
Display QR code for web-based setup (alternative to CLI setup).

```bash
agentpay qr --budget 200 --message "Scan to set up AgentPay"
```

### `agentpay dashboard [options]`
Open web dashboard for managing AgentPay.

```bash
agentpay dashboard --port 3141
```

### `agentpay mcp [options]`
Start MCP server for direct agent integration.

```bash
agentpay mcp             # stdio transport
agentpay mcp --http      # HTTP transport
```

### `agentpay reset`
Delete all AgentPay data. **Destructive — requires confirmation.**
