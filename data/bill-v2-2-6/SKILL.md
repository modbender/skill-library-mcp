---
name: AI Bill Intelligence
description: Real-time billing dashboard for OpenClaw. Accurate token-based cost
  tracking across 12+ AI providers.
---

# AI Bill Intelligence

Real-time billing dashboard for OpenClaw. Accurate token-based cost tracking across 12+ AI providers.

## 🚀 Installation
```bash
openclaw skill install https://github.com/fumabot16-max/bill-project
```

## 🛠 Usage
The skill operates via a background collector. As an agent, you can help the user by:
1. **Reporting Usage**: Read `/root/.openclaw/workspace/bill_project/dist/usage.json` to summarize spending.
2. **Updating Balances**: Redirect the user to the `/setup` page or update `vault.json` on their behalf.
3. **Checking Health**: Ensure the `ai-bill` service and `collector.js` are running.

## ⚙️ Configuration
- **Port**: Default is `8003`.
- **Modes**: `prepaid`, `postpaid`, `subscribe`, `unused` (off).

## 📂 Managed Files (Declarations)
This skill manages the following data files inside the `app/` directory:
- `app/vault.json`: User-defined balances and payment modes.
- `app/prices.json`: AI model pricing data.
- `app/cumulative_usage.json`: Archived costs from expired sessions.
- `app/dist/usage.json`: Real-time aggregated usage data for the dashboard.
- `app/debug.log`: Collector activity logs.

Built by Tiger Jung & Chloe (@fumarole16-afk).
<!-- Sync trigger: Fri Feb 20 22:36:10 KST 2026 -->
