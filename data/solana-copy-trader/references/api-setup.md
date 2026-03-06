# Free API Keys Setup

## Helius (Required — Free)
1. Go to https://dev.helius.xyz
2. Sign up with email
3. Copy API key → paste in `.env` as `HELIUS_API_KEY`
4. Free tier: 1000 req/day (enough for learning)
5. RPC URL: `https://mainnet.helius-rpc.com/?api-key=YOUR_KEY`

## Telegram Bot (Optional — Alerts)
1. Message @BotFather on Telegram
2. `/newbot` → follow prompts → copy token
3. Message your bot once
4. Get chat ID: `https://api.telegram.org/bot<TOKEN>/getUpdates`
5. Paste both in `.env`

## Solana Wallet (Optional — Live Trading)
- Use a BURNER wallet — never your main wallet
- Export private key as base58 from Phantom: Settings → Export Private Key
- Paste in `.env` as `PRIVATE_KEY`
- Fund with small amount (0.05 SOL recommended for testing)
