# Locus Heartbeat

*Run this every 30 minutes. You can also check anytime you want!*

Time to check in on your Locus orders and payments.

---

## First: Check for Skill Updates

Check if there's a new version (once a day is plenty):

```bash
curl -s https://paywithlocus.com/skill.json | grep '"version"'
```

Compare with your saved version. If there's a new version, re-fetch the skill files:

```bash
curl -s https://paywithlocus.com/skill.md > ~/.locus/skills/SKILL.md
curl -s https://paywithlocus.com/onboarding.md > ~/.locus/skills/ONBOARDING.md
curl -s https://paywithlocus.com/fiverr.md > ~/.locus/skills/FIVERR.md
curl -s https://paywithlocus.com/heartbeat.md > ~/.locus/skills/HEARTBEAT.md
curl -s https://paywithlocus.com/skill.json > ~/.locus/skills/skill.json
```

Update `lastSkillUpdate` in `~/.config/locus/state.json` so you don't re-check every heartbeat.

---

## Load Memory

Before polling, load your memory file at `~/.config/locus/memory.json`. This tracks the last known state of each order so you can detect what actually changed.

If the file doesn't exist yet, create it:

```json
{
  "orders": {}
}
```

The `orders` object maps order IDs to their last known state:

```json
{
  "orders": {
    "order-uuid-1": { "status": "PENDING_APPROVAL", "deliverables": null },
    "order-uuid-2": { "status": "COMPLETED", "deliverables": ["https://example.com/logo.svg"] }
  }
}
```

---

## Check Active Orders

```bash
curl "https://api.paywithlocus.com/api/fiverr/orders?limit=50" \
  -H "Authorization: Bearer YOUR_LOCUS_API_KEY"
```

Go through each order in the response and **compare against your memory file** to detect changes:

### Diff Logic

For each order in the API response:
1. Look up `orders[id]` in your memory file
2. If the order is **new** (not in memory) or its **status changed**, process it below
3. If nothing changed, skip it — no action needed

### COMPLETED orders (newly completed)

Only report if the order was NOT already `COMPLETED` in your memory. The `deliverables` field has an array of URLs. Report them to your human:

> Your [category] order is complete! Deliverables:
> - [url1]
> - [url2]

### CANCELLED orders (newly cancelled)

Only report if the order was NOT already `CANCELLED` in your memory. Funds were returned to the wallet:

> Order #[id] was cancelled. Funds returned to your wallet.

### Stuck in PENDING_APPROVAL (2+ hours)

If an order has been `PENDING_APPROVAL` for over 2 hours (compare `submitted_at` to now), remind your human:

> Your order for [request] has been waiting for completion for a while. You can check its status at https://app.paywithlocus.com

### DEPOSITING / CREATED (30+ minutes)

These should resolve quickly. If stuck for 30+ minutes, note it but don't alarm your human — it may just be processing.

### Everything else

`APPROVED`, `COMPLETING` — normal in-progress states. No action needed.

---

## Update Memory

After processing all orders, **overwrite** `~/.config/locus/memory.json` with the current state of every order from the API response:

```json
{
  "orders": {
    "order-uuid-1": { "status": "COMPLETED", "deliverables": ["https://example.com/logo.svg"] },
    "order-uuid-3": { "status": "DEPOSITING", "deliverables": null }
  }
}
```

This ensures the next heartbeat can diff against the latest snapshot and only surface real changes.

---

## Do You Need to Order Anything?

Ask yourself:
- Does your human have a pending task that needs freelance work?
- Did a previous order get cancelled that should be re-ordered?
- Is there a recurring need (e.g., weekly blog posts)?

If yes, follow **[FIVERR.md](FIVERR.md)** to place a new order.

---

## When to Tell Your Human

**Do tell them:**
- An order completed (deliverables ready)
- An order was cancelled unexpectedly
- You hit a policy limit (403) trying to place an order
- An order has been stuck in a non-terminal state for a long time

**Don't bother them:**
- Normal in-progress statuses
- Routine heartbeat with no changes
- Orders moving through expected stages

---

## Response Format

If nothing changed:
```
HEARTBEAT_OK — No Locus order updates.
```

If orders completed:
```
Locus: 1 order completed (logo_design). Deliverables saved. 2 orders still in progress.
```

If something needs human attention:
```
Locus: Order for "minimalist logo" has been PENDING_APPROVAL for 3 hours. Please check https://app.paywithlocus.com
```

