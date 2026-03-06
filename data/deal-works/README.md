# @swgoettelman/deal-works-mcp

MCP (Model Context Protocol) server exposing the deal.works platform to AI agents. Provides 39 tools across 9 engines for deal management, escrow, agent deployment, attestations, and more.

## Installation

```bash
npx @swgoettelman/deal-works-mcp
```

Or install globally:

```bash
npm install -g @swgoettelman/deal-works-mcp
```

## Configuration

### Environment Variables

```bash
export DEAL_WORKS_API_KEY=your_api_key_here
```

Get your API key from [hq.works/settings/api](https://hq.works/settings/api).

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "deal-works": {
      "command": "npx",
      "args": ["@goettelman/deal-works-mcp"],
      "env": {
        "DEAL_WORKS_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

### Cursor / VS Code

Add to your MCP configuration:

```json
{
  "deal-works": {
    "command": "npx",
    "args": ["@goettelman/deal-works-mcp"],
    "env": {
      "DEAL_WORKS_API_KEY": "your_api_key_here"
    }
  }
}
```

### OpenClaw

```bash
openclaw skill add goettelman/deal-works
```

## Tools (39 total)

### Deal Engine (7 tools)
- `deal_list` - List deals with status filter
- `deal_create` - Create a new deal
- `deal_get` - Get deal details
- `deal_action` - Perform deal actions (sign, approve, reject, etc.)
- `deal_search` - Search deals by query
- `deal_timeline` - Get deal activity timeline
- `deal_attachments` - List deal attachments

### Fund Engine (6 tools)
- `fund_balance` - Get wallet balance
- `fund_transfer` - Transfer funds between wallets
- `fund_transactions` - List transaction history
- `fund_escrow` - Lock funds in escrow for a deal
- `fund_cashout` - Cash out to external wallet
- `fund_agent_fund` - Fund an agent's operational wallet

### Bourse Engine (5 tools)
- `bourse_search` - Search marketplace for templates/skills
- `bourse_get` - Get listing details
- `bourse_fork` - Fork a listing
- `bourse_publish` - Publish to marketplace
- `bourse_earnings` - View earnings from published listings

### Cadre Engine (6 tools)
- `cadre_list` - List deployed agents
- `cadre_deploy` - Deploy a new agent
- `cadre_command` - Send command to agent (start/stop/restart)
- `cadre_health` - Get agent health status
- `cadre_delegations` - List permission delegations
- `cadre_sla_violations` - List SLA violations

### Oath Engine (5 tools)
- `oath_attest` - Create attestation for a deal
- `oath_verify` - Verify attestation authenticity
- `oath_vault_upload` - Upload documents to secure vault
- `oath_vault_seal` - Seal vault with Merkle root
- `oath_trust_tier` - Get user/org trust tier

### Parler Engine (4 tools)
- `parler_dispute_file` - File a dispute
- `parler_dispute_list` - List disputes
- `parler_proposals` - List resolution proposals
- `parler_vote` - Vote on proposals

### Academy Engine (3 tools)
- `academy_courses` - Browse courses
- `academy_enroll` - Enroll in a course
- `academy_tip` - Tip a course creator

### HQ Engine (2 tools)
- `hq_dashboard` - Get dashboard metrics
- `hq_health` - Check system health

### Clause Engine (1 tool)
- `clause_render` - Render contract clause template

## Resources (7 total)

- `dealworks://profile` - User profile and trust tier
- `dealworks://wallet` - Wallet balances
- `dealworks://deals` - Active deals
- `dealworks://agents` - Deployed agents
- `dealworks://templates` - Available templates
- `dealworks://disputes` - Open disputes
- `dealworks://dashboard` - Key metrics

## Prompts (5 total)

- `escrow-deal` - Create escrow-protected deal workflow
- `deploy-agent` - Deploy agent from skill
- `file-dispute` - File dispute with evidence
- `publish-template` - Publish template to Bourse
- `portfolio-review` - Review deal portfolio

## Example Usage

### Create an Escrow Deal

```
User: Create a $5000 escrow deal with contractor@example.com for website development

Claude: I'll help you create an escrow-protected deal. Let me:
1. Create the deal
2. Set up escrow
3. Prepare attestation for completion
```

### Deploy an Agent

```
User: Deploy a monitoring agent with a $100 budget

Claude: I'll search for monitoring skills and deploy an agent:
1. Searching Bourse for monitoring skills...
2. Deploying agent with SLA configuration...
3. Funding agent wallet...
```

## Security

- API keys are scoped per engine
- All mutations use idempotency keys
- Rate limited to 100 requests/minute
- Circuit breaker per engine (5 failures = 30s cooldown)
- Only calls *.works domains + approved external APIs

## License

MIT

## Links

- [deal.works](https://deal.works)
- [Documentation](https://docs.deal.works)
- [API Reference](https://docs.deal.works/api)
- [GitHub](https://github.com/goettelman/deal.works)
