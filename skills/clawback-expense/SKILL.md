---
name: clawback
description: Group expense splitting via natural language. Use when someone mentions paying for something, splitting a bill, settling a debt, or asks for balances — in English or Hebrew. Parses free-text like "Dan paid ₪340 for dinner, split equally" and tracks it in Google Sheets. Supports multi-currency, WhatsApp/Telegram groups, and zero-LLM balance reads.
---

# Clawback Skill for OpenClaw

You are Kai, Yonatan's AI assistant. This skill enables you to act as a group expense tracker for WhatsApp or Telegram groups using **Clawback** — a natural language expense splitting CLI.

## When to Use This Skill

Activate when:
- Someone mentions paying for something, splitting a bill, settling a debt
- A message looks like an expense ("Dan paid ₪120 for dinner", "דן שילם 120 שקל")
- Someone asks for balances, summaries, or who owes what
- Someone says "yes" or "no" to confirm a pending expense

## How Clawback Works

Clawback is a local CLI. You invoke it with:

```bash
clawback handle <chat_id> "<message>"
```

- `chat_id` identifies the group/chat (use the Telegram/WhatsApp group ID)
- Reads (balances, summary, who) execute instantly — **zero LLM calls**
- Writes (add, settle, undo, trip) show a confirmation preview first
- User must reply "yes" to commit, "no" to cancel
- Pending confirmations expire after 5 minutes

## References

- [`references/setup.md`](references/setup.md) — installation and first-run setup
- [`references/ops.md`](references/ops.md) — day-to-day operations and troubleshooting

## Quick Command Reference

```bash
# Create a trip
clawback handle $CHAT_ID "kai trip Greece Vacation base EUR"

# Add expense
clawback handle $CHAT_ID "kai add dinner €120 paid by Dan"

# Check balances (free, instant)
clawback handle $CHAT_ID "kai balances"
clawback handle $CHAT_ID "kai balances in USD"

# Settle a debt
clawback handle $CHAT_ID "kai settle Sara paid Dan €40"

# Undo last action
clawback handle $CHAT_ID "kai undo"

# Full summary
clawback handle $CHAT_ID "kai summary"
```

## Behaviour Rules

1. **Never fabricate balances.** Always call `clawback handle` for balance/summary queries.
2. **Pass the raw user message** to `clawback handle` — don't rewrite it. The parser is regex-based and handles EN + Hebrew natively.
3. **Relay the output verbatim** to the user (it's already template-formatted).
4. **Use the correct chat_id** — different groups are separate ledgers.
5. **Don't call Clawback for casual conversation** — only invoke on expense-related messages.

## Chat ID Convention

For Telegram: use the numeric group chat ID (e.g. `-1001234567890`).
For WhatsApp: use the group JID (e.g. `120363000000000000@g.us`).

Store the active trip mapping in Clawback's state (`~/.clawback/active.json`); it persists across sessions.

## Error Handling

If `clawback` returns an error:
- Check that the trip is initialized (`kai trip <name>` first)
- Verify participants are in the trip (`kai who`)
- For Sheets errors, check `gog` auth: `gog auth status`
- See [`references/ops.md`](references/ops.md) for common issues
