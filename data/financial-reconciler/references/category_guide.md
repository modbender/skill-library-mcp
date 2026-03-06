# Category Guide

## Default Categories

| Category | Description | Example Merchants |
|----------|-------------|-------------------|
| groceries | Grocery stores, supermarkets | Whole Foods, Kroger, Trader Joe's, Costco |
| dining | Restaurants, fast food, coffee, delivery | Starbucks, Chipotle, DoorDash, McDonald's |
| transport | Gas, rideshare, transit, parking, auto | Shell, Uber, Lyft, EZ Pass, Jiffy Lube |
| utilities | Electric, gas, water, internet, phone | Comcast, AT&T, Verizon, PG&E |
| subscriptions | Streaming, software, memberships | Netflix, Spotify, Adobe, Planet Fitness |
| shopping | Retail, online shopping, clothing | Amazon, Target, Best Buy, Nike |
| healthcare | Medical, dental, pharmacy, vision | CVS, Walgreens, doctor visits, insurance |
| entertainment | Movies, events, travel, recreation | AMC, Airbnb, Delta, Ticketmaster |
| income | Salary, deposits, refunds, interest | Payroll, direct deposit, tax refund |
| uncategorized | Unmatched transactions | Anything not matching other categories |

## How Categorization Works

Transactions are matched in priority order:

1. **Custom rules** (confidence 1.0) — User-defined exact matches
2. **Exact keyword** (confidence 0.95) — Description exactly matches a keyword
3. **Partial keyword** (confidence 0.85) — Keyword found within the description (min 3 chars)
4. **Regex pattern** (confidence 0.75) — Description matches a regex pattern
5. **Uncategorized** (confidence 0.0) — No match found

Merchant names are cleaned before matching: bank prefixes like "POS DEBIT", "ACH", "PURCHASE AUTHORIZED ON" are stripped, and trailing dates/reference numbers are removed.

## Customizing Categories

### Add a keyword rule
```bash
python3 scripts/categorize.py add-rule dining "joes pizza" --type keyword
```

### Add a regex rule
```bash
python3 scripts/categorize.py add-rule groceries "(?i)farmers?\s*market" --type regex
```

### Add a custom exact-match rule
```bash
python3 scripts/categorize.py add-rule utilities "MY LOCAL ISP MONTHLY" --type custom
```

### Re-run categorization after adding rules
```bash
python3 scripts/categorize.py run --recategorize
```

## Tips

- After importing transactions, check the uncategorized count
- Add keyword rules for merchants that appear frequently in uncategorized
- Longer keywords match more specifically (prefer "trader joe" over "joe")
- Custom rules always take priority over built-in keywords
- Use `--recategorize` to re-process all transactions with updated rules
