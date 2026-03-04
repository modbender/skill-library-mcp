---
name: nummo
description: Nummo connects AI agents to the user's bank accounts via Plaid, enabling financial insights through natural language. More info at nummo.ai.
---

## Commands

### Authentication

**`nummo auth signup <email>`**
Creates a new Nummo account and sends a magic link to the provided email.
Use when the user wants to get started or is not yet authenticated.

**`nummo auth status`**
Checks whether the user is authenticated and shows their email and session expiry.
Use to verify setup before running other commands.

### Accounts

**`nummo accounts connect`**
Starts the bank connection flow and returns a Plaid Link URL.
Share the URL with the user — they must open it in a browser to connect their bank.
Use when the user wants to add a bank account.

**`nummo accounts list`**
Lists all connected bank accounts grouped by institution, with account name and last 4 digits.
Use to show the user what banks are connected, or to verify a connection was successful.

**`nummo accounts txs [--from YYYY-MM-DD] [--to YYYY-MM-DD] [--all]`**
Returns individual transactions with date, merchant, amount, account, and category.
Default range: last 7 days. Use `--all` to fetch all available history.
Amounts: `+` = income, `-` = spending.
Use for: finding specific transactions, merchant lookups, category drill-downs, recent activity.

**`nummo accounts summary [--from YYYY-MM-DD] [--to YYYY-MM-DD]`**
Returns total income and spending, broken down by category and subcategory.
Default range: last 30 days.
Use for: spending overviews, budget questions, monthly recaps, "how much did I spend on X".

### Subscription

**`nummo sub tiers`**
Lists available subscription plans with pricing, billing interval, account limits, and transaction history access.

**`nummo sub me`**
Shows the user's current plan, status, trial end date or next billing date.
Use to check subscription status or when the user asks about their plan.

**`nummo sub checkout <tier>`**
Creates a Stripe checkout session for trial users and returns a payment URL.
Share the URL with the user — they must open it in a browser to complete the purchase.
Valid tiers: `pro_monthly`, `pro_yearly`, `max_monthly`, `max_yearly`.
Use `nummo sub tiers` first if the user is unsure which plan to choose.

**`nummo sub change <tier>`**
Same as checkout but for users who are already subscribed and want to change plans.

**`nummo sub cancel`**
Informs the user how to cancel their subscription.

---

## Guidelines

- Always ask for permission before calling any tool. This skill gives you read access to financial data, and you must get explicit consent from the user.
- If no date range is mentioned, use the command defaults — don't ask the user for dates.
- Use `summary` by default when the user asks broad questions about their finances. - Use `txs` for specific lookups or drill-downs.
- When a command returns a URL (connect, checkout, change), always present it clearly and tell the user to open it in their browser.
