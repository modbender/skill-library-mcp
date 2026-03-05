---
name: agentfinobs
description: AI Agent Financial Observability — monitor, budget, and analyze spending across any AI agent. Track costs, set budgets, detect anomalies, and export metrics across payment rails including x402/USDC, Stripe/ACP, Polymarket CLOB, and more.
---

# agentfinobs

AI Agent Financial Observability — monitor, budget, and analyze spending across any AI agent.

## What it does

- **SpendTracker** — Record and settle transactions across any payment rail
- **BudgetManager** — Set spending limits with automatic alerts
- **AnomalyDetector** — Flag unusual spending patterns
- **MetricsEngine** — Track ROI, win rate, burn rate, and runway
- **Dashboard** — Built-in HTTP server for live monitoring
- **Exporters** — Forward data to JSONL, webhooks, or Prometheus

## Usage
```python
from agentfinobs import SpendTracker, BudgetManager, BudgetRule

tracker = SpendTracker(agent_id="my-agent")
budget = BudgetManager(rules=[
    BudgetRule(name="hourly", max_amount=10.0, window_seconds=3600)
])
tracker.add_listener(budget)

tx = tracker.record(amount=2.50, rail="x402_usdc", counterparty="api-provider")
tracker.settle(tx.tx_id, status="confirmed", revenue=5.0)
```

## Install
```bash
pip install agentfinobs
```

## Requirements
- Python 3.10+
