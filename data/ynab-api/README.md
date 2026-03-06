# YNAB Budget Management Skill

Complete automation toolkit for YNAB (You Need A Budget) with goal tracking, spending analysis, and daily budget reports.

## Features

- 📊 **Goal Progress Tracking** with visual bars
- 📅 **Scheduled Transaction Alerts** (never miss bills)
- 💰 **Age of Money Monitoring** (financial health)
- 📈 **Month-over-Month Comparison** (spot trends)
- ⚠️ **Overspending Alerts** (stay on budget)
- 🔄 **Automated Daily Check** (morning WhatsApp summary)
- 🎯 **Smart Categorization** (learn from history)
- 💸 **Real Transfer Support** (properly linked)

## Quick Start

1. Install the skill:
```bash
clawhub install ynab-api
```

2. Get your YNAB API token: https://app.ynab.com/settings/developer

3. Create config file `~/.config/ynab/config.json`:
```json
{
  "api_key": "YOUR_TOKEN_HERE",
  "budget_id": "YOUR_BUDGET_ID"
}
```

4. Test it:
```bash
/home/node/clawd/skills/ynab-api/scripts/goals-progress.sh
```

5. Set up automated reports (recommended):
```bash
# One-command setup - creates all recommended cron jobs
/home/node/clawd/skills/ynab-api/scripts/setup-automation.sh

# Preview first (dry run)
/home/node/clawd/skills/ynab-api/scripts/setup-automation.sh --dry-run
```

This creates:
- Daily Budget Check (7:15 AM)
- Weekly Spending Review (Monday 8 AM)
- Mid-Month Goal Check (15th, 9 AM)
- Upcoming Bills Alert (10 AM daily)

## Available Scripts

All scripts in `scripts/` directory:

- `goals-progress.sh` - Show goal progress with visual bars
- `scheduled-upcoming.sh` - List upcoming scheduled transactions
- `month-comparison.sh` - Compare spending month-over-month
- `transfer.sh` - Create proper account transfers
- `daily-budget-check.sh` - Comprehensive morning report

## Full Documentation

See `SKILL.md` for:
- Complete API best practices
- Transfer transaction guide (critical!)
- Automation setup examples
- Troubleshooting
- Security tips

## Example Daily Report

```
☀️ BUDGET CHECK MATTUTINO

💰 Age of Money: 141 giorni ✅

📅 Prossime uscite (7gg)
• Domani: Netflix €12.99

⚠️ Alert Budget Superato
• Eating Out: €178 / €150 (+€28)

🎯 Obiettivi in ritardo
• Gym: 8% (€22/€270)
```

## License

MIT License - Free to use and modify

## Support

- YNAB API Docs: https://api.ynab.com
- ClawHub: https://clawhub.com
- Issues: Open on GitHub

---

Made with ❤️ for the OpenClaw community
