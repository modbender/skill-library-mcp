# Setup — Polymarket CLI

Read this when `~/polymarket-cli/` doesn't exist or is empty.

## Your Attitude

You're enabling access to prediction markets — one of the most interesting ways to get calibrated probabilities on real-world events. The user should feel excited about what they can now query and potentially trade.

## Priority Order

### 1. First: Integration (Ask Permission)

Ask how they want this skill to integrate:
- "Would you like this skill to activate whenever prediction markets come up, or only when you ask directly?"
- "I can track specific markets and alert you to changes — interested?"

Only save preferences after they confirm. Save to their main memory so the skill activates appropriately.

### 2. Then: Understand Their Use Case

Figure out what they mainly want:
- **Read-only exploration** — browsing markets, checking odds, tracking events
- **Active trading** — placing orders, managing positions
- **Data analysis** — pulling historical data, tracking price movements
- **Automation** — scripting trades, building bots

Most users start read-only. Don't push wallet setup unless they want to trade.

### 3. Finally: Wallet Setup (Only If Trading)

If they want to trade, guide them to set up their wallet themselves:
1. They run `polymarket wallet create` or `polymarket wallet import KEY` directly
2. Remind them about MATIC for gas on Polygon
3. They run `polymarket approve set` before first trade
4. Emphasize: the agent never handles private keys — wallet setup is done by the user directly

## What Gets Saved

With user permission, store in `~/polymarket-cli/memory.md`:
- How they want the skill to activate (always ask first)
- Main use case (read-only, trading, analysis)
- Markets they asked to track
- Trading preferences if shared

## Feedback After Each Exchange

When they share what they're interested in:
1. Acknowledge their interest
2. Show them a relevant market or price immediately
3. Explain what else they can do

Example:
> User: "I want to track the election odds"
> 
> Good: "Perfect — let me pull up the current election markets. [runs polymarket markets search 'election'] Here are the top ones. The Trump market is at 52¢ right now. Want me to alert you if it moves significantly, or just check when you ask?"
