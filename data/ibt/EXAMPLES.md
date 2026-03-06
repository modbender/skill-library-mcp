# IBT v2.5 Examples — Before/After

## Example 1: Trivial (Skip)

```
User: what's 2+2?
→ 4
```

## Example 2: Standard (Pulse)

```
User: check my balance
→ Noticing you asked yesterday — full breakdown or just balance?
→ [executes]
```

## Example 3: Human Ambiguity (v2.5)

```
User: I want to get my car washed

❌ Wrong (assumed):
"Walking is faster — it's only 50 meters."

✅ Right (asked first):
"Do you want to wash it today, or were you just going to check pricing?"
```

## Example 4: Complex (Full)

```
User: build me a trading bot

Observe:
│   • Pattern: 3rd trading request this week
│   • Take: Good idea, needs guardrails first
│   • Hunch: Without risk limits, could lose money fast
│   • Suggest: Define max position, stop-loss, paper-trade first?

→ Parse: Build with risk controls
→ Plan: [continues...]
```

## Example 5: Session Realignment (v2.5)

```
User: [returns after 12 hours]

Quick realignment — here's where we left off:
- Working on SIE integration
- Waiting for your API keys
Still accurate? Anything I missed? What's top of mind?
```

## License

MIT
