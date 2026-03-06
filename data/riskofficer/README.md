# RiskOfficer Skill for OpenClaw

Manage investment portfolios, calculate risk metrics (VaR, Monte Carlo, Stress Tests), optimize allocations, and automatically generate optimal portfolios — all through natural language chat.

**Required:** One env var — `RISK_OFFICER_TOKEN` (create in RiskOfficer app → Settings → API Keys).  
**Source:** [github.com/mib424242/riskofficer-openclaw-skill](https://github.com/mib424242/riskofficer-openclaw-skill) · [riskofficer.tech](https://riskofficer.tech)

## Features

- **Ticker Search** — Find any stock by name or symbol (MOEX, NYSE, NASDAQ, Crypto), get current prices and currency info
- **Portfolio Management** — View, create, edit, and delete portfolios; long & short positions supported
- **Risk Calculations** — VaR (free, 3 methods), Monte Carlo simulation, Stress Tests against historical crises
- **Portfolio Optimization** — Risk Parity (ERC) and Calmar Ratio; long-only, long-short, or unconstrained
- **Auto Portfolio Generation** — Automatically construct optimal portfolios using Max Sharpe, HRP, or Max Calmar strategies
- **Broker Integration** — Sync from Tinkoff/T-Bank; connect, refresh, and disconnect brokers
- **Multi-currency** — RUB/USD with automatic CBR-rate conversion in aggregated portfolio
- **Active Snapshot Selection** — Run risk calculations on any historical version of your portfolio

## Installation

### 1. Get your API Token

1. Open RiskOfficer app on iOS
2. Go to **Settings → API Keys**
3. Create a new token named "OpenClaw"
4. Copy the token (starts with `ro_pat_...`)

### 2. Install the Skill

**Option A: Install via ClawHub (recommended)**

```bash
clawhub install riskofficer
```

Skill catalog page: [clawhub.ai/mib424242/riskofficer](https://clawhub.ai/mib424242/riskofficer)

**Option B: Clone to workspace (per-agent)**

```bash
cd ~/.openclaw/workspace/skills
git clone https://github.com/mib424242/riskofficer-openclaw-skill riskofficer
```

**Option C: Clone to managed skills (shared across all agents)**

```bash
cd ~/.openclaw/skills
git clone https://github.com/mib424242/riskofficer-openclaw-skill riskofficer
```

### 3. Configure the Token

Add to `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "riskofficer": {
        "enabled": true,
        "apiKey": "ro_pat_your_token_here"
      }
    }
  }
}
```

Or set environment variable:

```bash
export RISK_OFFICER_TOKEN="ro_pat_your_token_here"
```

## Usage Examples

```
"Show my portfolios"
"What's the current price of Tesla?"
"Find the ticker for Sberbank"
"Calculate VaR for my main portfolio"
"Run Monte Carlo simulation for 1 year"
"Run stress test — COVID scenario"
"Optimize my portfolio using Risk Parity"
"Optimize my portfolio by Calmar Ratio"
"Add 50 shares of SBER to my portfolio"
"Create a long-short portfolio: long SBER 100, short YNDX 50"
"Show all my portfolios combined in USD"
"Calculate risks for my portfolio as it was last month"
"Compare my portfolio to last week"
"Delete my test portfolio"
"Disconnect Tinkoff broker"
"Create an investment portfolio for 500K rubles"
"Build me a safe portfolio for $10,000"
"What assets are available for auto-generation?"

# Russian / Русский
"Покажи мои риски"
"Оптимизируй портфель по Калмару"
"Посчитай VaR как было месяц назад"
"Добавь Газпром в портфель"
"Собери портфель на 500 тысяч"
"Надёжный портфель на 10 тысяч долларов"
```

## Subscription

All features are **currently FREE** for all users:

| Feature | Tier |
|---------|------|
| VaR calculation (historical, parametric, GARCH) | Free |
| Monte Carlo Simulation | Quant (free during beta) |
| Stress Testing | Quant (free during beta) |
| Portfolio Optimization (Risk Parity + Calmar) | Quant (free during beta) |
| Auto Portfolio Generation (Max Sharpe, HRP, Max Calmar) | Quant (free during beta) |

## API Coverage

This skill covers the full RiskOfficer API:

| Category | Endpoints |
|----------|-----------|
| Ticker Search | Search by name/ticker/ISIN, current prices, historical data |
| Portfolio | List, snapshot, history, diff, aggregated, create, update, delete |
| Broker | Connect, list, sync, disconnect; Tinkoff and Alfa |
| Risk | VaR (3 methods), Monte Carlo, Stress Test, calculation history |
| Optimization | Risk Parity, Calmar Ratio, Auto Generate, apply; long/short/unconstrained modes |
| Active Snapshot | Pin historical snapshot for risk calculations |
| Subscription | Check status |

## Links

- **ClawHub:** [clawhub.ai/mib424242/riskofficer](https://clawhub.ai/mib424242/riskofficer) — `clawhub install riskofficer`
- **GitHub:** [github.com/mib424242/riskofficer-openclaw-skill](https://github.com/mib424242/riskofficer-openclaw-skill)
- **App Store:** [RiskOfficer](https://apps.apple.com/ru/app/riskofficer/id6757360596)
- **Website:** [riskofficer.tech](https://riskofficer.tech)
- **Forum:** [forum.riskofficer.tech](https://forum.riskofficer.tech)
- **Support:** support@riskofficer.tech

## License

MIT

---

**Security:** This skill contains only Markdown and documented API examples (curl). No executables or scripts — compatible with ClawHub/VirusTotal scanning.

**Skill v3.0.0 — Scope disclaimer: virtual portfolios, analysis and research only; no real broker orders.**
