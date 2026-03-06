# Clawback Operations Reference

## Day-to-Day

### Check active trip for a chat

```bash
cat ~/.clawback/active.json
# {"mygroup": "Greece Vacation", "familytrip": "Beach 2025"}
```

### Switch trips

```bash
clawback handle mygroup "kai trip Beach 2025"
clawback handle mygroup "yes"
```

### List all trips

```bash
clawback trips
```

### Show balances directly (bypasses chat handler)

```bash
clawback balances "Greece Vacation"
```

## Troubleshooting

### "No active trip for this chat"

The chat has no trip set. Create one:
```bash
clawback handle <chat_id> "kai trip My Trip"
clawback handle <chat_id> "yes"
```

### "Unknown participant: <name>"

The person hasn't been added yet. They're auto-added when they first pay or are named in a split. If you need to add manually, add a zero-amount expense with them as payer and cancel it — or just include them in the next expense.

### Pending confirmation expired

Confirmations expire after 5 minutes. Re-send the original expense message.

### Google Sheets not updating

1. Check gog auth: `gog auth status`
2. Verify the env var: `echo $GOG_KEYRING_PASSWORD`
3. Test manually: `gog sheets list`
4. If all else fails, local state is authoritative — Sheets is just a view.

### Undo last action

```bash
clawback handle <chat_id> "kai undo"
clawback handle <chat_id> "yes"
```

Undo is single-step only (no multi-level undo).

## Currency Conversion

FX rates are fetched live from [frankfurter.app](https://www.frankfurter.app) — free, no API key.

```bash
# Show balances in a different currency
clawback handle mygroup "kai balances in USD"
```

Rates are cached for the session. If you need fresh rates, restart the process.

## Oracle Test Suite (dev only)

The oracle suite validates 130 edge cases including:
- Hebrew payer names
- Space-separated thousands (₪1 200)
- SQL injection inputs
- Duplicate deduplication
- Mixed-script messages

```bash
# Requires ANTHROPIC_API_KEY
pytest -m oracle --haiku   # ~11 Haiku batch calls, ~100s, ~$0.01
```

NOT run in default CI. Trigger via GitHub Actions → "Oracle Validation" → Run workflow.

## Backup

```bash
# Backup local state
cp -r ~/.clawback/ ~/.clawback.bak.$(date +%Y%m%d)

# The Google Sheet is also a backup if Sheets sync is enabled
```

## Resetting a Trip

There's no delete command. To reset:
1. Create a new trip with a different name
2. Or manually edit `~/.clawback/trips.json` (it's plain JSON)
