# Workflow: Budget Optimization

The user connected fscl to an existing Actual Budget. Accounts, transactions, and categories already exist, but fscl automation (rules, payee cleanup) hasn't been set up. Your job: audit the current state, clean it up, and build automation.

## Step 1: Audit Current State

Gather the full picture:

```bash
fscl accounts list --json
fscl categories list --json
fscl transactions uncategorized --json
fscl payees stats --extended --json
fscl rules list --json
fscl month status --json
```

Assess and report to the user:
- How many accounts? Are balances reasonable?
- How many categories? Any duplicates or obvious gaps?
- How many uncategorized transactions?
- How many payees? Are there messy bank names?
- Any rules already set up?
- Current budget status — is money allocated?

Present a summary: "Here's what I found in your budget. I have some suggestions to clean things up — want to go through them?"

## Step 2: Category Cleanup

Compare against templates in [budgeting.md](budgeting.md) — don't force a template, but use it to spot gaps.

Look for:
- **Duplicates** (e.g., "Food" and "Foods") → merge: `fscl categories delete <dup-id> --transfer-to <keep-id> --yes`
- **Empty groups** → delete if unused
- **Missing categories** → suggest additions based on transaction patterns
- **Miscategorized income** → ensure income categories have the `--income` flag

Confirm changes with the user before making them.

## Step 3: Payee Cleanup

Use payee stats to find the worst offenders:

```bash
fscl payees stats --extended --json
```

Look for:
- Multiple payees for the same merchant (e.g., "AMZN MKTP US", "AMAZON.COM", "AMZN DIGITAL")
- Ugly bank names that should be human-readable

Rename and merge:

```bash
fscl payees update <id> --name "Amazon"
fscl payees merge <amazon-id> <amzn-mktp-id> <amzn-digital-id>
```

## Step 4: Process Uncategorized Transactions

If `transactions.uncategorized > 0`, work through them:

```bash
# Categorize (payee names are now clean from Step 3)
fscl transactions categorize draft
# Fill in category IDs using _meta context
# Do not create categorize.json manually; edit the generated draft file
fscl transactions categorize apply
```

For large backlogs, use `--limit` to work in batches:

```bash
fscl transactions categorize draft --limit 50
```

## Step 5: Create Rules

After cleaning payees and categorizing, build rules for recurring patterns so future imports auto-categorize.

Use the draft/apply pattern:

```bash
fscl rules draft
# Edit rules.json — add new rules (no id field), update existing (with id)
fscl rules apply
fscl rules run --and-commit
```

For high-volume payees with name variations, create pre-stage rules:

```bash
fscl rules create '{
  "stage": "pre",
  "conditionsOp": "and",
  "conditions": [{"field": "imported_payee", "op": "matches", "value": "AMZN|AMAZON"}],
  "actions": [{"field": "payee", "op": "set", "value": "<amazon-payee-id>"}]
}'
```

See [rules.md](rules.md) for the full schema (conditions, actions, stages).

## Step 6: Review Budget Amounts

Compare actual spending to budgeted amounts:

```bash
fscl month status --compare 3 --json
```

Suggest adjustments for categories that are consistently over or under budget.

If the budget has no amounts set for the current month, offer to set them up using the approach in [workflow-onboarding.md](workflow-onboarding.md) Step 4.

## Step 7: Credit Card Check

If any accounts have negative balances (credit cards), verify the setup:
- **Paying in full monthly?** No special setup needed — purchases use regular expense categories.
- **Carrying debt?** See [credit-cards.md](credit-cards.md) for rollover category + carryover setup.

## What's Next

Once optimization is complete, tell the user:
- "Your budget is cleaned up! I've set up rules so future imports will auto-categorize most transactions."
- "Going forward, import new transactions periodically and I'll handle the rest."
- "At the start of each month, we'll review spending and set the next month's budget."
