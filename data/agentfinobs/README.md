# agentfinobs

**Agent Financial Observability — "Datadog for Agent Payments"**

Monitor, budget, and analyze spending across any AI agent, regardless of payment rail.

```
pip install agentfinobs
```

## Quick Start

```python
from agentfinobs import ObservabilityStack

obs = ObservabilityStack.create(
    agent_id="my-agent",
    budget_rules=[
        {"name": "hourly", "max_amount": 50, "window_seconds": 3600},
        {"name": "daily", "max_amount": 200, "window_seconds": 86400,
         "halt_on_breach": True},
    ],
    total_budget=1000.0,
    dashboard_port=9400,
)

# Record a spend
tx = obs.track(amount=1.50, task_id="task-1", description="API call")

# Settle with outcome
obs.settle(tx.tx_id, revenue=2.00)

# Check before spending
ok, reason = obs.can_spend(50.0)

# Get metrics snapshot
snap = obs.snapshot()
print(f"ROI: {snap.roi_pct:.1f}%  Burn: ${snap.burn_rate_per_hour:.2f}/hr")
```

## Features

- **SpendTracker** — Thread-safe transaction recording with JSONL persistence
- **BudgetManager** — Real-time budget enforcement with configurable rules
- **MetricsEngine** — ROI, cost/task, burn rate, runway estimation
- **AnomalyDetector** — Statistical anomaly detection (z-score, Welford's algorithm)
- **Dashboard** — Zero-dependency HTTP server serving JSON metrics
- **Exporters** — Pluggable: JSONL, Webhook, Prometheus, or build your own

## Zero Dependencies

The core SDK uses only Python stdlib. Optional integrations:

```
pip install agentfinobs[prometheus]   # Prometheus/Grafana
pip install agentfinobs[webhook]      # Webhook export (httpx)
pip install agentfinobs[all]          # Everything
```

## Payment Rail Agnostic

Works with any agent payment method:

| Rail | Status |
|------|--------|
| x402 / USDC | Supported |
| Stripe / ACP | Supported |
| Visa TAP | Supported |
| Mastercard Agent Pay | Supported |
| Circle Nanopayments | Supported |
| Polymarket CLOB | Supported |
| Custom | Extend `PaymentRail` enum |

## Dashboard

Start the built-in dashboard:

```python
obs = ObservabilityStack.create(dashboard_port=9400)
```

Endpoints:
- `GET /metrics` — Full metrics snapshot
- `GET /metrics/1h` — Last hour
- `GET /metrics/24h` — Last 24 hours
- `GET /budget` — Budget headroom and halt status
- `GET /alerts` — Budget + anomaly alerts
- `GET /txs/recent` — Last 50 transactions
- `GET /healthz` — Health check

## License

MIT
