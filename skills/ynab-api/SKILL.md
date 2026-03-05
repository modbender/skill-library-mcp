---
name: ynab-api
description: YNAB (You Need A Budget) comprehensive budget management with automated tracking, goal monitoring, spending analysis, and daily budget check reports. Ready-to-use scripts included.
user-invocable: true
metadata: {"clawdbot":{"emoji":"💰","requires":{"env":["YNAB_API_KEY","YNAB_BUDGET_ID"]}}}
---

# YNAB Budget Management

Complete YNAB budget automation toolkit with best practices, automated monitoring, and ready-to-use helper scripts.

## ✨ Features

- 📊 **Goal Progress Tracking** - Monitor category goals with visual progress bars
- 📅 **Scheduled Transaction Alerts** - Never miss upcoming bills
- 💰 **Age of Money Monitoring** - Track financial stability
- 📈 **Month-over-Month Analysis** - Compare spending trends
- ⚠️ **Overspending Alerts** - Get notified when exceeding budgets
- 🔄 **Automated Daily Check** - Morning budget summary via WhatsApp/Telegram
- 🎯 **Smart Categorization** - Learn from transaction history
- 💸 **Real Transfer Support** - Properly linked account transfers

## 🚀 Quick Start

This skill provides best practices for managing YNAB budgets via API, including transaction categorization, data consistency, and automated workflows.

## 📋 Installation & Setup

### 1. Get Your YNAB API Key

1. Go to https://app.ynab.com/settings/developer
2. Click "New Token" and copy your Personal Access Token
3. Get your Budget ID from the YNAB URL (e.g., `https://app.ynab.com/abc123...` → `abc123...`)

### 2. Configure the Skill

Create config file at `~/.config/ynab/config.json`:

```json
{
  "api_key": "YOUR_YNAB_TOKEN_HERE",
  "budget_id": "YOUR_BUDGET_ID_HERE"
}
```

Or set environment variables:
```bash
export YNAB_API_KEY="your_token"
export YNAB_BUDGET_ID="your_budget_id"
```

### 3. Set Up Automated Reports (Recommended)

**🚀 ONE-COMMAND SETUP:**

```bash
/home/node/clawd/skills/ynab-api/scripts/setup-automation.sh
```

This interactive script creates all recommended cron jobs:
- ✅ **Daily Budget Check** (7:15 AM) - Age of Money, upcoming bills, alerts
- ✅ **Weekly Spending Review** (Monday 8:00 AM) - Month comparison
- ✅ **Mid-Month Goal Check** (15th, 9:00 AM) - Category goals progress
- ✅ **Upcoming Bills Alert** (10:00 AM daily) - Next 2 days transactions

**Preview changes first:**
```bash
/home/node/clawd/skills/ynab-api/scripts/setup-automation.sh --dry-run
```

**Manual setup (alternative):**

If you prefer to create cron jobs manually:

```bash
openclaw cron add --name "Daily Budget Check" \
  --schedule "15 7 * * *" \
  --session isolated \
  --model gemini-flash \
  --delivery announce \
  --task "Run YNAB daily budget check and send via WhatsApp"
```

### 4. Test Your Setup

Run a quick test:
```bash
/home/node/clawd/skills/ynab-api/scripts/goals-progress.sh
```

If you see your budget goals, you're all set! 🎉

## Core Best Practices

### 1. Always Categorize Immediately

**Never** create transactions without a category. Uncategorized transactions break budget tracking.

When adding a transaction, categorize it at creation time—don't defer.

### 2. Check Transaction History for Unknown Merchants

When you encounter an unfamiliar merchant/payee:

1. Search YNAB for past transactions with the same payee name
2. Use the same category as previous transactions
3. Maintain consistency with historical categorization

**Why**: This preserves categorization consistency and reduces user interruptions.

Example:
```bash
# Search for past transactions by payee
curl -s "https://api.ynab.com/v1/budgets/$BUDGET_ID/transactions" \
  -H "Authorization: Bearer $API_KEY" | \
  jq '.data.transactions[] | select(.payee_name | contains("MERCHANT_NAME"))'
```

### 3. Check for Pending Transactions Before Adding

Before creating a new transaction:
1. Check if an unapproved transaction already exists for the same amount
2. If found → approve it and update payee/memo if needed
3. If not found → create new transaction

**Why**: Avoids duplicates from imported bank transactions.

### 4. Use Milliunits for Amounts

YNAB API uses **milliunits** for all amounts:
- €10.00 = `10000` (positive for income)
- -€10.00 = `-10000` (negative for expenses)

**Always** divide by 1000 when displaying, multiply by 1000 when submitting.

### 5. Monthly Expense Calculation

When calculating monthly spending:
- Only count transactions with `amount < 0` (actual expenses)
- Consider excluding non-discretionary categories like:
  - Tax payments (mandatory, not spending choices)
  - Advances/reimbursements (temporary, not true expenses)
  - Uncategorized (often transfers/investments)
  - Extraordinary one-time expenses (if tracking discretionary budget)

**Note**: Exclusion rules depend on your budget goals. Configure your specific exclusions in a local config or notes file.

### 6. Handle Split Transactions

Transactions with category "Split" contain `subtransactions`.

**Never** show "Split" as a category in reports—always expand to subcategories:

```bash
# For each split transaction
if [ "$category_name" = "Split" ]; then
  for subtx in subtransactions; do
    echo "$subtx.category_name: $subtx.amount"
  done
fi
```

### 7. Transfer Transactions (CRITICAL)

**⚠️ IMPORTANT**: To create a **real** transfer that YNAB recognizes as linked transactions between accounts, you MUST use the account's `transfer_payee_id`, NOT a payee name.

#### How Transfers Work

Each account has a special field `transfer_payee_id` - this is the payee ID that represents transfers TO that account.

**✅ CORRECT - Real Transfer**:
```bash
# Transfer from Account A to Account B
# Get Account B's transfer_payee_id first, then:
curl -X POST "$YNAB_API/budgets/$BUDGET_ID/transactions" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"transaction\": {
      \"account_id\": \"ACCOUNT_A_ID\",
      \"date\": \"2026-02-21\",
      \"amount\": -50000,
      \"payee_id\": \"ACCOUNT_B_TRANSFER_PAYEE_ID\",
      \"approved\": true
    }
  }"
```

**❌ WRONG - NOT a Real Transfer**:
```bash
# Using payee_name creates a regular transaction, NOT a transfer
"payee_name": "Transfer: To Account B"  # YNAB won't link this
```

#### Getting Transfer Payee IDs

Get all accounts with their transfer_payee_id:
```bash
curl "$YNAB_API/budgets/$BUDGET_ID/accounts" \
  -H "Authorization: Bearer $API_KEY" | \
  jq -r '.data.accounts[] | "\(.name): \(.transfer_payee_id)"'
```

Store these IDs in your personal config (TOOLS.md or local config file) for quick reference.

#### What Happens When Done Correctly

When you use `transfer_payee_id`:
- YNAB creates **two linked transactions** (one in each account)
- The matching transaction appears automatically in the destination account
- Both transactions are marked as transfers (not regular expenses/income)
- Category is automatically set to "Transfer" (no budget impact)
- Deleting one side deletes both

#### Common Transfer Mistakes

1. **Using payee_name** → Creates regular transaction, not a transfer
2. **Manually creating both sides** → Creates duplicates instead of linked pair
3. **Setting a category** → Transfers shouldn't have categories (YNAB ignores it)
4. **Wrong transfer_payee_id** → Transfer goes to wrong account

#### Transfer vs. Regular Transaction

| Transfer (payee_id = transfer_payee_id) | Regular Transaction (payee_name) |
|----------------------------------------|----------------------------------|
| Two linked transactions created        | Single transaction              |
| Automatically categorized as Transfer  | Needs category                  |
| No budget impact                       | Affects budget                  |
| Both sides auto-reconcile              | Manual reconciliation           |

## Common Account IDs Structure

Store account IDs in config (example structure):
```json
{
  "accounts": {
    "primary_checking": "UUID-HERE",
    "savings": "UUID-HERE",
    "cash": "UUID-HERE"
  },
  "default_account": "primary_checking"
}
```

**Never** hardcode account IDs in scripts—use config references.

## Common Operations

### Add Transaction

```bash
YNAB_API="https://api.ynab.com/v1"

curl -X POST "$YNAB_API/budgets/$BUDGET_ID/transactions" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"transaction\": {
      \"account_id\": \"$ACCOUNT_ID\",
      \"date\": \"2026-02-21\",
      \"amount\": -10000,
      \"payee_name\": \"Coffee Shop\",
      \"category_id\": \"$CATEGORY_ID\",
      \"memo\": \"Morning coffee\",
      \"approved\": true
    }
  }"
```

### Create Transfer Between Accounts

```bash
# Step 1: Get destination account's transfer_payee_id
DEST_ACCOUNT_NAME="Savings"
TRANSFER_PAYEE_ID=$(curl -s "$YNAB_API/budgets/$BUDGET_ID/accounts" \
  -H "Authorization: Bearer $API_KEY" | \
  jq -r ".data.accounts[] | select(.name == \"$DEST_ACCOUNT_NAME\") | .transfer_payee_id")

# Step 2: Create transfer transaction
curl -X POST "$YNAB_API/budgets/$BUDGET_ID/transactions" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"transaction\": {
      \"account_id\": \"$SOURCE_ACCOUNT_ID\",
      \"date\": \"2026-02-21\",
      \"amount\": -50000,
      \"payee_id\": \"$TRANSFER_PAYEE_ID\",
      \"memo\": \"Monthly savings transfer\",
      \"approved\": true
    }
  }"

# YNAB will automatically create the matching transaction in the destination account
```

**Important**: Only create ONE transaction - YNAB creates the matching side automatically.

### Search Transactions

```bash
# Get transactions since date
curl "$YNAB_API/budgets/$BUDGET_ID/transactions?since_date=2026-02-01" \
  -H "Authorization: Bearer $API_KEY"

# Filter by payee (client-side with jq)
... | jq '.data.transactions[] | select(.payee_name | contains("Coffee"))'
```

### Get Categories

```bash
curl "$YNAB_API/budgets/$BUDGET_ID/categories" \
  -H "Authorization: Bearer $API_KEY" | \
  jq '.data.category_groups[].categories[] | {id, name}'
```

## Monthly Spending Report

To calculate monthly spending:

1. Get all transactions for the month
2. Filter: `amount < 0` (expenses only)
3. Exclude configured non-discretionary categories (taxes, transfers, etc.)
4. Expand Split transactions into subcategories
5. Sum by category or total

**Tip**: Consider separating small recurring expenses from large one-time purchases for better budget analysis.

## 🛠️ Available Scripts

All scripts are in `/skills/ynab-api/scripts/` and ready to use.

### `setup-automation.sh [--dry-run]`
**⭐ START HERE** - One-command automation setup.

```bash
./setup-automation.sh          # Interactive setup
./setup-automation.sh --dry-run # Preview changes
```

Creates all recommended cron jobs:
- Daily Budget Check (7:15 AM)
- Weekly Spending Review (Monday 8 AM)  
- Mid-Month Goal Check (15th at 9 AM)
- Upcoming Bills Alert (10 AM daily)

**What it does:**
1. Validates YNAB config exists
2. Prompts for your WhatsApp number
3. Creates 4 automation cron jobs
4. Confirms successful setup

**This is the recommended way to get started!**

### `goals-progress.sh [month]`
Shows visual progress bars for all category goals.

```bash
./goals-progress.sh          # Current month
./goals-progress.sh 2026-01  # Specific month
```

**Example output:**
```
📊 PROGRESSI OBIETTIVI - 2026-02-01

Palestra 🏋️♂️:
  ████░░░░░░ 8% (€22/€270) 🟢

Salute ⚕️:
  ████████░░ 43% (€261/€500) 🟡

Mangiare Fuori 🍝:
  ██████████ 119% (€178/€150) 🔴
```

### `scheduled-upcoming.sh [days]`
Lists upcoming scheduled transactions.

```bash
./scheduled-upcoming.sh     # Next 7 days
./scheduled-upcoming.sh 30  # Next 30 days
```

**Example output:**
```
📅 TRANSAZIONI PROGRAMMATE - Prossimi 7 giorni

2026-03-01 💸 Lisa Valent: €-42.18 - Spotify
2026-03-02 💸 Andrea Schiffo: €-84.36 - Spotify lui e moglie
---
TOTALE: €-126.54
```

### `month-comparison.sh [month1] [month2]`
Compares spending between two months.

```bash
./month-comparison.sh                    # Current vs last month
./month-comparison.sh 2026-02 2026-01    # Specific months
```

**Example output:**
```
📊 CONFRONTO SPESE
2026-02-01 vs 2026-01-01

Casa 🏠: €1,241 (era €450) ⚠️ +176%
Mangiare Fuori 🍝: €178 (era €120) ↗️ +48%
Palestra 🏋️♂️: €100 (era €100) = 0%
---
TOTALE 2026-02: €5,298
TOTALE 2026-01: €3,450
Differenza: +€1,848 (+53.6%)
```

### `transfer.sh SOURCE_ACCOUNT DEST_ACCOUNT AMOUNT DATE [MEMO]`
Creates a proper linked transfer between accounts.

```bash
./transfer.sh abc-123 "Savings" 100.50 2026-02-21 "Monthly savings"
```

**Important**: Uses `transfer_payee_id` for real transfers recognized by YNAB.

### `daily-budget-check.sh`
Comprehensive morning budget report (designed for cron).

```bash
./daily-budget-check.sh
```

**Example output:**
```
☀️ BUDGET CHECK MATTUTINO

💰 Age of Money: 141 giorni ✅

📅 Prossime uscite (7gg)
• Domani: Lisa Valent €42.18

⚠️ Alert Budget Superato
• Mangiare Fuori 🍝: €178 / €150 (+€28)

🎯 Obiettivi in ritardo
• Palestra 🏋️♂️: 8% (€22/€270)
```

This script is perfect for automated cron jobs to get daily budget insights.

## Personal Configuration

For personal preferences (merchant mappings, category exclusions, default accounts):

**Option 1**: Add to your workspace `TOOLS.md`:
```markdown
## YNAB Personal Config
- Default account: [account_id]
- Exclude from budget: Category1, Category2
- Merchant mappings: Store → Category
```

**Option 2**: Create local config file (e.g., `~/.config/ynab/rules.json`):
```json
{
  "exclude_categories": ["Taxes", "Transfers"],
  "merchant_map": {
    "Coffee Shop": "category_id_here"
  }
}
```

The skill will check transaction history for consistency—your personal preferences stay private.

## Security Notes

- **Never** commit API keys to version control
- Store `YNAB_API_KEY` in environment or secure config (`~/.config/ynab/config.json` with 600 permissions)
- **Never** log or display full API keys in output

## API Documentation

Official YNAB API docs: https://api.ynab.com

Rate limit: ~200 requests per hour per IP.

## 🤖 Automation Ideas

### Daily Morning Check (Recommended)
Get a comprehensive budget overview every morning at 7:15 AM:
```bash
openclaw cron add --name "Daily Budget Check" \
  --schedule "15 7 * * *" \
  --session isolated \
  --model gemini-flash \
  --delivery announce \
  --task "Run YNAB daily budget check and send via WhatsApp"
```

### Weekly Spending Review
Every Monday morning, compare last week with previous week:
```bash
openclaw cron add --name "Weekly Spending Review" \
  --schedule "0 8 * * 1" \
  --session isolated \
  --model gemini-flash \
  --delivery announce \
  --task "Compare current month vs last month YNAB spending"
```

### Goal Progress Reminder
Mid-month reminder (15th) to check goal progress:
```bash
openclaw cron add --name "Mid-Month Goal Check" \
  --schedule "0 9 15 * *" \
  --session isolated \
  --model gemini-flash \
  --delivery announce \
  --task "Show YNAB goals progress for current month"
```

### Scheduled Transaction Alerts
Get notified 2 days before scheduled payments:
```bash
openclaw cron add --name "Upcoming Bills Alert" \
  --schedule "0 10 * * *" \
  --session isolated \
  --model gemini-flash \
  --delivery announce \
  --task "Show YNAB scheduled transactions for next 2 days"
```

## 💡 Pro Tips

1. **Set realistic goals**: Use YNAB's goal feature for categories you want to track closely
2. **Review Age of Money**: Target 30+ days minimum, 90+ is excellent
3. **Check scheduled transactions weekly**: Avoid surprises from forgotten subscriptions
4. **Use import_id**: When importing from CSV, use unique import_id to avoid duplicates
5. **Transfer payee IDs**: Store these in your personal TOOLS.md for quick reference
6. **Categorize immediately**: Never leave transactions uncategorized
7. **Monthly comparison**: Use month-comparison.sh to spot spending trends

## 🔒 Security Best Practices

- Store API key in config file with permissions `600`
- Never commit `config.json` to version control
- Add to `.gitignore`: `config/ynab.json`, `.config/ynab/`
- Rotate API tokens periodically (every 6-12 months)
- Use read-only tokens when possible (YNAB doesn't support this yet, but request it!)

## 🆘 Troubleshooting

**401 Unauthorized**: API key invalid or expired
- Regenerate token at https://app.ynab.com/settings/developer

**404 Not Found**: Budget ID or transaction ID doesn't exist
- Verify budget ID in YNAB URL or with `/budgets` endpoint

**429 Too Many Requests**: Rate limit exceeded (~200 requests/hour)
- Add delays between bulk operations
- Cache frequently-used data (accounts, categories)

**Transfer not linking**: Using payee_name instead of transfer_payee_id
- See "Transfer Transactions (CRITICAL)" section above

**Common mistakes**:
- Forgetting milliunits (using 10 instead of 10000)
- Wrong date format (use YYYY-MM-DD)
- Missing required fields (account_id, date, amount)
- Using payee_name for transfers (use transfer_payee_id)

## 📚 Resources

- **YNAB API Docs**: https://api.ynab.com
- **Budget templates**: https://www.ynab.com/learn
- **OpenAPI Spec**: https://github.com/ynab/ynab-sdk-ruby/blob/main/open_api_spec.yaml
- **Rate limits**: ~200 requests/hour per IP
- **Support**: https://support.ynab.com

## 🎉 What's Next?

After installation:
1. ✅ Test with `goals-progress.sh`
2. ✅ Set up daily budget check cron
3. ✅ Store transfer_payee_ids in TOOLS.md
4. ✅ Configure personal category exclusions
5. ✅ Enjoy automated budget insights!

**Happy budgeting!** 💰
