# Evenrealities Order Tracker - Skill Package

Automated tracking of Evenrealities orders with status history and change notifications.

## Files

- `SKILL.md` - Complete skill documentation
- `scripts/tracker.py` - Main tracking script
- `references/evenrealities-orders-example.json` - Configuration template

## Quick Setup

1. **Copy configuration template:**
   ```bash
   cp references/evenrealities-orders-example.json ../memory/evenrealities-orders.json
   ```

2. **Edit with your orders:**
   ```json
   {
     "orders": [
       {"email": "you@example.com", "order_id": "ORD-123456"}
     ]
   }
   ```

3. **Set up daily cron (9 AM):**
   ```bash
   clawdbot cron add \
     --name "Evenrealities order check" \
     --schedule "0 9 * * *" \
     --task "python3 /Users/thibautrey/clawd/skills/evenrealities-tracker/scripts/tracker.py --check"
   ```

4. **Done!** You'll get notified only when order statuses change.

## How It Works

- ✅ Checks orders daily at 9 AM
- ✅ Stores status history
- ✅ Notifies only on changes
- ✅ Uses browser automation (fast-browser-use skill)
- ✅ Fully automated

## Usage

**Check now:**
```bash
python3 scripts/tracker.py --check
```

**Show configuration:**
```bash
python3 scripts/tracker.py --config
```

**Show history:**
```bash
python3 scripts/tracker.py --history
```

## Files Generated

- `memory/evenrealities-orders.json` - Your order list
- `memory/evenrealities-status-history.json` - Status history (auto-generated)

## Next Steps

1. Add your orders to `memory/evenrealities-orders.json`
2. Create the cron job (see SKILL.md)
3. First run: Baseline established (no notification)
4. Subsequent runs: Notified only if status changes

See SKILL.md for complete documentation.
