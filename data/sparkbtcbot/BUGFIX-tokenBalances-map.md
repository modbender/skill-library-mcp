# Bug: `tokenBalances` is a Map, not a plain Object — silent data loss

## Problem

`wallet.getBalance()` returns `{ balance, tokenBalances }` where `tokenBalances` is a JavaScript **`Map`**, not a plain object. This is undocumented in the Spark SDK and the SKILL.md doesn't call it out explicitly.

This matters because when an AI agent (the primary consumer of this skill) works with the balance data, it will naturally reach for standard JS patterns that **silently fail on Maps**:

```javascript
// All of these return {} or [] — SILENT DATA LOSS
JSON.stringify(tokenBalances)           // "{}"
Object.entries(tokenBalances)           // []
Object.keys(tokenBalances)             // []
Object.keys(tokenBalances).length === 0 // true (even when tokens exist!)
```

None of these throw an error. They just return empty results, making it look like the wallet holds no tokens when it actually does.

## How we discovered it

1. User sent BEPSI tokens to the wallet's Spark address
2. Agent checked balance using `wallet.getBalance()`
3. Agent serialized `tokenBalances` with `JSON.stringify()` → showed `{}`
4. Agent reported "No tokens found" — **incorrect**
5. Running the `token-operations.js` example script (which uses `tokenBalances.size` and `for...of`) correctly showed 5,000,000 BEPSI

The wallet had tokens the entire time. The agent just couldn't see them because of the Map vs Object mismatch.

## Why this is especially bad for AI agents

AI agents (the target users of this skill) generate code on the fly. They default to the most common JS patterns — `JSON.stringify`, `Object.entries`, `Object.keys`. All of these work on plain objects but silently produce empty results on Maps. There's no error, no warning, no indication that data was lost.

An agent could:
- Report zero token balance when the user actually holds tokens
- Skip token operations because it thinks the wallet is empty
- Fail to trigger token-based logic (sweeps, transfers, alerts)

## Fix

### 1. Add explicit Map documentation to SKILL.md

In the Quick Example and the `getBalance()` sections, add a clear warning:

```
⚠️ `tokenBalances` is a JavaScript `Map`, not a plain object.
Use `.size`, `for...of`, or `Map` methods. Do NOT use JSON.stringify(),
Object.entries(), or Object.keys() — they silently return empty results.
```

### 2. Add a safe serialization helper to the Quick Example

```javascript
// tokenBalances is a Map — convert to object for JSON/logging
const tokensObj = Object.fromEntries(
  [...tokenBalances].map(([id, info]) => [
    info.tokenMetadata.tokenTicker,
    { balance: info.balance.toString(), decimals: info.tokenMetadata.decimals }
  ])
);
console.log("Tokens:", JSON.stringify(tokensObj));
```

### 3. Update the Quick Example to include token checking

The current Quick Example only shows BTC balance. It should show tokens too, since that's a primary use case.

## Files changed

- `SKILL.md` — Added Map warning, updated Quick Example with token balance check and safe serialization
