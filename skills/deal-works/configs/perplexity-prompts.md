# deal.works Perplexity Computer Prompts

Pre-built prompts for common multi-agent workflows using deal.works MCP tools.

## Setup

1. Install the deal.works MCP connector in Perplexity Mac app
2. Set your `DEAL_WORKS_API_KEY` environment variable
3. Copy any prompt below and paste into Perplexity

---

## Prompt 1: Escrow Deal Creation

**Use case**: Create a protected deal with automatic escrow

```
I need to create an escrow-protected deal. Here are the details:

- Counterparty: [EMAIL]
- Amount: $[AMOUNT]
- Description: [WHAT THE DEAL IS FOR]
- Due date: [DATE]

Please:
1. Use deal_create to create the deal with these terms
2. Use fund_balance to check I have sufficient funds
3. Use fund_escrow to lock the amount for this deal
4. Use oath_attest to prepare a completion attestation template
5. Summarize the deal ID, escrow status, and next steps

Confirm each step before proceeding.
```

**Expected token usage**: ~3,000-4,000 tokens

---

## Prompt 2: Deploy Monitoring Agent

**Use case**: Deploy an autonomous agent to monitor deals and alert on issues

```
Deploy a monitoring agent for my deal.works account:

- Budget: [AMOUNT] Talers
- Monitor: Active deals, SLA violations, escrow status
- Alert on: Late deliveries, low balance, agent failures

Steps:
1. Use bourse_search to find monitoring/alerting skills
2. Show me the top 3 options with quality scores
3. After I choose, use cadre_deploy to launch the agent
4. Use fund_agent_fund to allocate the budget
5. Use cadre_health to verify the agent is running
6. Show me the agent ID and how to check its status later
```

**Expected token usage**: ~4,000-5,000 tokens

---

## Prompt 3: Portfolio Review

**Use case**: Comprehensive review of your deal.works portfolio

```
Give me a complete portfolio review:

1. Use deal_list to show all active deals with status
2. Use fund_balance to show wallet balances (available, locked, pending)
3. Use cadre_list to show deployed agents and their health
4. Use cadre_sla_violations to check for any SLA issues
5. Use hq_dashboard to get key metrics for this week

Summarize:
- Total deal volume and value
- Funds in escrow vs available
- Agent performance metrics
- Any items needing immediate attention

Format as a structured report.
```

**Expected token usage**: ~5,000-6,000 tokens

---

## Prompt 4: Dispute Resolution

**Use case**: File and manage a dispute for a problematic deal

```
I need to file a dispute for deal [DEAL_ID]:

Reason: [NON_DELIVERY / QUALITY_ISSUE / LATE_DELIVERY / PAYMENT_DISPUTE]
Description: [DETAILED DESCRIPTION OF THE ISSUE]

Please:
1. Use deal_get to retrieve the deal details
2. Use deal_timeline to show the activity history
3. Use oath_verify to check any existing attestations
4. Use parler_dispute_file to file the dispute with my description
5. Use parler_dispute_list to confirm the dispute is registered
6. Explain the resolution process and timeline
```

**Expected token usage**: ~4,000-5,000 tokens

---

## Prompt 5: Marketplace Publishing

**Use case**: Publish a deal template to earn passive income

```
I want to publish a deal template to the Bourse marketplace:

Template name: [NAME]
Category: [freelance / consulting / real-estate / saas / other]
Description: [WHAT THIS TEMPLATE IS FOR]
Price: [AMOUNT] Talers (0 for free)

Steps:
1. Use bourse_search to check for similar templates
2. Show me competing templates and their prices
3. Based on the market, recommend a price point
4. Use bourse_publish to create the listing
5. Use bourse_get to confirm it's live
6. Explain how I'll earn from forks and usage
```

**Expected token usage**: ~3,000-4,000 tokens

---

## Multi-Step Workflow: Complete Deal Lifecycle

**Use case**: End-to-end deal from creation to completion

```
Guide me through a complete deal lifecycle:

Deal: [DESCRIPTION]
Counterparty: [EMAIL]
Amount: $[AMOUNT]
Deliverable: [WHAT WILL BE DELIVERED]

Phase 1 - Setup:
1. deal_create with terms
2. fund_escrow to lock funds
3. Share deal link with counterparty

Phase 2 - Execution (after counterparty signs):
4. deal_action SIGN to co-sign
5. oath_vault_upload for any documents
6. cadre_deploy a reminder agent (optional)

Phase 3 - Completion:
7. Verify deliverable received
8. oath_attest COMPLETION with evidence
9. deal_action COMPLETE to release escrow
10. fund_transactions to confirm payment

Track progress and prompt me at each phase.
```

**Expected token usage**: ~6,000-8,000 tokens (full lifecycle)

---

## Token Consumption Notes

| Workflow | Est. Tokens | Sonar Model |
|----------|-------------|-------------|
| Simple query | 1,000-2,000 | sonar |
| Escrow deal | 3,000-4,000 | sonar-pro |
| Agent deploy | 4,000-5,000 | sonar-pro |
| Portfolio review | 5,000-6,000 | sonar-pro |
| Dispute filing | 4,000-5,000 | sonar-pro |
| Full lifecycle | 6,000-8,000 | sonar-reasoning-pro |

Perplexity Max subscribers: Unlimited queries. Pro subscribers: Check your quota at perplexity.ai/settings.
