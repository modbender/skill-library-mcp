# Command Cheat Sheet

Common patterns and recipes. For full flag/output details, see [command-reference.md](command-reference.md).

## Conventions

- Always pass `--json` — present output as human-friendly summaries, never raw JSON.
- Amounts: input as decimals (`--amount 45.99`), output in cents (`-4599`).
- Dates: `YYYY-MM-DD`. Months: `YYYY-MM`.
- JSON input: pass inline or use `@filepath` to read from file.
- Deletion: always requires `--yes`. Use `--transfer-to <id>` to reassign children before deleting.
- `find` does case-insensitive substring matching. Multiple terms are OR-matched.
- If a command returns code `not-logged-in`, run `fscl login [server-url] --password <pw>` and retry.

## Entity Resolution

Commands that accept account, category, or category group IDs also accept names. The CLI resolves names to IDs automatically using exact case-insensitive matching. If the name is ambiguous (multiple matches), the command fails with the matching IDs listed.

```bash
# These are equivalent:
fscl transactions list abc-123-def --start 2026-01-01 --end 2026-01-31
fscl transactions list "Checking" --start 2026-01-01 --end 2026-01-31

fscl month set 2026-02 "Groceries" 500.00
fscl categories create "Dining Out" --group "Food"
```

For fuzzy substring searches (multiple results), use `find`:

```bash
fscl accounts find "checking" --json
fscl categories find "groceries" --json
fscl payees find amzn amazon "whole foods" --json
fscl schedules find "rent" --json
```

Use `--columns id,name` to get concise output when you only need IDs.

## Draft/Apply Pattern

Six commands use draft/apply: **categories**, **categorize**, **edit**, **rules**, **month**, **templates**. The cycle is always the same:

```bash
fscl <command> draft [filters]     # Writes JSON to <dataDir>/<budgetId>/drafts/
# Edit the draft file
fscl <command> apply --dry-run     # Preview changes
fscl <command> apply               # Commit changes (deletes draft on success)
```

Never hand-create a new draft JSON file by guessing the `drafts/` path. Always generate it with `fscl <command> draft` first, then edit the generated file.

Draft files include `_meta` fields for context — these are ignored on apply.

Category drafts use two entity types: category-group rows at the top level and category rows inside each group's `categories` array (`[{ id?, name, categories: [{ id?, name }] }]`). Categories do not contain child categories.

## Import Pipeline

The standard sequence after getting bank files:

```bash
# 1. Preview
fscl transactions import <acct-id> <file> --dry-run --report

# 2. Import
fscl transactions import <acct-id> <file> --report

# 3. Auto-categorize with rules
fscl rules run --and-commit

# 4. Handle remaining uncategorized
fscl transactions categorize draft
# Fill in category IDs using _meta context
fscl transactions categorize apply

# 5. Create rules for new recurring payees
fscl rules draft
# Add new rules (rows without id)
fscl rules apply
fscl rules run --and-commit
```

For CSV column mapping, see [import-guide.md](import-guide.md).

## Budget Amounts

```bash
# Set one category
fscl month set 2026-02 <cat-id> 500.00

# Copy all amounts from one month to another
fscl month copy 2026-01 2026-02

# Bulk edit
fscl month draft 2026-02
# Edit amounts in the draft
fscl month apply 2026-02

# Use templates
fscl month templates run 2026-03
```

Budget mutation commands (`month set`, `month apply`, `month copy`, `month templates run`) include `toBudget` in their JSON output — the current To Budget amount for the affected month.

## Rules

```bash
# Create and immediately apply retroactively
fscl rules create '<json>' --run

# Preview what a rule would match (without creating it)
fscl rules preview '<json>'

# Batch create/edit via draft
fscl rules draft → edit → fscl rules apply → fscl rules run --and-commit
```

See [rules.md](rules.md) for JSON schema, stages, and common patterns.

## Payee Cleanup

```bash
# Find messy names
fscl payees stats --extended --json

# Rename
fscl payees update <id> --name "Clean Name"

# Merge duplicates (keeps target, reassigns transactions)
fscl payees merge <keep-id> <dup-id-1> <dup-id-2>
```

## Schedules

```bash
fscl schedules upcoming --days 7 --json     # What's due soon
fscl schedules missed --json                 # What's overdue
fscl schedules summary --json                # Recurring cost overview (monthly/annual totals)
fscl schedules history <id> --json           # Past transactions for a schedule
fscl schedules reviews --due --json          # Schedules needing review
```

## Init Modes

```bash
# Local-only budget
fscl init --non-interactive --mode local --budget-name "My Budget"

# Delete a local budget copy
fscl budgets delete <id> --yes

# Pull existing remote budget
fscl login http://actual.local:5006 --password secret
fscl init --non-interactive --mode remote \
  --server-url http://actual.local:5006 --sync-id <id>

# Create local, then upload to server
fscl init --non-interactive --mode local --budget-name "My Budget"
fscl login http://actual.local:5006 --password secret
fscl budgets push --server-url http://actual.local:5006
```

Interactive `fscl init` asks whether to install the Fiscal skill (`npx skills add fiscal-sh/fscl`) at the end. In non-interactive mode, run that command manually when needed.
If init is run as `npx fscl init`, interactive mode also asks whether to install fscl globally with `npm install -g fscl`.
