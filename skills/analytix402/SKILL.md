# Analytix402

Monitor, control, and optimize your AI agent's API spend and LLM costs in real-time.

## Description

Analytix402 gives your OpenClaw agent financial visibility and guardrails. Track every API call, LLM invocation, and x402 payment your agent makes. Set budget limits, detect duplicate purchases, and get alerts before costs spiral.

**What it does:**
- Tracks all outbound API calls and x402 payments automatically
- Monitors LLM token usage and costs across OpenAI, Anthropic, and other providers
- Enforces daily budget limits and per-call spend caps
- Detects duplicate API purchases to prevent waste
- Sends heartbeats so you know your agent is alive and healthy
- Provides a real-time dashboard at analytix402.com

## Configuration

```yaml
# Required
ANALYTIX402_API_KEY: ax_live_your_key_here

# Optional
ANALYTIX402_AGENT_ID: my-openclaw-agent
ANALYTIX402_BASE_URL: https://analytix402.com
ANALYTIX402_DAILY_BUDGET: 50.00
ANALYTIX402_PER_CALL_LIMIT: 5.00
ANALYTIX402_TRACK_LLM: true
```

## Tools

### analytix402_spend_report
Get a summary of your agent's spend — total cost, breakdown by API and LLM provider, and efficiency score.

### analytix402_set_budget
Set or update the daily budget limit for this agent session.

### analytix402_check_budget
Check remaining budget before making an expensive API call.

### analytix402_flag_purchase
Flag a potential duplicate or unnecessary purchase for review.

## Tags

monitoring, analytics, budget, x402, payments, observability, cost-tracking
