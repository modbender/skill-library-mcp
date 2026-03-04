---
name: deal-works
description: AI agent infrastructure for deals, escrow, attestations, and autonomous agents. 39 tools across 9 engines.
version: 0.1.0
author: swgoettelman
license: MIT
metadata:
  openclaw:
    emoji: "🤝"
    homepage: https://deal.works
    primaryEnv: DEAL_WORKS_API_KEY
    requires:
      env:
        - DEAL_WORKS_API_KEY
      bins:
        - node
    install:
      - kind: node
        package: "@swgoettelman/deal-works-mcp"
        bins: [deal-works-mcp]
    mcp:
      server: "@swgoettelman/deal-works-mcp"
      transport: stdio
tags:
  - deals
  - escrow
  - smart-contracts
  - attestation
  - agents
  - blockchain
  - finance
  - mcp
---

# deal.works

AI agent infrastructure for trustworthy deal-making. Enables agents to create deals, manage escrow, deploy autonomous agents, and issue cryptographic attestations.

## Quick Start

```bash
# Install the skill
openclaw skill add swgoettelman/deal-works

# Set your API key
export DEAL_WORKS_API_KEY=your_key_here

# The skill is now available to your agent
```

Get your API key at [hq.works/settings/api](https://hq.works/settings/api).

## Capabilities

### 9 Engines, 39 Tools

| Engine | Tools | Purpose |
|--------|-------|---------|
| **Deal** | 7 | Deal lifecycle: create, sign, approve, search, timeline |
| **Fund** | 6 | Wallets, transfers, escrow, cashout, agent funding |
| **Bourse** | 5 | Marketplace for templates, skills, integrations |
| **Cadre** | 6 | Deploy and manage autonomous agents |
| **Oath** | 5 | Cryptographic attestations (completed on-chain) |
| **Parler** | 4 | Dispute resolution and governance |
| **Academy** | 3 | Learning platform for deal-making |
| **HQ** | 2 | Dashboard metrics and system health |
| **Clause** | 1 | Contract clause rendering |

### 7 Resources

- `dealworks://profile` - User profile and trust tier
- `dealworks://wallet` - Wallet balances
- `dealworks://deals` - Active deals
- `dealworks://agents` - Deployed agents
- `dealworks://templates` - Available templates
- `dealworks://disputes` - Open disputes
- `dealworks://dashboard` - Key metrics

### 5 Pre-built Prompts

- `escrow-deal` - Create escrow-protected deal workflow
- `deploy-agent` - Deploy agent from skill
- `file-dispute` - File dispute with evidence
- `publish-template` - Publish template to Bourse
- `portfolio-review` - Review deal portfolio

## Common Workflows

### Create an Escrow Deal

```
User: Create a $5000 escrow deal with contractor@example.com for website development

Agent: I'll use deal_create to create the deal, then fund_escrow to lock the funds,
       and oath_attest to prepare completion verification.
```

### Deploy a Monitoring Agent

```
User: Deploy an agent to monitor my active deals and alert on SLA violations

Agent: I'll use bourse_search to find monitoring skills, cadre_deploy to launch
       the agent, and fund_agent_fund to allocate operational budget.
```

### File a Dispute

```
User: The contractor didn't deliver. File a dispute for deal xyz123.

Agent: I'll use deal_get to review the deal, then parler_dispute_file with
       the evidence. The dispute enters the resolution queue.
```

## Tool Reference

### Deal Engine

| Tool | Description |
|------|-------------|
| `deal_list` | List deals with optional status filter |
| `deal_create` | Create a new deal with terms and counterparty |
| `deal_get` | Get detailed deal information |
| `deal_action` | Perform action: SIGN, APPROVE, REJECT, CANCEL, COMPLETE, ARCHIVE |
| `deal_search` | Search deals by text query |
| `deal_timeline` | Get activity timeline for a deal |
| `deal_attachments` | List deal attachments |

### Fund Engine

| Tool | Description |
|------|-------------|
| `fund_balance` | Get wallet balance (available, locked, pending) |
| `fund_transfer` | Transfer funds between wallets |
| `fund_transactions` | List transaction history |
| `fund_escrow` | Lock funds in escrow for a deal |
| `fund_cashout` | Cash out to external wallet on Base |
| `fund_agent_fund` | Fund an agent's operational wallet |

### Bourse Engine

| Tool | Description |
|------|-------------|
| `bourse_search` | Search marketplace for templates/skills |
| `bourse_get` | Get listing details and reviews |
| `bourse_fork` | Fork a listing to customize |
| `bourse_publish` | Publish to marketplace |
| `bourse_earnings` | View earnings from published listings |

### Cadre Engine

| Tool | Description |
|------|-------------|
| `cadre_list` | List deployed agents |
| `cadre_deploy` | Deploy a new agent from skill |
| `cadre_command` | Send command: START, STOP, RESTART, SCALE |
| `cadre_health` | Get agent health status |
| `cadre_delegations` | List permission delegations |
| `cadre_sla_violations` | List SLA violations |

### Oath Engine

| Tool | Description |
|------|-------------|
| `oath_attest` | Create attestation for deal milestone |
| `oath_verify` | Verify attestation authenticity |
| `oath_vault_upload` | Upload document hashes to vault |
| `oath_vault_seal` | Seal vault with Merkle root on-chain |
| `oath_trust_tier` | Get user/org trust tier |

### Parler Engine

| Tool | Description |
|------|-------------|
| `parler_dispute_file` | File a dispute with evidence |
| `parler_dispute_list` | List disputes by status/role |
| `parler_proposals` | List resolution proposals |
| `parler_vote` | Vote on proposal |

### Academy Engine

| Tool | Description |
|------|-------------|
| `academy_courses` | Browse available courses |
| `academy_enroll` | Enroll in a course |
| `academy_tip` | Tip a course creator |

### HQ Engine

| Tool | Description |
|------|-------------|
| `hq_dashboard` | Get dashboard metrics |
| `hq_health` | Check system health |

### Clause Engine

| Tool | Description |
|------|-------------|
| `clause_render` | Render contract clause template |

## Security

- All mutations use idempotency keys (safe to retry)
- API keys scoped per engine
- Rate limited: 100 requests/minute
- Circuit breaker per engine (5 failures = 30s cooldown)
- Only calls *.works domains + approved external APIs

## Links

- [deal.works](https://deal.works) - Main platform
- [Documentation](https://docs.deal.works) - Full API docs
- [npm package](https://www.npmjs.com/package/@swgoettelman/deal-works-mcp)
- [GitHub](https://github.com/swgoettelman/titanium-federation)
