# Solana Trading Concepts

## MEV (Maximal Extractable Value)
Bots front-run transactions by paying higher priority fees.
Example: Whale buys token → bot sees it in mempool → bot buys first → price rises → bot sells to whale at higher price.

## Copy Trading
Watch a profitable wallet → when they buy X, you buy X too → when they sell, you sell.
Risk: you're always slightly behind (latency), so you pay higher price.
Reward: ride the same price move as the whale.

## Arbitrage  
Same token, different price on two DEXes.
Buy cheap on Raydium → sell expensive on Orca = risk-free profit.
Reality: bots compete, margins are tiny (0.1-0.5%), need speed + size.

## Jupiter Aggregator
Best swap router on Solana. Finds optimal route across all DEXes.
API: quote-api.jup.ag/v6/quote → get best price
     quote-api.jup.ag/v6/swap → get transaction to execute

## Pump.fun Bonding Curve
New tokens launch on pump.fun with a bonding curve:
- Price increases as more people buy
- Token "graduates" to Raydium at ~$69K market cap
- Before graduation: only trade via pump.fun bonding curve
- After graduation: trade via Jupiter/Raydium like normal token

## Helius WebSocket
Real-time transaction monitoring:
```js
connection.onAccountChange(pubkey, callback)  // watch wallet
```
Fires within 400ms of any transaction.

## Price Impact
How much your trade moves the price.
- Low liquidity token + big trade = high price impact
- >5% impact = bad trade (you're moving the market against yourself)
- >50% impact = rug risk or extremely thin liquidity
